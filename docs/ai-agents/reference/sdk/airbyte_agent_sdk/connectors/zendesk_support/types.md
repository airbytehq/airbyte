---
id: airbyte_agent_sdk-connectors-zendesk_support-types
title: airbyte_agent_sdk.connectors.zendesk_support.types
---

Module airbyte_agent_sdk.connectors.zendesk_support.types
=========================================================
Type definitions for zendesk-support connector.

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

<a id="ArticleAttachmentsAndCondition"></a>

`ArticleAttachmentsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsAnyCondition]`
    :   The type of the None singleton.

<a id="ArticleAttachmentsAnyCondition"></a>

`ArticleAttachmentsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsAnyValueFilter`
    :   The type of the None singleton.

<a id="ArticleAttachmentsAnyValueFilter"></a>

`ArticleAttachmentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `article_id: Any`
    :   The ID of the article this attachment belongs to

    `content_type: Any`
    :   The MIME type of the attachment

    `content_url: Any`
    :   The URL to download the attachment

    `created_at: Any`
    :   The time the attachment was created

    `file_name: Any`
    :   The name of the attached file

    `id: Any`
    :   The unique ID of the attachment

    `inline: Any`
    :   Whether the attachment is displayed inline

    `size: Any`
    :   The size of the attachment in bytes

    `updated_at: Any`
    :   The time the attachment was last updated

    `url: Any`
    :   The API URL of the attachment

<a id="ArticleAttachmentsContainsCondition"></a>

`ArticleAttachmentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsAnyValueFilter`
    :   The type of the None singleton.

<a id="ArticleAttachmentsDownloadParams"></a>

`ArticleAttachmentsDownloadParams(*args, **kwargs)`
:   Parameters for article_attachments.download operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `article_id: str`
    :   The type of the None singleton.

    `attachment_id: str`
    :   The type of the None singleton.

    `range_header: str`
    :   The type of the None singleton.

<a id="ArticleAttachmentsEqCondition"></a>

`ArticleAttachmentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsSearchFilter`
    :   The type of the None singleton.

<a id="ArticleAttachmentsFuzzyCondition"></a>

`ArticleAttachmentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsStringFilter`
    :   The type of the None singleton.

<a id="ArticleAttachmentsGetParams"></a>

`ArticleAttachmentsGetParams(*args, **kwargs)`
:   Parameters for article_attachments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `article_id: str`
    :   The type of the None singleton.

    `attachment_id: str`
    :   The type of the None singleton.

<a id="ArticleAttachmentsGtCondition"></a>

`ArticleAttachmentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsSearchFilter`
    :   The type of the None singleton.

<a id="ArticleAttachmentsGteCondition"></a>

`ArticleAttachmentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsSearchFilter`
    :   The type of the None singleton.

<a id="ArticleAttachmentsInCondition"></a>

`ArticleAttachmentsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsInFilter`
    :   The type of the None singleton.

<a id="ArticleAttachmentsInFilter"></a>

`ArticleAttachmentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `article_id: list[int]`
    :   The ID of the article this attachment belongs to

    `content_type: list[str]`
    :   The MIME type of the attachment

    `content_url: list[str]`
    :   The URL to download the attachment

    `created_at: list[str]`
    :   The time the attachment was created

    `file_name: list[str]`
    :   The name of the attached file

    `id: list[int]`
    :   The unique ID of the attachment

    `inline: list[bool]`
    :   Whether the attachment is displayed inline

    `size: list[int]`
    :   The size of the attachment in bytes

    `updated_at: list[str]`
    :   The time the attachment was last updated

    `url: list[str]`
    :   The API URL of the attachment

<a id="ArticleAttachmentsKeywordCondition"></a>

`ArticleAttachmentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsStringFilter`
    :   The type of the None singleton.

<a id="ArticleAttachmentsLikeCondition"></a>

`ArticleAttachmentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsStringFilter`
    :   The type of the None singleton.

<a id="ArticleAttachmentsListParams"></a>

`ArticleAttachmentsListParams(*args, **kwargs)`
:   Parameters for article_attachments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `article_id: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="ArticleAttachmentsLtCondition"></a>

`ArticleAttachmentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsSearchFilter`
    :   The type of the None singleton.

<a id="ArticleAttachmentsLteCondition"></a>

`ArticleAttachmentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsSearchFilter`
    :   The type of the None singleton.

<a id="ArticleAttachmentsNeqCondition"></a>

`ArticleAttachmentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsSearchFilter`
    :   The type of the None singleton.

<a id="ArticleAttachmentsNotCondition"></a>

`ArticleAttachmentsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsAnyCondition`
    :   The type of the None singleton.

<a id="ArticleAttachmentsOrCondition"></a>

`ArticleAttachmentsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsAnyCondition]`
    :   The type of the None singleton.

<a id="ArticleAttachmentsSearchFilter"></a>

`ArticleAttachmentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering article_attachments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `article_id: int | None`
    :   The ID of the article this attachment belongs to

    `content_type: str | None`
    :   The MIME type of the attachment

    `content_url: str | None`
    :   The URL to download the attachment

    `created_at: str | None`
    :   The time the attachment was created

    `file_name: str | None`
    :   The name of the attached file

    `id: int | None`
    :   The unique ID of the attachment

    `inline: bool | None`
    :   Whether the attachment is displayed inline

    `size: int | None`
    :   The size of the attachment in bytes

    `updated_at: str | None`
    :   The time the attachment was last updated

    `url: str | None`
    :   The API URL of the attachment

<a id="ArticleAttachmentsSearchQuery"></a>

`ArticleAttachmentsSearchQuery(*args, **kwargs)`
:   Search query for article_attachments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.ArticleAttachmentsSortFilter]`
    :   The type of the None singleton.

<a id="ArticleAttachmentsSortFilter"></a>

`ArticleAttachmentsSortFilter(*args, **kwargs)`
:   Available fields for sorting article_attachments search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `article_id: Literal['asc', 'desc']`
    :   The ID of the article this attachment belongs to

    `content_type: Literal['asc', 'desc']`
    :   The MIME type of the attachment

    `content_url: Literal['asc', 'desc']`
    :   The URL to download the attachment

    `created_at: Literal['asc', 'desc']`
    :   The time the attachment was created

    `file_name: Literal['asc', 'desc']`
    :   The name of the attached file

    `id: Literal['asc', 'desc']`
    :   The unique ID of the attachment

    `inline: Literal['asc', 'desc']`
    :   Whether the attachment is displayed inline

    `size: Literal['asc', 'desc']`
    :   The size of the attachment in bytes

    `updated_at: Literal['asc', 'desc']`
    :   The time the attachment was last updated

    `url: Literal['asc', 'desc']`
    :   The API URL of the attachment

<a id="ArticleAttachmentsStringFilter"></a>

`ArticleAttachmentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `article_id: str`
    :   The ID of the article this attachment belongs to

    `content_type: str`
    :   The MIME type of the attachment

    `content_url: str`
    :   The URL to download the attachment

    `created_at: str`
    :   The time the attachment was created

    `file_name: str`
    :   The name of the attached file

    `id: str`
    :   The unique ID of the attachment

    `inline: str`
    :   Whether the attachment is displayed inline

    `size: str`
    :   The size of the attachment in bytes

    `updated_at: str`
    :   The time the attachment was last updated

    `url: str`
    :   The API URL of the attachment

<a id="ArticlesAndCondition"></a>

`ArticlesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesAnyCondition]`
    :   The type of the None singleton.

<a id="ArticlesAnyCondition"></a>

`ArticlesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesAnyValueFilter`
    :   The type of the None singleton.

<a id="ArticlesAnyValueFilter"></a>

`ArticlesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: Any`
    :   The ID of the user who created the article

    `body: Any`
    :   The body content of the article (HTML)

    `created_at: Any`
    :   The time the article was created

    `draft: Any`
    :   Whether the article is a draft

    `html_url: Any`
    :   The public URL of the article

    `id: Any`
    :   The unique ID of the article

    `label_names: Any`
    :   List of label names associated with the article

    `locale: Any`
    :   The locale of the article

    `position: Any`
    :   Position of the article in the section

    `promoted: Any`
    :   Whether the article is promoted

    `section_id: Any`
    :   The ID of the section the article belongs to

    `title: Any`
    :   The title of the article

    `updated_at: Any`
    :   The time the article was last updated

    `url: Any`
    :   The API URL of the article

    `vote_count: Any`
    :   Number of votes

    `vote_sum: Any`
    :   Sum of upvotes and downvotes

<a id="ArticlesContainsCondition"></a>

`ArticlesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesAnyValueFilter`
    :   The type of the None singleton.

<a id="ArticlesEqCondition"></a>

`ArticlesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesSearchFilter`
    :   The type of the None singleton.

<a id="ArticlesFuzzyCondition"></a>

`ArticlesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesStringFilter`
    :   The type of the None singleton.

<a id="ArticlesGetParams"></a>

`ArticlesGetParams(*args, **kwargs)`
:   Parameters for articles.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ArticlesGtCondition"></a>

`ArticlesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesSearchFilter`
    :   The type of the None singleton.

<a id="ArticlesGteCondition"></a>

`ArticlesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesSearchFilter`
    :   The type of the None singleton.

<a id="ArticlesInCondition"></a>

`ArticlesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesInFilter`
    :   The type of the None singleton.

<a id="ArticlesInFilter"></a>

`ArticlesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: list[int]`
    :   The ID of the user who created the article

    `body: list[str]`
    :   The body content of the article (HTML)

    `created_at: list[str]`
    :   The time the article was created

    `draft: list[bool]`
    :   Whether the article is a draft

    `html_url: list[str]`
    :   The public URL of the article

    `id: list[int]`
    :   The unique ID of the article

    `label_names: list[list[typing.Any]]`
    :   List of label names associated with the article

    `locale: list[str]`
    :   The locale of the article

    `position: list[int]`
    :   Position of the article in the section

    `promoted: list[bool]`
    :   Whether the article is promoted

    `section_id: list[int]`
    :   The ID of the section the article belongs to

    `title: list[str]`
    :   The title of the article

    `updated_at: list[str]`
    :   The time the article was last updated

    `url: list[str]`
    :   The API URL of the article

    `vote_count: list[int]`
    :   Number of votes

    `vote_sum: list[int]`
    :   Sum of upvotes and downvotes

<a id="ArticlesKeywordCondition"></a>

`ArticlesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesStringFilter`
    :   The type of the None singleton.

<a id="ArticlesLikeCondition"></a>

`ArticlesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesStringFilter`
    :   The type of the None singleton.

<a id="ArticlesListParams"></a>

`ArticlesListParams(*args, **kwargs)`
:   Parameters for articles.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

<a id="ArticlesLtCondition"></a>

`ArticlesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesSearchFilter`
    :   The type of the None singleton.

<a id="ArticlesLteCondition"></a>

`ArticlesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesSearchFilter`
    :   The type of the None singleton.

<a id="ArticlesNeqCondition"></a>

`ArticlesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesSearchFilter`
    :   The type of the None singleton.

<a id="ArticlesNotCondition"></a>

`ArticlesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesAnyCondition`
    :   The type of the None singleton.

<a id="ArticlesOrCondition"></a>

`ArticlesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesAnyCondition]`
    :   The type of the None singleton.

<a id="ArticlesSearchFilter"></a>

`ArticlesSearchFilter(*args, **kwargs)`
:   Available fields for filtering articles search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: int | None`
    :   The ID of the user who created the article

    `body: str | None`
    :   The body content of the article (HTML)

    `created_at: str | None`
    :   The time the article was created

    `draft: bool | None`
    :   Whether the article is a draft

    `html_url: str | None`
    :   The public URL of the article

    `id: int | None`
    :   The unique ID of the article

    `label_names: list[typing.Any] | None`
    :   List of label names associated with the article

    `locale: str | None`
    :   The locale of the article

    `position: int | None`
    :   Position of the article in the section

    `promoted: bool | None`
    :   Whether the article is promoted

    `section_id: int | None`
    :   The ID of the section the article belongs to

    `title: str | None`
    :   The title of the article

    `updated_at: str | None`
    :   The time the article was last updated

    `url: str | None`
    :   The API URL of the article

    `vote_count: int | None`
    :   Number of votes

    `vote_sum: int | None`
    :   Sum of upvotes and downvotes

<a id="ArticlesSearchQuery"></a>

`ArticlesSearchQuery(*args, **kwargs)`
:   Search query for articles entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.ArticlesSortFilter]`
    :   The type of the None singleton.

<a id="ArticlesSortFilter"></a>

`ArticlesSortFilter(*args, **kwargs)`
:   Available fields for sorting articles search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: Literal['asc', 'desc']`
    :   The ID of the user who created the article

    `body: Literal['asc', 'desc']`
    :   The body content of the article (HTML)

    `created_at: Literal['asc', 'desc']`
    :   The time the article was created

    `draft: Literal['asc', 'desc']`
    :   Whether the article is a draft

    `html_url: Literal['asc', 'desc']`
    :   The public URL of the article

    `id: Literal['asc', 'desc']`
    :   The unique ID of the article

    `label_names: Literal['asc', 'desc']`
    :   List of label names associated with the article

    `locale: Literal['asc', 'desc']`
    :   The locale of the article

    `position: Literal['asc', 'desc']`
    :   Position of the article in the section

    `promoted: Literal['asc', 'desc']`
    :   Whether the article is promoted

    `section_id: Literal['asc', 'desc']`
    :   The ID of the section the article belongs to

    `title: Literal['asc', 'desc']`
    :   The title of the article

    `updated_at: Literal['asc', 'desc']`
    :   The time the article was last updated

    `url: Literal['asc', 'desc']`
    :   The API URL of the article

    `vote_count: Literal['asc', 'desc']`
    :   Number of votes

    `vote_sum: Literal['asc', 'desc']`
    :   Sum of upvotes and downvotes

<a id="ArticlesStringFilter"></a>

`ArticlesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: str`
    :   The ID of the user who created the article

    `body: str`
    :   The body content of the article (HTML)

    `created_at: str`
    :   The time the article was created

    `draft: str`
    :   Whether the article is a draft

    `html_url: str`
    :   The public URL of the article

    `id: str`
    :   The unique ID of the article

    `label_names: str`
    :   List of label names associated with the article

    `locale: str`
    :   The locale of the article

    `position: str`
    :   Position of the article in the section

    `promoted: str`
    :   Whether the article is promoted

    `section_id: str`
    :   The ID of the section the article belongs to

    `title: str`
    :   The title of the article

    `updated_at: str`
    :   The time the article was last updated

    `url: str`
    :   The API URL of the article

    `vote_count: str`
    :   Number of votes

    `vote_sum: str`
    :   Sum of upvotes and downvotes

<a id="AttachmentsDownloadParams"></a>

`AttachmentsDownloadParams(*args, **kwargs)`
:   Parameters for attachments.download operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachment_id: str`
    :   The type of the None singleton.

    `range_header: str`
    :   The type of the None singleton.

<a id="AttachmentsGetParams"></a>

`AttachmentsGetParams(*args, **kwargs)`
:   Parameters for attachments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachment_id: str`
    :   The type of the None singleton.

<a id="AutomationsAndCondition"></a>

`AutomationsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsAnyCondition]`
    :   The type of the None singleton.

<a id="AutomationsAnyCondition"></a>

`AutomationsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsAnyValueFilter`
    :   The type of the None singleton.

<a id="AutomationsAnyValueFilter"></a>

`AutomationsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: Any`
    :   An array of actions

    `active: Any`
    :   Whether the automation is active

    `conditions: Any`
    :   An object that describes the conditions under which the automation will execute

    `created_at: Any`
    :   The time the automation was created

    `id: Any`
    :   Automatically assigned when created

    `position: Any`
    :   The position of the automation

    `raw_title: Any`
    :   The dynamic content placeholder for title

    `title: Any`
    :   The title of the automation

    `updated_at: Any`
    :   The time the automation was last updated

<a id="AutomationsContainsCondition"></a>

`AutomationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsAnyValueFilter`
    :   The type of the None singleton.

<a id="AutomationsEqCondition"></a>

`AutomationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsSearchFilter`
    :   The type of the None singleton.

<a id="AutomationsFuzzyCondition"></a>

`AutomationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsStringFilter`
    :   The type of the None singleton.

<a id="AutomationsGetParams"></a>

`AutomationsGetParams(*args, **kwargs)`
:   Parameters for automations.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `automation_id: str`
    :   The type of the None singleton.

<a id="AutomationsGtCondition"></a>

`AutomationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsSearchFilter`
    :   The type of the None singleton.

<a id="AutomationsGteCondition"></a>

`AutomationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsSearchFilter`
    :   The type of the None singleton.

<a id="AutomationsInCondition"></a>

`AutomationsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsInFilter`
    :   The type of the None singleton.

<a id="AutomationsInFilter"></a>

`AutomationsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: list[list[typing.Any]]`
    :   An array of actions

    `active: list[bool]`
    :   Whether the automation is active

    `conditions: list[dict[str, typing.Any]]`
    :   An object that describes the conditions under which the automation will execute

    `created_at: list[str]`
    :   The time the automation was created

    `id: list[int]`
    :   Automatically assigned when created

    `position: list[int]`
    :   The position of the automation

    `raw_title: list[str]`
    :   The dynamic content placeholder for title

    `title: list[str]`
    :   The title of the automation

    `updated_at: list[str]`
    :   The time the automation was last updated

<a id="AutomationsKeywordCondition"></a>

`AutomationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsStringFilter`
    :   The type of the None singleton.

<a id="AutomationsLikeCondition"></a>

`AutomationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsStringFilter`
    :   The type of the None singleton.

<a id="AutomationsListParams"></a>

`AutomationsListParams(*args, **kwargs)`
:   Parameters for automations.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: bool`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

<a id="AutomationsLtCondition"></a>

`AutomationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsSearchFilter`
    :   The type of the None singleton.

<a id="AutomationsLteCondition"></a>

`AutomationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsSearchFilter`
    :   The type of the None singleton.

<a id="AutomationsNeqCondition"></a>

`AutomationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsSearchFilter`
    :   The type of the None singleton.

<a id="AutomationsNotCondition"></a>

`AutomationsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsAnyCondition`
    :   The type of the None singleton.

<a id="AutomationsOrCondition"></a>

`AutomationsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsAnyCondition]`
    :   The type of the None singleton.

<a id="AutomationsSearchFilter"></a>

`AutomationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering automations search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: list[typing.Any] | None`
    :   An array of actions

    `active: bool | None`
    :   Whether the automation is active

    `conditions: dict[str, typing.Any] | None`
    :   An object that describes the conditions under which the automation will execute

    `created_at: str | None`
    :   The time the automation was created

    `id: int | None`
    :   Automatically assigned when created

    `position: int | None`
    :   The position of the automation

    `raw_title: str | None`
    :   The dynamic content placeholder for title

    `title: str | None`
    :   The title of the automation

    `updated_at: str | None`
    :   The time the automation was last updated

<a id="AutomationsSearchQuery"></a>

`AutomationsSearchQuery(*args, **kwargs)`
:   Search query for automations entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.AutomationsSortFilter]`
    :   The type of the None singleton.

<a id="AutomationsSortFilter"></a>

`AutomationsSortFilter(*args, **kwargs)`
:   Available fields for sorting automations search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: Literal['asc', 'desc']`
    :   An array of actions

    `active: Literal['asc', 'desc']`
    :   Whether the automation is active

    `conditions: Literal['asc', 'desc']`
    :   An object that describes the conditions under which the automation will execute

    `created_at: Literal['asc', 'desc']`
    :   The time the automation was created

    `id: Literal['asc', 'desc']`
    :   Automatically assigned when created

    `position: Literal['asc', 'desc']`
    :   The position of the automation

    `raw_title: Literal['asc', 'desc']`
    :   The dynamic content placeholder for title

    `title: Literal['asc', 'desc']`
    :   The title of the automation

    `updated_at: Literal['asc', 'desc']`
    :   The time the automation was last updated

<a id="AutomationsStringFilter"></a>

`AutomationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: str`
    :   An array of actions

    `active: str`
    :   Whether the automation is active

    `conditions: str`
    :   An object that describes the conditions under which the automation will execute

    `created_at: str`
    :   The time the automation was created

    `id: str`
    :   Automatically assigned when created

    `position: str`
    :   The position of the automation

    `raw_title: str`
    :   The dynamic content placeholder for title

    `title: str`
    :   The title of the automation

    `updated_at: str`
    :   The time the automation was last updated

<a id="BrandsAndCondition"></a>

`BrandsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.BrandsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsAnyCondition]`
    :   The type of the None singleton.

<a id="BrandsAnyCondition"></a>

`BrandsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsAnyValueFilter`
    :   The type of the None singleton.

<a id="BrandsAnyValueFilter"></a>

`BrandsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Any`
    :   Indicates whether the brand is set as active

    `brand_url: Any`
    :   The public URL of the brand

    `created_at: Any`
    :   Timestamp when the brand was created

    `default: Any`
    :   Indicates whether the brand is the default brand for tickets generated from non-branded channels

    `has_help_center: Any`
    :   Indicates whether the brand has a Help Center enabled

    `help_center_state: Any`
    :   The state of the Help Center, with allowed values of enabled, disabled, or restricted

    `host_mapping: Any`
    :   The host mapping configuration for the brand, visible only to administrators

    `id: Any`
    :   Unique identifier automatically assigned when the brand is created

    `is_deleted: Any`
    :   Indicates whether the brand has been deleted

    `logo: Any`
    :   Brand logo image file represented as an Attachment object

    `name: Any`
    :   The name of the brand

    `signature_template: Any`
    :   The signature template used for the brand

    `subdomain: Any`
    :   The subdomain associated with the brand

    `ticket_form_ids: Any`
    :   Array of ticket form IDs that are available for use by this brand

    `updated_at: Any`
    :   Timestamp when the brand was last updated

    `url: Any`
    :   The API URL for accessing this brand resource

<a id="BrandsContainsCondition"></a>

`BrandsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsAnyValueFilter`
    :   The type of the None singleton.

<a id="BrandsEqCondition"></a>

`BrandsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsSearchFilter`
    :   The type of the None singleton.

<a id="BrandsFuzzyCondition"></a>

`BrandsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsStringFilter`
    :   The type of the None singleton.

<a id="BrandsGetParams"></a>

`BrandsGetParams(*args, **kwargs)`
:   Parameters for brands.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `brand_id: str`
    :   The type of the None singleton.

<a id="BrandsGtCondition"></a>

`BrandsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsSearchFilter`
    :   The type of the None singleton.

<a id="BrandsGteCondition"></a>

`BrandsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsSearchFilter`
    :   The type of the None singleton.

<a id="BrandsInCondition"></a>

`BrandsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsInFilter`
    :   The type of the None singleton.

<a id="BrandsInFilter"></a>

`BrandsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: list[bool]`
    :   Indicates whether the brand is set as active

    `brand_url: list[str]`
    :   The public URL of the brand

    `created_at: list[str]`
    :   Timestamp when the brand was created

    `default: list[bool]`
    :   Indicates whether the brand is the default brand for tickets generated from non-branded channels

    `has_help_center: list[bool]`
    :   Indicates whether the brand has a Help Center enabled

    `help_center_state: list[str]`
    :   The state of the Help Center, with allowed values of enabled, disabled, or restricted

    `host_mapping: list[str]`
    :   The host mapping configuration for the brand, visible only to administrators

    `id: list[int]`
    :   Unique identifier automatically assigned when the brand is created

    `is_deleted: list[bool]`
    :   Indicates whether the brand has been deleted

    `logo: list[str]`
    :   Brand logo image file represented as an Attachment object

    `name: list[str]`
    :   The name of the brand

    `signature_template: list[str]`
    :   The signature template used for the brand

    `subdomain: list[str]`
    :   The subdomain associated with the brand

    `ticket_form_ids: list[list[typing.Any]]`
    :   Array of ticket form IDs that are available for use by this brand

    `updated_at: list[str]`
    :   Timestamp when the brand was last updated

    `url: list[str]`
    :   The API URL for accessing this brand resource

<a id="BrandsKeywordCondition"></a>

`BrandsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsStringFilter`
    :   The type of the None singleton.

<a id="BrandsLikeCondition"></a>

`BrandsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsStringFilter`
    :   The type of the None singleton.

<a id="BrandsListParams"></a>

`BrandsListParams(*args, **kwargs)`
:   Parameters for brands.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="BrandsLtCondition"></a>

`BrandsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsSearchFilter`
    :   The type of the None singleton.

<a id="BrandsLteCondition"></a>

`BrandsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsSearchFilter`
    :   The type of the None singleton.

<a id="BrandsNeqCondition"></a>

`BrandsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsSearchFilter`
    :   The type of the None singleton.

<a id="BrandsNotCondition"></a>

`BrandsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsAnyCondition`
    :   The type of the None singleton.

<a id="BrandsOrCondition"></a>

`BrandsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.BrandsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsAnyCondition]`
    :   The type of the None singleton.

<a id="BrandsSearchFilter"></a>

`BrandsSearchFilter(*args, **kwargs)`
:   Available fields for filtering brands search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: bool | None`
    :   Indicates whether the brand is set as active

    `brand_url: str | None`
    :   The public URL of the brand

    `created_at: str | None`
    :   Timestamp when the brand was created

    `default: bool | None`
    :   Indicates whether the brand is the default brand for tickets generated from non-branded channels

    `has_help_center: bool | None`
    :   Indicates whether the brand has a Help Center enabled

    `help_center_state: str | None`
    :   The state of the Help Center, with allowed values of enabled, disabled, or restricted

    `host_mapping: str | None`
    :   The host mapping configuration for the brand, visible only to administrators

    `id: int | None`
    :   Unique identifier automatically assigned when the brand is created

    `is_deleted: bool | None`
    :   Indicates whether the brand has been deleted

    `logo: str | None`
    :   Brand logo image file represented as an Attachment object

    `name: str | None`
    :   The name of the brand

    `signature_template: str | None`
    :   The signature template used for the brand

    `subdomain: str | None`
    :   The subdomain associated with the brand

    `ticket_form_ids: list[typing.Any] | None`
    :   Array of ticket form IDs that are available for use by this brand

    `updated_at: str | None`
    :   Timestamp when the brand was last updated

    `url: str | None`
    :   The API URL for accessing this brand resource

<a id="BrandsSearchQuery"></a>

`BrandsSearchQuery(*args, **kwargs)`
:   Search query for brands entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.BrandsSortFilter]`
    :   The type of the None singleton.

<a id="BrandsSortFilter"></a>

`BrandsSortFilter(*args, **kwargs)`
:   Available fields for sorting brands search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Literal['asc', 'desc']`
    :   Indicates whether the brand is set as active

    `brand_url: Literal['asc', 'desc']`
    :   The public URL of the brand

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the brand was created

    `default: Literal['asc', 'desc']`
    :   Indicates whether the brand is the default brand for tickets generated from non-branded channels

    `has_help_center: Literal['asc', 'desc']`
    :   Indicates whether the brand has a Help Center enabled

    `help_center_state: Literal['asc', 'desc']`
    :   The state of the Help Center, with allowed values of enabled, disabled, or restricted

    `host_mapping: Literal['asc', 'desc']`
    :   The host mapping configuration for the brand, visible only to administrators

    `id: Literal['asc', 'desc']`
    :   Unique identifier automatically assigned when the brand is created

    `is_deleted: Literal['asc', 'desc']`
    :   Indicates whether the brand has been deleted

    `logo: Literal['asc', 'desc']`
    :   Brand logo image file represented as an Attachment object

    `name: Literal['asc', 'desc']`
    :   The name of the brand

    `signature_template: Literal['asc', 'desc']`
    :   The signature template used for the brand

    `subdomain: Literal['asc', 'desc']`
    :   The subdomain associated with the brand

    `ticket_form_ids: Literal['asc', 'desc']`
    :   Array of ticket form IDs that are available for use by this brand

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the brand was last updated

    `url: Literal['asc', 'desc']`
    :   The API URL for accessing this brand resource

<a id="BrandsStringFilter"></a>

`BrandsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: str`
    :   Indicates whether the brand is set as active

    `brand_url: str`
    :   The public URL of the brand

    `created_at: str`
    :   Timestamp when the brand was created

    `default: str`
    :   Indicates whether the brand is the default brand for tickets generated from non-branded channels

    `has_help_center: str`
    :   Indicates whether the brand has a Help Center enabled

    `help_center_state: str`
    :   The state of the Help Center, with allowed values of enabled, disabled, or restricted

    `host_mapping: str`
    :   The host mapping configuration for the brand, visible only to administrators

    `id: str`
    :   Unique identifier automatically assigned when the brand is created

    `is_deleted: str`
    :   Indicates whether the brand has been deleted

    `logo: str`
    :   Brand logo image file represented as an Attachment object

    `name: str`
    :   The name of the brand

    `signature_template: str`
    :   The signature template used for the brand

    `subdomain: str`
    :   The subdomain associated with the brand

    `ticket_form_ids: str`
    :   Array of ticket form IDs that are available for use by this brand

    `updated_at: str`
    :   Timestamp when the brand was last updated

    `url: str`
    :   The API URL for accessing this brand resource

<a id="DeletedTicketsAndCondition"></a>

`DeletedTicketsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsAnyCondition]`
    :   The type of the None singleton.

<a id="DeletedTicketsAnyCondition"></a>

`DeletedTicketsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsAnyValueFilter`
    :   The type of the None singleton.

<a id="DeletedTicketsAnyValueFilter"></a>

`DeletedTicketsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actor: Any`
    :   The user who performed the deletion action

    `deleted_at: Any`
    :   The timestamp when the ticket was deleted

    `description: Any`
    :   Additional details or comments about the deleted ticket

    `id: Any`
    :   The unique identifier of the deleted ticket

    `previous_state: Any`
    :   The state of the ticket before it was deleted

    `subject: Any`
    :   The subject or title of the deleted ticket

<a id="DeletedTicketsContainsCondition"></a>

`DeletedTicketsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsAnyValueFilter`
    :   The type of the None singleton.

<a id="DeletedTicketsEqCondition"></a>

`DeletedTicketsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsSearchFilter`
    :   The type of the None singleton.

<a id="DeletedTicketsFuzzyCondition"></a>

`DeletedTicketsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsStringFilter`
    :   The type of the None singleton.

<a id="DeletedTicketsGtCondition"></a>

`DeletedTicketsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsSearchFilter`
    :   The type of the None singleton.

<a id="DeletedTicketsGteCondition"></a>

`DeletedTicketsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsSearchFilter`
    :   The type of the None singleton.

<a id="DeletedTicketsInCondition"></a>

`DeletedTicketsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsInFilter`
    :   The type of the None singleton.

<a id="DeletedTicketsInFilter"></a>

`DeletedTicketsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actor: list[dict[str, typing.Any]]`
    :   The user who performed the deletion action

    `deleted_at: list[str]`
    :   The timestamp when the ticket was deleted

    `description: list[str]`
    :   Additional details or comments about the deleted ticket

    `id: list[int]`
    :   The unique identifier of the deleted ticket

    `previous_state: list[str]`
    :   The state of the ticket before it was deleted

    `subject: list[str]`
    :   The subject or title of the deleted ticket

<a id="DeletedTicketsKeywordCondition"></a>

`DeletedTicketsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsStringFilter`
    :   The type of the None singleton.

<a id="DeletedTicketsLikeCondition"></a>

`DeletedTicketsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsStringFilter`
    :   The type of the None singleton.

<a id="DeletedTicketsListParams"></a>

`DeletedTicketsListParams(*args, **kwargs)`
:   Parameters for deleted_tickets.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

<a id="DeletedTicketsLtCondition"></a>

`DeletedTicketsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsSearchFilter`
    :   The type of the None singleton.

<a id="DeletedTicketsLteCondition"></a>

`DeletedTicketsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsSearchFilter`
    :   The type of the None singleton.

<a id="DeletedTicketsNeqCondition"></a>

`DeletedTicketsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsSearchFilter`
    :   The type of the None singleton.

<a id="DeletedTicketsNotCondition"></a>

`DeletedTicketsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsAnyCondition`
    :   The type of the None singleton.

<a id="DeletedTicketsOrCondition"></a>

`DeletedTicketsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsAnyCondition]`
    :   The type of the None singleton.

<a id="DeletedTicketsSearchFilter"></a>

`DeletedTicketsSearchFilter(*args, **kwargs)`
:   Available fields for filtering deleted_tickets search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actor: dict[str, typing.Any] | None`
    :   The user who performed the deletion action

    `deleted_at: str | None`
    :   The timestamp when the ticket was deleted

    `description: str | None`
    :   Additional details or comments about the deleted ticket

    `id: int | None`
    :   The unique identifier of the deleted ticket

    `previous_state: str | None`
    :   The state of the ticket before it was deleted

    `subject: str | None`
    :   The subject or title of the deleted ticket

<a id="DeletedTicketsSearchQuery"></a>

`DeletedTicketsSearchQuery(*args, **kwargs)`
:   Search query for deleted_tickets entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsSortFilter]`
    :   The type of the None singleton.

<a id="DeletedTicketsSortFilter"></a>

`DeletedTicketsSortFilter(*args, **kwargs)`
:   Available fields for sorting deleted_tickets search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actor: Literal['asc', 'desc']`
    :   The user who performed the deletion action

    `deleted_at: Literal['asc', 'desc']`
    :   The timestamp when the ticket was deleted

    `description: Literal['asc', 'desc']`
    :   Additional details or comments about the deleted ticket

    `id: Literal['asc', 'desc']`
    :   The unique identifier of the deleted ticket

    `previous_state: Literal['asc', 'desc']`
    :   The state of the ticket before it was deleted

    `subject: Literal['asc', 'desc']`
    :   The subject or title of the deleted ticket

<a id="DeletedTicketsStringFilter"></a>

`DeletedTicketsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actor: str`
    :   The user who performed the deletion action

    `deleted_at: str`
    :   The timestamp when the ticket was deleted

    `description: str`
    :   Additional details or comments about the deleted ticket

    `id: str`
    :   The unique identifier of the deleted ticket

    `previous_state: str`
    :   The state of the ticket before it was deleted

    `subject: str`
    :   The subject or title of the deleted ticket

<a id="GroupMembershipsAndCondition"></a>

`GroupMembershipsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsAnyCondition]`
    :   The type of the None singleton.

<a id="GroupMembershipsAnyCondition"></a>

`GroupMembershipsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsAnyValueFilter`
    :   The type of the None singleton.

<a id="GroupMembershipsAnyValueFilter"></a>

`GroupMembershipsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   When the group membership was created

    `default: Any`
    :   If true, tickets assigned directly to the agent will assume this membership's group

    `group_id: Any`
    :   The id of a group

    `id: Any`
    :   Automatically assigned upon creation

    `updated_at: Any`
    :   When the group membership was last updated

    `url: Any`
    :   The API url of this record

    `user_id: Any`
    :   The id of an agent

<a id="GroupMembershipsContainsCondition"></a>

`GroupMembershipsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsAnyValueFilter`
    :   The type of the None singleton.

<a id="GroupMembershipsEqCondition"></a>

`GroupMembershipsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsSearchFilter`
    :   The type of the None singleton.

<a id="GroupMembershipsFuzzyCondition"></a>

`GroupMembershipsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsStringFilter`
    :   The type of the None singleton.

<a id="GroupMembershipsGtCondition"></a>

`GroupMembershipsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsSearchFilter`
    :   The type of the None singleton.

<a id="GroupMembershipsGteCondition"></a>

`GroupMembershipsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsSearchFilter`
    :   The type of the None singleton.

<a id="GroupMembershipsInCondition"></a>

`GroupMembershipsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsInFilter`
    :   The type of the None singleton.

<a id="GroupMembershipsInFilter"></a>

`GroupMembershipsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   When the group membership was created

    `default: list[bool]`
    :   If true, tickets assigned directly to the agent will assume this membership's group

    `group_id: list[int]`
    :   The id of a group

    `id: list[int]`
    :   Automatically assigned upon creation

    `updated_at: list[str]`
    :   When the group membership was last updated

    `url: list[str]`
    :   The API url of this record

    `user_id: list[int]`
    :   The id of an agent

<a id="GroupMembershipsKeywordCondition"></a>

`GroupMembershipsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsStringFilter`
    :   The type of the None singleton.

<a id="GroupMembershipsLikeCondition"></a>

`GroupMembershipsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsStringFilter`
    :   The type of the None singleton.

<a id="GroupMembershipsListParams"></a>

`GroupMembershipsListParams(*args, **kwargs)`
:   Parameters for group_memberships.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="GroupMembershipsLtCondition"></a>

`GroupMembershipsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsSearchFilter`
    :   The type of the None singleton.

<a id="GroupMembershipsLteCondition"></a>

`GroupMembershipsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsSearchFilter`
    :   The type of the None singleton.

<a id="GroupMembershipsNeqCondition"></a>

`GroupMembershipsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsSearchFilter`
    :   The type of the None singleton.

<a id="GroupMembershipsNotCondition"></a>

`GroupMembershipsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsAnyCondition`
    :   The type of the None singleton.

<a id="GroupMembershipsOrCondition"></a>

`GroupMembershipsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsAnyCondition]`
    :   The type of the None singleton.

<a id="GroupMembershipsSearchFilter"></a>

`GroupMembershipsSearchFilter(*args, **kwargs)`
:   Available fields for filtering group_memberships search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   When the group membership was created

    `default: bool | None`
    :   If true, tickets assigned directly to the agent will assume this membership's group

    `group_id: int | None`
    :   The id of a group

    `id: int | None`
    :   Automatically assigned upon creation

    `updated_at: str | None`
    :   When the group membership was last updated

    `url: str | None`
    :   The API url of this record

    `user_id: int | None`
    :   The id of an agent

<a id="GroupMembershipsSearchQuery"></a>

`GroupMembershipsSearchQuery(*args, **kwargs)`
:   Search query for group_memberships entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.GroupMembershipsSortFilter]`
    :   The type of the None singleton.

<a id="GroupMembershipsSortFilter"></a>

`GroupMembershipsSortFilter(*args, **kwargs)`
:   Available fields for sorting group_memberships search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   When the group membership was created

    `default: Literal['asc', 'desc']`
    :   If true, tickets assigned directly to the agent will assume this membership's group

    `group_id: Literal['asc', 'desc']`
    :   The id of a group

    `id: Literal['asc', 'desc']`
    :   Automatically assigned upon creation

    `updated_at: Literal['asc', 'desc']`
    :   When the group membership was last updated

    `url: Literal['asc', 'desc']`
    :   The API url of this record

    `user_id: Literal['asc', 'desc']`
    :   The id of an agent

<a id="GroupMembershipsStringFilter"></a>

`GroupMembershipsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   When the group membership was created

    `default: str`
    :   If true, tickets assigned directly to the agent will assume this membership's group

    `group_id: str`
    :   The id of a group

    `id: str`
    :   Automatically assigned upon creation

    `updated_at: str`
    :   When the group membership was last updated

    `url: str`
    :   The API url of this record

    `user_id: str`
    :   The id of an agent

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

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.GroupsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="GroupsAnyValueFilter"></a>

`GroupsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   Timestamp indicating when the group was created

    `default: Any`
    :   Indicates if the group is the default one for the account

    `deleted: Any`
    :   Indicates whether the group has been deleted

    `description: Any`
    :   The description of the group

    `id: Any`
    :   Unique identifier automatically assigned when creating groups

    `is_public: Any`
    :   Indicates if the group is public (true) or private (false)

    `name: Any`
    :   The name of the group

    `updated_at: Any`
    :   Timestamp indicating when the group was last updated

    `url: Any`
    :   The API URL of the group

<a id="GroupsContainsCondition"></a>

`GroupsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="GroupsEqCondition"></a>

`GroupsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsFuzzyCondition"></a>

`GroupsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsStringFilter`
    :   The type of the None singleton.

<a id="GroupsGetParams"></a>

`GroupsGetParams(*args, **kwargs)`
:   Parameters for groups.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `group_id: str`
    :   The type of the None singleton.

<a id="GroupsGtCondition"></a>

`GroupsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsGteCondition"></a>

`GroupsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsInFilter`
    :   The type of the None singleton.

<a id="GroupsInFilter"></a>

`GroupsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   Timestamp indicating when the group was created

    `default: list[bool]`
    :   Indicates if the group is the default one for the account

    `deleted: list[bool]`
    :   Indicates whether the group has been deleted

    `description: list[str]`
    :   The description of the group

    `id: list[int]`
    :   Unique identifier automatically assigned when creating groups

    `is_public: list[bool]`
    :   Indicates if the group is public (true) or private (false)

    `name: list[str]`
    :   The name of the group

    `updated_at: list[str]`
    :   Timestamp indicating when the group was last updated

    `url: list[str]`
    :   The API URL of the group

<a id="GroupsKeywordCondition"></a>

`GroupsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsStringFilter`
    :   The type of the None singleton.

<a id="GroupsLikeCondition"></a>

`GroupsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsStringFilter`
    :   The type of the None singleton.

<a id="GroupsListParams"></a>

`GroupsListParams(*args, **kwargs)`
:   Parameters for groups.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `exclude_deleted: bool`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="GroupsLtCondition"></a>

`GroupsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsLteCondition"></a>

`GroupsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsSearchFilter`
    :   The type of the None singleton.

<a id="GroupsNeqCondition"></a>

`GroupsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.GroupsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsAnyCondition]`
    :   The type of the None singleton.

<a id="GroupsSearchFilter"></a>

`GroupsSearchFilter(*args, **kwargs)`
:   Available fields for filtering groups search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   Timestamp indicating when the group was created

    `default: bool | None`
    :   Indicates if the group is the default one for the account

    `deleted: bool | None`
    :   Indicates whether the group has been deleted

    `description: str | None`
    :   The description of the group

    `id: int | None`
    :   Unique identifier automatically assigned when creating groups

    `is_public: bool | None`
    :   Indicates if the group is public (true) or private (false)

    `name: str | None`
    :   The name of the group

    `updated_at: str | None`
    :   Timestamp indicating when the group was last updated

    `url: str | None`
    :   The API URL of the group

<a id="GroupsSearchQuery"></a>

`GroupsSearchQuery(*args, **kwargs)`
:   Search query for groups entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.GroupsSortFilter]`
    :   The type of the None singleton.

<a id="GroupsSortFilter"></a>

`GroupsSortFilter(*args, **kwargs)`
:   Available fields for sorting groups search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the group was created

    `default: Literal['asc', 'desc']`
    :   Indicates if the group is the default one for the account

    `deleted: Literal['asc', 'desc']`
    :   Indicates whether the group has been deleted

    `description: Literal['asc', 'desc']`
    :   The description of the group

    `id: Literal['asc', 'desc']`
    :   Unique identifier automatically assigned when creating groups

    `is_public: Literal['asc', 'desc']`
    :   Indicates if the group is public (true) or private (false)

    `name: Literal['asc', 'desc']`
    :   The name of the group

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the group was last updated

    `url: Literal['asc', 'desc']`
    :   The API URL of the group

<a id="GroupsStringFilter"></a>

`GroupsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   Timestamp indicating when the group was created

    `default: str`
    :   Indicates if the group is the default one for the account

    `deleted: str`
    :   Indicates whether the group has been deleted

    `description: str`
    :   The description of the group

    `id: str`
    :   Unique identifier automatically assigned when creating groups

    `is_public: str`
    :   Indicates if the group is public (true) or private (false)

    `name: str`
    :   The name of the group

    `updated_at: str`
    :   Timestamp indicating when the group was last updated

    `url: str`
    :   The API URL of the group

<a id="MacrosAndCondition"></a>

`MacrosAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.MacrosEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosAnyCondition]`
    :   The type of the None singleton.

<a id="MacrosAnyCondition"></a>

`MacrosAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.MacrosAnyValueFilter`
    :   The type of the None singleton.

<a id="MacrosAnyValueFilter"></a>

`MacrosAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: Any`
    :   Actions to perform when macro is applied

    `active: Any`
    :   Useful for determining if the macro should be displayed

    `created_at: Any`
    :   The time the macro was created

    `description: Any`
    :   The description of the macro

    `id: Any`
    :   Automatically assigned when the macro is created

    `position: Any`
    :   The position of the macro

    `raw_title: Any`
    :   The dynamic content placeholder for title

    `restriction: Any`
    :   Who may access this macro

    `title: Any`
    :   The title of the macro

    `updated_at: Any`
    :   The time the macro was last updated

    `url: Any`
    :   A URL to access the macro's details

<a id="MacrosContainsCondition"></a>

`MacrosContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.MacrosAnyValueFilter`
    :   The type of the None singleton.

<a id="MacrosEqCondition"></a>

`MacrosEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.MacrosSearchFilter`
    :   The type of the None singleton.

<a id="MacrosFuzzyCondition"></a>

`MacrosFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.MacrosStringFilter`
    :   The type of the None singleton.

<a id="MacrosGetParams"></a>

`MacrosGetParams(*args, **kwargs)`
:   Parameters for macros.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `macro_id: str`
    :   The type of the None singleton.

<a id="MacrosGtCondition"></a>

`MacrosGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.MacrosSearchFilter`
    :   The type of the None singleton.

<a id="MacrosGteCondition"></a>

`MacrosGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.MacrosSearchFilter`
    :   The type of the None singleton.

<a id="MacrosInCondition"></a>

`MacrosInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.MacrosInFilter`
    :   The type of the None singleton.

<a id="MacrosInFilter"></a>

`MacrosInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: list[list[typing.Any]]`
    :   Actions to perform when macro is applied

    `active: list[bool]`
    :   Useful for determining if the macro should be displayed

    `created_at: list[str]`
    :   The time the macro was created

    `description: list[str]`
    :   The description of the macro

    `id: list[int]`
    :   Automatically assigned when the macro is created

    `position: list[int]`
    :   The position of the macro

    `raw_title: list[str]`
    :   The dynamic content placeholder for title

    `restriction: list[dict[str, typing.Any]]`
    :   Who may access this macro

    `title: list[str]`
    :   The title of the macro

    `updated_at: list[str]`
    :   The time the macro was last updated

    `url: list[str]`
    :   A URL to access the macro's details

<a id="MacrosKeywordCondition"></a>

`MacrosKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.MacrosStringFilter`
    :   The type of the None singleton.

<a id="MacrosLikeCondition"></a>

`MacrosLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.MacrosStringFilter`
    :   The type of the None singleton.

<a id="MacrosListParams"></a>

`MacrosListParams(*args, **kwargs)`
:   Parameters for macros.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `access: str`
    :   The type of the None singleton.

    `active: bool`
    :   The type of the None singleton.

    `category: int`
    :   The type of the None singleton.

    `group_id: int`
    :   The type of the None singleton.

    `only_viewable: bool`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

<a id="MacrosLtCondition"></a>

`MacrosLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.MacrosSearchFilter`
    :   The type of the None singleton.

<a id="MacrosLteCondition"></a>

`MacrosLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.MacrosSearchFilter`
    :   The type of the None singleton.

<a id="MacrosNeqCondition"></a>

`MacrosNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.MacrosSearchFilter`
    :   The type of the None singleton.

<a id="MacrosNotCondition"></a>

`MacrosNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.MacrosEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosAnyCondition`
    :   The type of the None singleton.

<a id="MacrosOrCondition"></a>

`MacrosOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.MacrosEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosAnyCondition]`
    :   The type of the None singleton.

<a id="MacrosSearchFilter"></a>

`MacrosSearchFilter(*args, **kwargs)`
:   Available fields for filtering macros search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: list[typing.Any] | None`
    :   Actions to perform when macro is applied

    `active: bool | None`
    :   Useful for determining if the macro should be displayed

    `created_at: str | None`
    :   The time the macro was created

    `description: str | None`
    :   The description of the macro

    `id: int | None`
    :   Automatically assigned when the macro is created

    `position: int | None`
    :   The position of the macro

    `raw_title: str | None`
    :   The dynamic content placeholder for title

    `restriction: dict[str, typing.Any] | None`
    :   Who may access this macro

    `title: str | None`
    :   The title of the macro

    `updated_at: str | None`
    :   The time the macro was last updated

    `url: str | None`
    :   A URL to access the macro's details

<a id="MacrosSearchQuery"></a>

`MacrosSearchQuery(*args, **kwargs)`
:   Search query for macros entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.MacrosEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.MacrosAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.MacrosSortFilter]`
    :   The type of the None singleton.

<a id="MacrosSortFilter"></a>

`MacrosSortFilter(*args, **kwargs)`
:   Available fields for sorting macros search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: Literal['asc', 'desc']`
    :   Actions to perform when macro is applied

    `active: Literal['asc', 'desc']`
    :   Useful for determining if the macro should be displayed

    `created_at: Literal['asc', 'desc']`
    :   The time the macro was created

    `description: Literal['asc', 'desc']`
    :   The description of the macro

    `id: Literal['asc', 'desc']`
    :   Automatically assigned when the macro is created

    `position: Literal['asc', 'desc']`
    :   The position of the macro

    `raw_title: Literal['asc', 'desc']`
    :   The dynamic content placeholder for title

    `restriction: Literal['asc', 'desc']`
    :   Who may access this macro

    `title: Literal['asc', 'desc']`
    :   The title of the macro

    `updated_at: Literal['asc', 'desc']`
    :   The time the macro was last updated

    `url: Literal['asc', 'desc']`
    :   A URL to access the macro's details

<a id="MacrosStringFilter"></a>

`MacrosStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: str`
    :   Actions to perform when macro is applied

    `active: str`
    :   Useful for determining if the macro should be displayed

    `created_at: str`
    :   The time the macro was created

    `description: str`
    :   The description of the macro

    `id: str`
    :   Automatically assigned when the macro is created

    `position: str`
    :   The position of the macro

    `raw_title: str`
    :   The dynamic content placeholder for title

    `restriction: str`
    :   Who may access this macro

    `title: str`
    :   The title of the macro

    `updated_at: str`
    :   The time the macro was last updated

    `url: str`
    :   A URL to access the macro's details

<a id="OrganizationMembershipsAndCondition"></a>

`OrganizationMembershipsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsAnyCondition]`
    :   The type of the None singleton.

<a id="OrganizationMembershipsAnyCondition"></a>

`OrganizationMembershipsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsAnyValueFilter`
    :   The type of the None singleton.

<a id="OrganizationMembershipsAnyValueFilter"></a>

`OrganizationMembershipsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   When the membership was created

    `default: Any`
    :   If true, this is the default organization for the user

    `id: Any`
    :   Automatically assigned when the membership is created

    `organization_id: Any`
    :   The ID of the organization associated with this user

    `organization_name: Any`
    :   The name of the organization

    `updated_at: Any`
    :   When the membership was last updated

    `url: Any`
    :   The API url of this membership

    `user_id: Any`
    :   The ID of the user for whom this memberships belongs

    `view_tickets: Any`
    :   If true, this user can view tickets from this organization

<a id="OrganizationMembershipsContainsCondition"></a>

`OrganizationMembershipsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsAnyValueFilter`
    :   The type of the None singleton.

<a id="OrganizationMembershipsEqCondition"></a>

`OrganizationMembershipsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationMembershipsFuzzyCondition"></a>

`OrganizationMembershipsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsStringFilter`
    :   The type of the None singleton.

<a id="OrganizationMembershipsGtCondition"></a>

`OrganizationMembershipsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationMembershipsGteCondition"></a>

`OrganizationMembershipsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationMembershipsInCondition"></a>

`OrganizationMembershipsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsInFilter`
    :   The type of the None singleton.

<a id="OrganizationMembershipsInFilter"></a>

`OrganizationMembershipsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   When the membership was created

    `default: list[bool]`
    :   If true, this is the default organization for the user

    `id: list[int]`
    :   Automatically assigned when the membership is created

    `organization_id: list[int]`
    :   The ID of the organization associated with this user

    `organization_name: list[str]`
    :   The name of the organization

    `updated_at: list[str]`
    :   When the membership was last updated

    `url: list[str]`
    :   The API url of this membership

    `user_id: list[int]`
    :   The ID of the user for whom this memberships belongs

    `view_tickets: list[bool]`
    :   If true, this user can view tickets from this organization

<a id="OrganizationMembershipsKeywordCondition"></a>

`OrganizationMembershipsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsStringFilter`
    :   The type of the None singleton.

<a id="OrganizationMembershipsLikeCondition"></a>

`OrganizationMembershipsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsStringFilter`
    :   The type of the None singleton.

<a id="OrganizationMembershipsListParams"></a>

`OrganizationMembershipsListParams(*args, **kwargs)`
:   Parameters for organization_memberships.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="OrganizationMembershipsLtCondition"></a>

`OrganizationMembershipsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationMembershipsLteCondition"></a>

`OrganizationMembershipsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationMembershipsNeqCondition"></a>

`OrganizationMembershipsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationMembershipsNotCondition"></a>

`OrganizationMembershipsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsAnyCondition`
    :   The type of the None singleton.

<a id="OrganizationMembershipsOrCondition"></a>

`OrganizationMembershipsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsAnyCondition]`
    :   The type of the None singleton.

<a id="OrganizationMembershipsSearchFilter"></a>

`OrganizationMembershipsSearchFilter(*args, **kwargs)`
:   Available fields for filtering organization_memberships search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   When the membership was created

    `default: bool | None`
    :   If true, this is the default organization for the user

    `id: int | None`
    :   Automatically assigned when the membership is created

    `organization_id: int | None`
    :   The ID of the organization associated with this user

    `organization_name: str | None`
    :   The name of the organization

    `updated_at: str | None`
    :   When the membership was last updated

    `url: str | None`
    :   The API url of this membership

    `user_id: int | None`
    :   The ID of the user for whom this memberships belongs

    `view_tickets: bool | None`
    :   If true, this user can view tickets from this organization

<a id="OrganizationMembershipsSearchQuery"></a>

`OrganizationMembershipsSearchQuery(*args, **kwargs)`
:   Search query for organization_memberships entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationMembershipsSortFilter]`
    :   The type of the None singleton.

<a id="OrganizationMembershipsSortFilter"></a>

`OrganizationMembershipsSortFilter(*args, **kwargs)`
:   Available fields for sorting organization_memberships search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   When the membership was created

    `default: Literal['asc', 'desc']`
    :   If true, this is the default organization for the user

    `id: Literal['asc', 'desc']`
    :   Automatically assigned when the membership is created

    `organization_id: Literal['asc', 'desc']`
    :   The ID of the organization associated with this user

    `organization_name: Literal['asc', 'desc']`
    :   The name of the organization

    `updated_at: Literal['asc', 'desc']`
    :   When the membership was last updated

    `url: Literal['asc', 'desc']`
    :   The API url of this membership

    `user_id: Literal['asc', 'desc']`
    :   The ID of the user for whom this memberships belongs

    `view_tickets: Literal['asc', 'desc']`
    :   If true, this user can view tickets from this organization

<a id="OrganizationMembershipsStringFilter"></a>

`OrganizationMembershipsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   When the membership was created

    `default: str`
    :   If true, this is the default organization for the user

    `id: str`
    :   Automatically assigned when the membership is created

    `organization_id: str`
    :   The ID of the organization associated with this user

    `organization_name: str`
    :   The name of the organization

    `updated_at: str`
    :   When the membership was last updated

    `url: str`
    :   The API url of this membership

    `user_id: str`
    :   The ID of the user for whom this memberships belongs

    `view_tickets: str`
    :   If true, this user can view tickets from this organization

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

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAnyValueFilter`
    :   The type of the None singleton.

<a id="OrganizationsAnyValueFilter"></a>

`OrganizationsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   Timestamp when the organization was created

    `deleted_at: Any`
    :   Timestamp when the organization was deleted

    `details: Any`
    :   Details about the organization, such as the address

    `domain_names: Any`
    :   Array of domain names associated with this organization for automatic user assignment

    `external_id: Any`
    :   Unique external identifier to associate the organization to an external record (case-insensitive)

    `group_id: Any`
    :   ID of the group where new tickets from users in this organization are automatically assigned

    `id: Any`
    :   Unique identifier automatically assigned when the organization is created

    `name: Any`
    :   Unique name for the organization (mandatory field)

    `notes: Any`
    :   Notes about the organization

    `organization_fields: Any`
    :   Key-value object for custom organization fields

    `shared_comments: Any`
    :   Boolean indicating whether end users in this organization can comment on each other's tickets

    `shared_tickets: Any`
    :   Boolean indicating whether end users in this organization can see each other's tickets

    `tags: Any`
    :   Array of tags associated with the organization

    `updated_at: Any`
    :   Timestamp of the last update to the organization

    `url: Any`
    :   The API URL of this organization

<a id="OrganizationsContainsCondition"></a>

`OrganizationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAnyValueFilter`
    :   The type of the None singleton.

<a id="OrganizationsEqCondition"></a>

`OrganizationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationsFuzzyCondition"></a>

`OrganizationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsStringFilter`
    :   The type of the None singleton.

<a id="OrganizationsGetParams"></a>

`OrganizationsGetParams(*args, **kwargs)`
:   Parameters for organizations.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `organization_id: str`
    :   The type of the None singleton.

<a id="OrganizationsGtCondition"></a>

`OrganizationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationsGteCondition"></a>

`OrganizationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsInFilter`
    :   The type of the None singleton.

<a id="OrganizationsInFilter"></a>

`OrganizationsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   Timestamp when the organization was created

    `deleted_at: list[str]`
    :   Timestamp when the organization was deleted

    `details: list[str]`
    :   Details about the organization, such as the address

    `domain_names: list[list[typing.Any]]`
    :   Array of domain names associated with this organization for automatic user assignment

    `external_id: list[str]`
    :   Unique external identifier to associate the organization to an external record (case-insensitive)

    `group_id: list[int]`
    :   ID of the group where new tickets from users in this organization are automatically assigned

    `id: list[int]`
    :   Unique identifier automatically assigned when the organization is created

    `name: list[str]`
    :   Unique name for the organization (mandatory field)

    `notes: list[str]`
    :   Notes about the organization

    `organization_fields: list[dict[str, typing.Any]]`
    :   Key-value object for custom organization fields

    `shared_comments: list[bool]`
    :   Boolean indicating whether end users in this organization can comment on each other's tickets

    `shared_tickets: list[bool]`
    :   Boolean indicating whether end users in this organization can see each other's tickets

    `tags: list[list[typing.Any]]`
    :   Array of tags associated with the organization

    `updated_at: list[str]`
    :   Timestamp of the last update to the organization

    `url: list[str]`
    :   The API URL of this organization

<a id="OrganizationsKeywordCondition"></a>

`OrganizationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsStringFilter`
    :   The type of the None singleton.

<a id="OrganizationsLikeCondition"></a>

`OrganizationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsStringFilter`
    :   The type of the None singleton.

<a id="OrganizationsListParams"></a>

`OrganizationsListParams(*args, **kwargs)`
:   Parameters for organizations.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="OrganizationsLtCondition"></a>

`OrganizationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationsLteCondition"></a>

`OrganizationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationsNeqCondition"></a>

`OrganizationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAnyCondition]`
    :   The type of the None singleton.

<a id="OrganizationsSearchFilter"></a>

`OrganizationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering organizations search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the organization was created

    `deleted_at: str | None`
    :   Timestamp when the organization was deleted

    `details: str | None`
    :   Details about the organization, such as the address

    `domain_names: list[typing.Any] | None`
    :   Array of domain names associated with this organization for automatic user assignment

    `external_id: str | None`
    :   Unique external identifier to associate the organization to an external record (case-insensitive)

    `group_id: int | None`
    :   ID of the group where new tickets from users in this organization are automatically assigned

    `id: int | None`
    :   Unique identifier automatically assigned when the organization is created

    `name: str | None`
    :   Unique name for the organization (mandatory field)

    `notes: str | None`
    :   Notes about the organization

    `organization_fields: dict[str, typing.Any] | None`
    :   Key-value object for custom organization fields

    `shared_comments: bool | None`
    :   Boolean indicating whether end users in this organization can comment on each other's tickets

    `shared_tickets: bool | None`
    :   Boolean indicating whether end users in this organization can see each other's tickets

    `tags: list[typing.Any] | None`
    :   Array of tags associated with the organization

    `updated_at: str | None`
    :   Timestamp of the last update to the organization

    `url: str | None`
    :   The API URL of this organization

<a id="OrganizationsSearchQuery"></a>

`OrganizationsSearchQuery(*args, **kwargs)`
:   Search query for organizations entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsSortFilter]`
    :   The type of the None singleton.

<a id="OrganizationsSortFilter"></a>

`OrganizationsSortFilter(*args, **kwargs)`
:   Available fields for sorting organizations search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the organization was created

    `deleted_at: Literal['asc', 'desc']`
    :   Timestamp when the organization was deleted

    `details: Literal['asc', 'desc']`
    :   Details about the organization, such as the address

    `domain_names: Literal['asc', 'desc']`
    :   Array of domain names associated with this organization for automatic user assignment

    `external_id: Literal['asc', 'desc']`
    :   Unique external identifier to associate the organization to an external record (case-insensitive)

    `group_id: Literal['asc', 'desc']`
    :   ID of the group where new tickets from users in this organization are automatically assigned

    `id: Literal['asc', 'desc']`
    :   Unique identifier automatically assigned when the organization is created

    `name: Literal['asc', 'desc']`
    :   Unique name for the organization (mandatory field)

    `notes: Literal['asc', 'desc']`
    :   Notes about the organization

    `organization_fields: Literal['asc', 'desc']`
    :   Key-value object for custom organization fields

    `shared_comments: Literal['asc', 'desc']`
    :   Boolean indicating whether end users in this organization can comment on each other's tickets

    `shared_tickets: Literal['asc', 'desc']`
    :   Boolean indicating whether end users in this organization can see each other's tickets

    `tags: Literal['asc', 'desc']`
    :   Array of tags associated with the organization

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp of the last update to the organization

    `url: Literal['asc', 'desc']`
    :   The API URL of this organization

<a id="OrganizationsStringFilter"></a>

`OrganizationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   Timestamp when the organization was created

    `deleted_at: str`
    :   Timestamp when the organization was deleted

    `details: str`
    :   Details about the organization, such as the address

    `domain_names: str`
    :   Array of domain names associated with this organization for automatic user assignment

    `external_id: str`
    :   Unique external identifier to associate the organization to an external record (case-insensitive)

    `group_id: str`
    :   ID of the group where new tickets from users in this organization are automatically assigned

    `id: str`
    :   Unique identifier automatically assigned when the organization is created

    `name: str`
    :   Unique name for the organization (mandatory field)

    `notes: str`
    :   Notes about the organization

    `organization_fields: str`
    :   Key-value object for custom organization fields

    `shared_comments: str`
    :   Boolean indicating whether end users in this organization can comment on each other's tickets

    `shared_tickets: str`
    :   Boolean indicating whether end users in this organization can see each other's tickets

    `tags: str`
    :   Array of tags associated with the organization

    `updated_at: str`
    :   Timestamp of the last update to the organization

    `url: str`
    :   The API URL of this organization

<a id="SatisfactionRatingsAndCondition"></a>

`SatisfactionRatingsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsAnyCondition]`
    :   The type of the None singleton.

<a id="SatisfactionRatingsAnyCondition"></a>

`SatisfactionRatingsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsAnyValueFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsAnyValueFilter"></a>

`SatisfactionRatingsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee_id: Any`
    :   The identifier of the agent assigned to the ticket at the time the rating was submitted

    `comment: Any`
    :   Optional comment provided by the requester with the rating

    `created_at: Any`
    :   Timestamp indicating when the satisfaction rating was created

    `group_id: Any`
    :   The identifier of the group assigned to the ticket at the time the rating was submitted

    `id: Any`
    :   Unique identifier for the satisfaction rating, automatically assigned upon creation

    `reason: Any`
    :   Free-text reason for a bad rating provided by the requester in a follow-up question

    `reason_id: Any`
    :   Identifier for the predefined reason given for a negative rating

    `requester_id: Any`
    :   The identifier of the ticket requester who submitted the satisfaction rating

    `score: Any`
    :   The satisfaction rating value: 'offered', 'unoffered', 'good', or 'bad'

    `ticket_id: Any`
    :   The identifier of the ticket being rated

    `updated_at: Any`
    :   Timestamp indicating when the satisfaction rating was last updated

    `url: Any`
    :   The API URL of this satisfaction rating resource

<a id="SatisfactionRatingsContainsCondition"></a>

`SatisfactionRatingsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsAnyValueFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsEqCondition"></a>

`SatisfactionRatingsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsFuzzyCondition"></a>

`SatisfactionRatingsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsStringFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsGetParams"></a>

`SatisfactionRatingsGetParams(*args, **kwargs)`
:   Parameters for satisfaction_ratings.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `satisfaction_rating_id: str`
    :   The type of the None singleton.

<a id="SatisfactionRatingsGtCondition"></a>

`SatisfactionRatingsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsGteCondition"></a>

`SatisfactionRatingsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsInCondition"></a>

`SatisfactionRatingsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsInFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsInFilter"></a>

`SatisfactionRatingsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee_id: list[int]`
    :   The identifier of the agent assigned to the ticket at the time the rating was submitted

    `comment: list[str]`
    :   Optional comment provided by the requester with the rating

    `created_at: list[str]`
    :   Timestamp indicating when the satisfaction rating was created

    `group_id: list[int]`
    :   The identifier of the group assigned to the ticket at the time the rating was submitted

    `id: list[int]`
    :   Unique identifier for the satisfaction rating, automatically assigned upon creation

    `reason: list[str]`
    :   Free-text reason for a bad rating provided by the requester in a follow-up question

    `reason_id: list[int]`
    :   Identifier for the predefined reason given for a negative rating

    `requester_id: list[int]`
    :   The identifier of the ticket requester who submitted the satisfaction rating

    `score: list[str]`
    :   The satisfaction rating value: 'offered', 'unoffered', 'good', or 'bad'

    `ticket_id: list[int]`
    :   The identifier of the ticket being rated

    `updated_at: list[str]`
    :   Timestamp indicating when the satisfaction rating was last updated

    `url: list[str]`
    :   The API URL of this satisfaction rating resource

<a id="SatisfactionRatingsKeywordCondition"></a>

`SatisfactionRatingsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsStringFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsLikeCondition"></a>

`SatisfactionRatingsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsStringFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsListParams"></a>

`SatisfactionRatingsListParams(*args, **kwargs)`
:   Parameters for satisfaction_ratings.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `end_time: int`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `score: str`
    :   The type of the None singleton.

    `start_time: int`
    :   The type of the None singleton.

<a id="SatisfactionRatingsLtCondition"></a>

`SatisfactionRatingsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsLteCondition"></a>

`SatisfactionRatingsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsNeqCondition"></a>

`SatisfactionRatingsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

<a id="SatisfactionRatingsNotCondition"></a>

`SatisfactionRatingsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsAnyCondition`
    :   The type of the None singleton.

<a id="SatisfactionRatingsOrCondition"></a>

`SatisfactionRatingsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsAnyCondition]`
    :   The type of the None singleton.

<a id="SatisfactionRatingsSearchFilter"></a>

`SatisfactionRatingsSearchFilter(*args, **kwargs)`
:   Available fields for filtering satisfaction_ratings search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee_id: int | None`
    :   The identifier of the agent assigned to the ticket at the time the rating was submitted

    `comment: str | None`
    :   Optional comment provided by the requester with the rating

    `created_at: str | None`
    :   Timestamp indicating when the satisfaction rating was created

    `group_id: int | None`
    :   The identifier of the group assigned to the ticket at the time the rating was submitted

    `id: int | None`
    :   Unique identifier for the satisfaction rating, automatically assigned upon creation

    `reason: str | None`
    :   Free-text reason for a bad rating provided by the requester in a follow-up question

    `reason_id: int | None`
    :   Identifier for the predefined reason given for a negative rating

    `requester_id: int | None`
    :   The identifier of the ticket requester who submitted the satisfaction rating

    `score: str | None`
    :   The satisfaction rating value: 'offered', 'unoffered', 'good', or 'bad'

    `ticket_id: int | None`
    :   The identifier of the ticket being rated

    `updated_at: str | None`
    :   Timestamp indicating when the satisfaction rating was last updated

    `url: str | None`
    :   The API URL of this satisfaction rating resource

<a id="SatisfactionRatingsSearchQuery"></a>

`SatisfactionRatingsSearchQuery(*args, **kwargs)`
:   Search query for satisfaction_ratings entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsSortFilter]`
    :   The type of the None singleton.

<a id="SatisfactionRatingsSortFilter"></a>

`SatisfactionRatingsSortFilter(*args, **kwargs)`
:   Available fields for sorting satisfaction_ratings search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee_id: Literal['asc', 'desc']`
    :   The identifier of the agent assigned to the ticket at the time the rating was submitted

    `comment: Literal['asc', 'desc']`
    :   Optional comment provided by the requester with the rating

    `created_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the satisfaction rating was created

    `group_id: Literal['asc', 'desc']`
    :   The identifier of the group assigned to the ticket at the time the rating was submitted

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the satisfaction rating, automatically assigned upon creation

    `reason: Literal['asc', 'desc']`
    :   Free-text reason for a bad rating provided by the requester in a follow-up question

    `reason_id: Literal['asc', 'desc']`
    :   Identifier for the predefined reason given for a negative rating

    `requester_id: Literal['asc', 'desc']`
    :   The identifier of the ticket requester who submitted the satisfaction rating

    `score: Literal['asc', 'desc']`
    :   The satisfaction rating value: 'offered', 'unoffered', 'good', or 'bad'

    `ticket_id: Literal['asc', 'desc']`
    :   The identifier of the ticket being rated

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the satisfaction rating was last updated

    `url: Literal['asc', 'desc']`
    :   The API URL of this satisfaction rating resource

<a id="SatisfactionRatingsStringFilter"></a>

`SatisfactionRatingsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee_id: str`
    :   The identifier of the agent assigned to the ticket at the time the rating was submitted

    `comment: str`
    :   Optional comment provided by the requester with the rating

    `created_at: str`
    :   Timestamp indicating when the satisfaction rating was created

    `group_id: str`
    :   The identifier of the group assigned to the ticket at the time the rating was submitted

    `id: str`
    :   Unique identifier for the satisfaction rating, automatically assigned upon creation

    `reason: str`
    :   Free-text reason for a bad rating provided by the requester in a follow-up question

    `reason_id: str`
    :   Identifier for the predefined reason given for a negative rating

    `requester_id: str`
    :   The identifier of the ticket requester who submitted the satisfaction rating

    `score: str`
    :   The satisfaction rating value: 'offered', 'unoffered', 'good', or 'bad'

    `ticket_id: str`
    :   The identifier of the ticket being rated

    `updated_at: str`
    :   Timestamp indicating when the satisfaction rating was last updated

    `url: str`
    :   The API URL of this satisfaction rating resource

<a id="SlaPoliciesAndCondition"></a>

`SlaPoliciesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesAnyCondition]`
    :   The type of the None singleton.

<a id="SlaPoliciesAnyCondition"></a>

`SlaPoliciesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesAnyValueFilter`
    :   The type of the None singleton.

<a id="SlaPoliciesAnyValueFilter"></a>

`SlaPoliciesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   When the SLA policy was created

    `description: Any`
    :   The description of the SLA policy

    `filter: Any`
    :   Filter for the SLA policy

    `id: Any`
    :   Automatically assigned when the SLA policy is created

    `policy_metrics: Any`
    :   Array of policy metrics

    `position: Any`
    :   Position of the SLA policy

    `title: Any`
    :   The title of the SLA policy

    `updated_at: Any`
    :   When the SLA policy was last updated

    `url: Any`
    :   URL of the SLA policy

<a id="SlaPoliciesContainsCondition"></a>

`SlaPoliciesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesAnyValueFilter`
    :   The type of the None singleton.

<a id="SlaPoliciesEqCondition"></a>

`SlaPoliciesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesSearchFilter`
    :   The type of the None singleton.

<a id="SlaPoliciesFuzzyCondition"></a>

`SlaPoliciesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesStringFilter`
    :   The type of the None singleton.

<a id="SlaPoliciesGetParams"></a>

`SlaPoliciesGetParams(*args, **kwargs)`
:   Parameters for sla_policies.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `sla_policy_id: str`
    :   The type of the None singleton.

<a id="SlaPoliciesGtCondition"></a>

`SlaPoliciesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesSearchFilter`
    :   The type of the None singleton.

<a id="SlaPoliciesGteCondition"></a>

`SlaPoliciesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesSearchFilter`
    :   The type of the None singleton.

<a id="SlaPoliciesInCondition"></a>

`SlaPoliciesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesInFilter`
    :   The type of the None singleton.

<a id="SlaPoliciesInFilter"></a>

`SlaPoliciesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   When the SLA policy was created

    `description: list[str]`
    :   The description of the SLA policy

    `filter: list[dict[str, typing.Any]]`
    :   Filter for the SLA policy

    `id: list[int]`
    :   Automatically assigned when the SLA policy is created

    `policy_metrics: list[list[typing.Any]]`
    :   Array of policy metrics

    `position: list[int]`
    :   Position of the SLA policy

    `title: list[str]`
    :   The title of the SLA policy

    `updated_at: list[str]`
    :   When the SLA policy was last updated

    `url: list[str]`
    :   URL of the SLA policy

<a id="SlaPoliciesKeywordCondition"></a>

`SlaPoliciesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesStringFilter`
    :   The type of the None singleton.

<a id="SlaPoliciesLikeCondition"></a>

`SlaPoliciesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesStringFilter`
    :   The type of the None singleton.

<a id="SlaPoliciesListParams"></a>

`SlaPoliciesListParams(*args, **kwargs)`
:   Parameters for sla_policies.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="SlaPoliciesLtCondition"></a>

`SlaPoliciesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesSearchFilter`
    :   The type of the None singleton.

<a id="SlaPoliciesLteCondition"></a>

`SlaPoliciesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesSearchFilter`
    :   The type of the None singleton.

<a id="SlaPoliciesNeqCondition"></a>

`SlaPoliciesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesSearchFilter`
    :   The type of the None singleton.

<a id="SlaPoliciesNotCondition"></a>

`SlaPoliciesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesAnyCondition`
    :   The type of the None singleton.

<a id="SlaPoliciesOrCondition"></a>

`SlaPoliciesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesAnyCondition]`
    :   The type of the None singleton.

<a id="SlaPoliciesSearchFilter"></a>

`SlaPoliciesSearchFilter(*args, **kwargs)`
:   Available fields for filtering sla_policies search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   When the SLA policy was created

    `description: str | None`
    :   The description of the SLA policy

    `filter: dict[str, typing.Any] | None`
    :   Filter for the SLA policy

    `id: int | None`
    :   Automatically assigned when the SLA policy is created

    `policy_metrics: list[typing.Any] | None`
    :   Array of policy metrics

    `position: int | None`
    :   Position of the SLA policy

    `title: str | None`
    :   The title of the SLA policy

    `updated_at: str | None`
    :   When the SLA policy was last updated

    `url: str | None`
    :   URL of the SLA policy

<a id="SlaPoliciesSearchQuery"></a>

`SlaPoliciesSearchQuery(*args, **kwargs)`
:   Search query for sla_policies entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.SlaPoliciesSortFilter]`
    :   The type of the None singleton.

<a id="SlaPoliciesSortFilter"></a>

`SlaPoliciesSortFilter(*args, **kwargs)`
:   Available fields for sorting sla_policies search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   When the SLA policy was created

    `description: Literal['asc', 'desc']`
    :   The description of the SLA policy

    `filter: Literal['asc', 'desc']`
    :   Filter for the SLA policy

    `id: Literal['asc', 'desc']`
    :   Automatically assigned when the SLA policy is created

    `policy_metrics: Literal['asc', 'desc']`
    :   Array of policy metrics

    `position: Literal['asc', 'desc']`
    :   Position of the SLA policy

    `title: Literal['asc', 'desc']`
    :   The title of the SLA policy

    `updated_at: Literal['asc', 'desc']`
    :   When the SLA policy was last updated

    `url: Literal['asc', 'desc']`
    :   URL of the SLA policy

<a id="SlaPoliciesStringFilter"></a>

`SlaPoliciesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   When the SLA policy was created

    `description: str`
    :   The description of the SLA policy

    `filter: str`
    :   Filter for the SLA policy

    `id: str`
    :   Automatically assigned when the SLA policy is created

    `policy_metrics: str`
    :   Array of policy metrics

    `position: str`
    :   Position of the SLA policy

    `title: str`
    :   The title of the SLA policy

    `updated_at: str`
    :   When the SLA policy was last updated

    `url: str`
    :   URL of the SLA policy

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

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.TagsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.TagsAnyValueFilter`
    :   The type of the None singleton.

<a id="TagsAnyValueFilter"></a>

`TagsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: Any`
    :   The number of times this tag has been used across resources

    `name: Any`
    :   The tag name string used to label and categorize resources

<a id="TagsContainsCondition"></a>

`TagsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.TagsAnyValueFilter`
    :   The type of the None singleton.

<a id="TagsEqCondition"></a>

`TagsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsFuzzyCondition"></a>

`TagsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.TagsStringFilter`
    :   The type of the None singleton.

<a id="TagsGtCondition"></a>

`TagsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsGteCondition"></a>

`TagsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.TagsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.TagsInFilter`
    :   The type of the None singleton.

<a id="TagsInFilter"></a>

`TagsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: list[int]`
    :   The number of times this tag has been used across resources

    `name: list[str]`
    :   The tag name string used to label and categorize resources

<a id="TagsKeywordCondition"></a>

`TagsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.TagsStringFilter`
    :   The type of the None singleton.

<a id="TagsLikeCondition"></a>

`TagsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.TagsStringFilter`
    :   The type of the None singleton.

<a id="TagsListParams"></a>

`TagsListParams(*args, **kwargs)`
:   Parameters for tags.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="TagsLtCondition"></a>

`TagsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsLteCondition"></a>

`TagsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsNeqCondition"></a>

`TagsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.TagsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.TagsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.TagsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsAnyCondition]`
    :   The type of the None singleton.

<a id="TagsSearchFilter"></a>

`TagsSearchFilter(*args, **kwargs)`
:   Available fields for filtering tags search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: int | None`
    :   The number of times this tag has been used across resources

    `name: str | None`
    :   The tag name string used to label and categorize resources

<a id="TagsSearchQuery"></a>

`TagsSearchQuery(*args, **kwargs)`
:   Search query for tags entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.TagsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.TagsSortFilter]`
    :   The type of the None singleton.

<a id="TagsSortFilter"></a>

`TagsSortFilter(*args, **kwargs)`
:   Available fields for sorting tags search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: Literal['asc', 'desc']`
    :   The number of times this tag has been used across resources

    `name: Literal['asc', 'desc']`
    :   The tag name string used to label and categorize resources

<a id="TagsStringFilter"></a>

`TagsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The number of times this tag has been used across resources

    `name: str`
    :   The tag name string used to label and categorize resources

<a id="TicketAuditsAndCondition"></a>

`TicketAuditsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketAuditsAnyCondition"></a>

`TicketAuditsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketAuditsAnyValueFilter"></a>

`TicketAuditsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: Any`
    :   Files or documents attached to the audit

    `author_id: Any`
    :   The unique identifier of the user who created the audit

    `created_at: Any`
    :   Timestamp indicating when the audit was created

    `events: Any`
    :   Array of events that occurred in this audit, such as field changes, comments, or tag updates

    `id: Any`
    :   Unique identifier for the audit record, automatically assigned when the audit is created

    `metadata: Any`
    :   Custom and system data associated with the audit

    `ticket_id: Any`
    :   The unique identifier of the ticket associated with this audit

    `via: Any`
    :   Describes how the audit was created, providing context about the creation source

<a id="TicketAuditsContainsCondition"></a>

`TicketAuditsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketAuditsEqCondition"></a>

`TicketAuditsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsSearchFilter`
    :   The type of the None singleton.

<a id="TicketAuditsFuzzyCondition"></a>

`TicketAuditsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsStringFilter`
    :   The type of the None singleton.

<a id="TicketAuditsGtCondition"></a>

`TicketAuditsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsSearchFilter`
    :   The type of the None singleton.

<a id="TicketAuditsGteCondition"></a>

`TicketAuditsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsSearchFilter`
    :   The type of the None singleton.

<a id="TicketAuditsInCondition"></a>

`TicketAuditsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsInFilter`
    :   The type of the None singleton.

<a id="TicketAuditsInFilter"></a>

`TicketAuditsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: list[list[typing.Any]]`
    :   Files or documents attached to the audit

    `author_id: list[int]`
    :   The unique identifier of the user who created the audit

    `created_at: list[str]`
    :   Timestamp indicating when the audit was created

    `events: list[list[typing.Any]]`
    :   Array of events that occurred in this audit, such as field changes, comments, or tag updates

    `id: list[int]`
    :   Unique identifier for the audit record, automatically assigned when the audit is created

    `metadata: list[dict[str, typing.Any]]`
    :   Custom and system data associated with the audit

    `ticket_id: list[int]`
    :   The unique identifier of the ticket associated with this audit

    `via: list[dict[str, typing.Any]]`
    :   Describes how the audit was created, providing context about the creation source

<a id="TicketAuditsKeywordCondition"></a>

`TicketAuditsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsStringFilter`
    :   The type of the None singleton.

<a id="TicketAuditsLikeCondition"></a>

`TicketAuditsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsStringFilter`
    :   The type of the None singleton.

<a id="TicketAuditsListParams"></a>

`TicketAuditsListParams(*args, **kwargs)`
:   Parameters for ticket_audits.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `ticket_id: str`
    :   The type of the None singleton.

<a id="TicketAuditsLtCondition"></a>

`TicketAuditsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsSearchFilter`
    :   The type of the None singleton.

<a id="TicketAuditsLteCondition"></a>

`TicketAuditsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsSearchFilter`
    :   The type of the None singleton.

<a id="TicketAuditsNeqCondition"></a>

`TicketAuditsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsSearchFilter`
    :   The type of the None singleton.

<a id="TicketAuditsNotCondition"></a>

`TicketAuditsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsAnyCondition`
    :   The type of the None singleton.

<a id="TicketAuditsOrCondition"></a>

`TicketAuditsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketAuditsSearchFilter"></a>

`TicketAuditsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ticket_audits search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: list[typing.Any] | None`
    :   Files or documents attached to the audit

    `author_id: int | None`
    :   The unique identifier of the user who created the audit

    `created_at: str | None`
    :   Timestamp indicating when the audit was created

    `events: list[typing.Any] | None`
    :   Array of events that occurred in this audit, such as field changes, comments, or tag updates

    `id: int | None`
    :   Unique identifier for the audit record, automatically assigned when the audit is created

    `metadata: dict[str, typing.Any] | None`
    :   Custom and system data associated with the audit

    `ticket_id: int | None`
    :   The unique identifier of the ticket associated with this audit

    `via: dict[str, typing.Any] | None`
    :   Describes how the audit was created, providing context about the creation source

<a id="TicketAuditsSearchQuery"></a>

`TicketAuditsSearchQuery(*args, **kwargs)`
:   Search query for ticket_audits entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsSortFilter]`
    :   The type of the None singleton.

<a id="TicketAuditsSortFilter"></a>

`TicketAuditsSortFilter(*args, **kwargs)`
:   Available fields for sorting ticket_audits search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: Literal['asc', 'desc']`
    :   Files or documents attached to the audit

    `author_id: Literal['asc', 'desc']`
    :   The unique identifier of the user who created the audit

    `created_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the audit was created

    `events: Literal['asc', 'desc']`
    :   Array of events that occurred in this audit, such as field changes, comments, or tag updates

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the audit record, automatically assigned when the audit is created

    `metadata: Literal['asc', 'desc']`
    :   Custom and system data associated with the audit

    `ticket_id: Literal['asc', 'desc']`
    :   The unique identifier of the ticket associated with this audit

    `via: Literal['asc', 'desc']`
    :   Describes how the audit was created, providing context about the creation source

<a id="TicketAuditsStringFilter"></a>

`TicketAuditsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: str`
    :   Files or documents attached to the audit

    `author_id: str`
    :   The unique identifier of the user who created the audit

    `created_at: str`
    :   Timestamp indicating when the audit was created

    `events: str`
    :   Array of events that occurred in this audit, such as field changes, comments, or tag updates

    `id: str`
    :   Unique identifier for the audit record, automatically assigned when the audit is created

    `metadata: str`
    :   Custom and system data associated with the audit

    `ticket_id: str`
    :   The unique identifier of the ticket associated with this audit

    `via: str`
    :   Describes how the audit was created, providing context about the creation source

<a id="TicketBulkUpdatesCreateParams"></a>

`TicketBulkUpdatesCreateParams(*args, **kwargs)`
:   Parameters for ticket_bulk_updates.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ids: str`
    :   The type of the None singleton.

    `ticket: airbyte_agent_sdk.connectors.zendesk_support.types.TicketBulkUpdatesCreateParamsTicket`
    :   The type of the None singleton.

<a id="TicketBulkUpdatesCreateParamsTicket"></a>

`TicketBulkUpdatesCreateParamsTicket(*args, **kwargs)`
:   The ticket fields to apply to all specified tickets

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `additional_tags: list[str]`
    :   The type of the None singleton.

    `assignee_id: int`
    :   The type of the None singleton.

    `group_id: int`
    :   The type of the None singleton.

    `priority: str`
    :   The type of the None singleton.

    `remove_tags: list[str]`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `tags: list[str]`
    :   The type of the None singleton.

<a id="TicketCommentsAndCondition"></a>

`TicketCommentsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketCommentsAnyCondition"></a>

`TicketCommentsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketCommentsAnyValueFilter"></a>

`TicketCommentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: Any`
    :   List of files or media attached to the comment

    `audit_id: Any`
    :   Identifier of the audit record associated with this comment event

    `author_id: Any`
    :   Identifier of the user who created the comment

    `body: Any`
    :   Content of the comment in its original format

    `created_at: Any`
    :   Timestamp when the comment was created

    `event_type: Any`
    :   Specific classification of the event within the ticket event stream

    `html_body: Any`
    :   HTML-formatted content of the comment

    `id: Any`
    :   Unique identifier for the comment event

    `metadata: Any`
    :   Additional structured information about the comment not covered by standard fields

    `plain_body: Any`
    :   Plain text content of the comment without formatting

    `public: Any`
    :   Boolean indicating whether the comment is visible to end users or is an internal note

    `ticket_id: Any`
    :   Identifier of the ticket to which this comment belongs

    `timestamp: Any`
    :   Timestamp of when the event occurred in the incremental export stream

    `type_: Any`
    :   Type of event, typically indicating this is a comment event

    `uploads: Any`
    :   Array of upload tokens or identifiers for files being attached to the comment

    `via: Any`
    :   Channel or method through which the comment was submitted

    `via_reference_id: Any`
    :   Reference identifier for the channel through which the comment was created

<a id="TicketCommentsContainsCondition"></a>

`TicketCommentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketCommentsCreateParams"></a>

`TicketCommentsCreateParams(*args, **kwargs)`
:   Parameters for ticket_comments.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ticket: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsCreateParamsTicket`
    :   The type of the None singleton.

    `ticket_id: str`
    :   The type of the None singleton.

<a id="TicketCommentsCreateParamsTicket"></a>

`TicketCommentsCreateParamsTicket(*args, **kwargs)`
:   The ticket update containing the comment

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `comment: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsCreateParamsTicketComment`
    :   The type of the None singleton.

<a id="TicketCommentsCreateParamsTicketComment"></a>

`TicketCommentsCreateParamsTicketComment(*args, **kwargs)`
:   The comment to add to the ticket

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: int`
    :   The type of the None singleton.

    `body: str`
    :   The type of the None singleton.

    `html_body: str`
    :   The type of the None singleton.

    `public: bool`
    :   The type of the None singleton.

<a id="TicketCommentsEqCondition"></a>

`TicketCommentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsSearchFilter`
    :   The type of the None singleton.

<a id="TicketCommentsFuzzyCondition"></a>

`TicketCommentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsStringFilter`
    :   The type of the None singleton.

<a id="TicketCommentsGtCondition"></a>

`TicketCommentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsSearchFilter`
    :   The type of the None singleton.

<a id="TicketCommentsGteCondition"></a>

`TicketCommentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsSearchFilter`
    :   The type of the None singleton.

<a id="TicketCommentsInCondition"></a>

`TicketCommentsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsInFilter`
    :   The type of the None singleton.

<a id="TicketCommentsInFilter"></a>

`TicketCommentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: list[list[typing.Any]]`
    :   List of files or media attached to the comment

    `audit_id: list[int]`
    :   Identifier of the audit record associated with this comment event

    `author_id: list[int]`
    :   Identifier of the user who created the comment

    `body: list[str]`
    :   Content of the comment in its original format

    `created_at: list[str]`
    :   Timestamp when the comment was created

    `event_type: list[str]`
    :   Specific classification of the event within the ticket event stream

    `html_body: list[str]`
    :   HTML-formatted content of the comment

    `id: list[int]`
    :   Unique identifier for the comment event

    `metadata: list[dict[str, typing.Any]]`
    :   Additional structured information about the comment not covered by standard fields

    `plain_body: list[str]`
    :   Plain text content of the comment without formatting

    `public: list[bool]`
    :   Boolean indicating whether the comment is visible to end users or is an internal note

    `ticket_id: list[int]`
    :   Identifier of the ticket to which this comment belongs

    `timestamp: list[int]`
    :   Timestamp of when the event occurred in the incremental export stream

    `type_: list[str]`
    :   Type of event, typically indicating this is a comment event

    `uploads: list[list[typing.Any]]`
    :   Array of upload tokens or identifiers for files being attached to the comment

    `via: list[dict[str, typing.Any]]`
    :   Channel or method through which the comment was submitted

    `via_reference_id: list[int]`
    :   Reference identifier for the channel through which the comment was created

<a id="TicketCommentsKeywordCondition"></a>

`TicketCommentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsStringFilter`
    :   The type of the None singleton.

<a id="TicketCommentsLikeCondition"></a>

`TicketCommentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsStringFilter`
    :   The type of the None singleton.

<a id="TicketCommentsListParams"></a>

`TicketCommentsListParams(*args, **kwargs)`
:   Parameters for ticket_comments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include_inline_images: bool`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

    `ticket_id: str`
    :   The type of the None singleton.

<a id="TicketCommentsLtCondition"></a>

`TicketCommentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsSearchFilter`
    :   The type of the None singleton.

<a id="TicketCommentsLteCondition"></a>

`TicketCommentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsSearchFilter`
    :   The type of the None singleton.

<a id="TicketCommentsNeqCondition"></a>

`TicketCommentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsSearchFilter`
    :   The type of the None singleton.

<a id="TicketCommentsNotCondition"></a>

`TicketCommentsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsAnyCondition`
    :   The type of the None singleton.

<a id="TicketCommentsOrCondition"></a>

`TicketCommentsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketCommentsSearchFilter"></a>

`TicketCommentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ticket_comments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: list[typing.Any] | None`
    :   List of files or media attached to the comment

    `audit_id: int | None`
    :   Identifier of the audit record associated with this comment event

    `author_id: int | None`
    :   Identifier of the user who created the comment

    `body: str | None`
    :   Content of the comment in its original format

    `created_at: str | None`
    :   Timestamp when the comment was created

    `event_type: str | None`
    :   Specific classification of the event within the ticket event stream

    `html_body: str | None`
    :   HTML-formatted content of the comment

    `id: int | None`
    :   Unique identifier for the comment event

    `metadata: dict[str, typing.Any] | None`
    :   Additional structured information about the comment not covered by standard fields

    `plain_body: str | None`
    :   Plain text content of the comment without formatting

    `public: bool | None`
    :   Boolean indicating whether the comment is visible to end users or is an internal note

    `ticket_id: int | None`
    :   Identifier of the ticket to which this comment belongs

    `timestamp: int | None`
    :   Timestamp of when the event occurred in the incremental export stream

    `type_: str | None`
    :   Type of event, typically indicating this is a comment event

    `uploads: list[typing.Any] | None`
    :   Array of upload tokens or identifiers for files being attached to the comment

    `via: dict[str, typing.Any] | None`
    :   Channel or method through which the comment was submitted

    `via_reference_id: int | None`
    :   Reference identifier for the channel through which the comment was created

<a id="TicketCommentsSearchQuery"></a>

`TicketCommentsSearchQuery(*args, **kwargs)`
:   Search query for ticket_comments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsSortFilter]`
    :   The type of the None singleton.

<a id="TicketCommentsSortFilter"></a>

`TicketCommentsSortFilter(*args, **kwargs)`
:   Available fields for sorting ticket_comments search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: Literal['asc', 'desc']`
    :   List of files or media attached to the comment

    `audit_id: Literal['asc', 'desc']`
    :   Identifier of the audit record associated with this comment event

    `author_id: Literal['asc', 'desc']`
    :   Identifier of the user who created the comment

    `body: Literal['asc', 'desc']`
    :   Content of the comment in its original format

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the comment was created

    `event_type: Literal['asc', 'desc']`
    :   Specific classification of the event within the ticket event stream

    `html_body: Literal['asc', 'desc']`
    :   HTML-formatted content of the comment

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the comment event

    `metadata: Literal['asc', 'desc']`
    :   Additional structured information about the comment not covered by standard fields

    `plain_body: Literal['asc', 'desc']`
    :   Plain text content of the comment without formatting

    `public: Literal['asc', 'desc']`
    :   Boolean indicating whether the comment is visible to end users or is an internal note

    `ticket_id: Literal['asc', 'desc']`
    :   Identifier of the ticket to which this comment belongs

    `timestamp: Literal['asc', 'desc']`
    :   Timestamp of when the event occurred in the incremental export stream

    `type_: Literal['asc', 'desc']`
    :   Type of event, typically indicating this is a comment event

    `uploads: Literal['asc', 'desc']`
    :   Array of upload tokens or identifiers for files being attached to the comment

    `via: Literal['asc', 'desc']`
    :   Channel or method through which the comment was submitted

    `via_reference_id: Literal['asc', 'desc']`
    :   Reference identifier for the channel through which the comment was created

<a id="TicketCommentsStringFilter"></a>

`TicketCommentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachments: str`
    :   List of files or media attached to the comment

    `audit_id: str`
    :   Identifier of the audit record associated with this comment event

    `author_id: str`
    :   Identifier of the user who created the comment

    `body: str`
    :   Content of the comment in its original format

    `created_at: str`
    :   Timestamp when the comment was created

    `event_type: str`
    :   Specific classification of the event within the ticket event stream

    `html_body: str`
    :   HTML-formatted content of the comment

    `id: str`
    :   Unique identifier for the comment event

    `metadata: str`
    :   Additional structured information about the comment not covered by standard fields

    `plain_body: str`
    :   Plain text content of the comment without formatting

    `public: str`
    :   Boolean indicating whether the comment is visible to end users or is an internal note

    `ticket_id: str`
    :   Identifier of the ticket to which this comment belongs

    `timestamp: str`
    :   Timestamp of when the event occurred in the incremental export stream

    `type_: str`
    :   Type of event, typically indicating this is a comment event

    `uploads: str`
    :   Array of upload tokens or identifiers for files being attached to the comment

    `via: str`
    :   Channel or method through which the comment was submitted

    `via_reference_id: str`
    :   Reference identifier for the channel through which the comment was created

<a id="TicketFieldsAndCondition"></a>

`TicketFieldsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketFieldsAnyCondition"></a>

`TicketFieldsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketFieldsAnyValueFilter"></a>

`TicketFieldsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Any`
    :   Whether this field is currently available for use

    `agent_description: Any`
    :   A description of the ticket field that only agents can see

    `collapsed_for_agents: Any`
    :   If true, the field is shown to agents by default; if false, it is hidden alongside infrequently used fields

    `created_at: Any`
    :   Timestamp when the custom ticket field was created

    `custom_field_options: Any`
    :   Array of option objects for custom ticket fields of type multiselect or tagger

    `custom_statuses: Any`
    :   List of customized ticket statuses, only present for system ticket fields of type custom_status

    `description: Any`
    :   Text describing the purpose of the ticket field to users

    `editable_in_portal: Any`
    :   Whether this field is editable by end users in Help Center

    `id: Any`
    :   Unique identifier for the ticket field, automatically assigned when created

    `key: Any`
    :   Internal identifier or reference key for the field

    `position: Any`
    :   The relative position of the ticket field on a ticket, controlling display order

    `raw_description: Any`
    :   The dynamic content placeholder if present, or the description value if not

    `raw_title: Any`
    :   The dynamic content placeholder if present, or the title value if not

    `raw_title_in_portal: Any`
    :   The dynamic content placeholder if present, or the title_in_portal value if not

    `regexp_for_validation: Any`
    :   For regexp fields only, the validation pattern for a field value to be deemed valid

    `removable: Any`
    :   If false, this field is a system field that must be present on all tickets

    `required: Any`
    :   If true, agents must enter a value in the field to change the ticket status to solved

    `required_in_portal: Any`
    :   If true, end users must enter a value in the field to create a request

    `sub_type_id: Any`
    :   For system ticket fields of type priority and status, controlling available options

    `system_field_options: Any`
    :   Array of options for system ticket fields of type tickettype, priority, or status

    `tag: Any`
    :   For checkbox fields only, a tag added to tickets when the checkbox field is selected

    `title: Any`
    :   The title of the ticket field displayed to agents

    `title_in_portal: Any`
    :   The title of the ticket field displayed to end users in Help Center

    `type_: Any`
    :   Field type such as text, textarea, checkbox, date, integer, decimal, regexp, multiselect, or tagger

    `updated_at: Any`
    :   Timestamp when the custom ticket field was last updated

    `url: Any`
    :   The API URL for this ticket field resource

    `visible_in_portal: Any`
    :   Whether this field is visible to end users in Help Center

<a id="TicketFieldsContainsCondition"></a>

`TicketFieldsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketFieldsEqCondition"></a>

`TicketFieldsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFieldsFuzzyCondition"></a>

`TicketFieldsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsStringFilter`
    :   The type of the None singleton.

<a id="TicketFieldsGetParams"></a>

`TicketFieldsGetParams(*args, **kwargs)`
:   Parameters for ticket_fields.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ticket_field_id: str`
    :   The type of the None singleton.

<a id="TicketFieldsGtCondition"></a>

`TicketFieldsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFieldsGteCondition"></a>

`TicketFieldsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFieldsInCondition"></a>

`TicketFieldsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsInFilter`
    :   The type of the None singleton.

<a id="TicketFieldsInFilter"></a>

`TicketFieldsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: list[bool]`
    :   Whether this field is currently available for use

    `agent_description: list[str]`
    :   A description of the ticket field that only agents can see

    `collapsed_for_agents: list[bool]`
    :   If true, the field is shown to agents by default; if false, it is hidden alongside infrequently used fields

    `created_at: list[str]`
    :   Timestamp when the custom ticket field was created

    `custom_field_options: list[list[typing.Any]]`
    :   Array of option objects for custom ticket fields of type multiselect or tagger

    `custom_statuses: list[list[typing.Any]]`
    :   List of customized ticket statuses, only present for system ticket fields of type custom_status

    `description: list[str]`
    :   Text describing the purpose of the ticket field to users

    `editable_in_portal: list[bool]`
    :   Whether this field is editable by end users in Help Center

    `id: list[int]`
    :   Unique identifier for the ticket field, automatically assigned when created

    `key: list[str]`
    :   Internal identifier or reference key for the field

    `position: list[int]`
    :   The relative position of the ticket field on a ticket, controlling display order

    `raw_description: list[str]`
    :   The dynamic content placeholder if present, or the description value if not

    `raw_title: list[str]`
    :   The dynamic content placeholder if present, or the title value if not

    `raw_title_in_portal: list[str]`
    :   The dynamic content placeholder if present, or the title_in_portal value if not

    `regexp_for_validation: list[str]`
    :   For regexp fields only, the validation pattern for a field value to be deemed valid

    `removable: list[bool]`
    :   If false, this field is a system field that must be present on all tickets

    `required: list[bool]`
    :   If true, agents must enter a value in the field to change the ticket status to solved

    `required_in_portal: list[bool]`
    :   If true, end users must enter a value in the field to create a request

    `sub_type_id: list[int]`
    :   For system ticket fields of type priority and status, controlling available options

    `system_field_options: list[list[typing.Any]]`
    :   Array of options for system ticket fields of type tickettype, priority, or status

    `tag: list[str]`
    :   For checkbox fields only, a tag added to tickets when the checkbox field is selected

    `title: list[str]`
    :   The title of the ticket field displayed to agents

    `title_in_portal: list[str]`
    :   The title of the ticket field displayed to end users in Help Center

    `type_: list[str]`
    :   Field type such as text, textarea, checkbox, date, integer, decimal, regexp, multiselect, or tagger

    `updated_at: list[str]`
    :   Timestamp when the custom ticket field was last updated

    `url: list[str]`
    :   The API URL for this ticket field resource

    `visible_in_portal: list[bool]`
    :   Whether this field is visible to end users in Help Center

<a id="TicketFieldsKeywordCondition"></a>

`TicketFieldsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsStringFilter`
    :   The type of the None singleton.

<a id="TicketFieldsLikeCondition"></a>

`TicketFieldsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsStringFilter`
    :   The type of the None singleton.

<a id="TicketFieldsListParams"></a>

`TicketFieldsListParams(*args, **kwargs)`
:   Parameters for ticket_fields.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `locale: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="TicketFieldsLtCondition"></a>

`TicketFieldsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFieldsLteCondition"></a>

`TicketFieldsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFieldsNeqCondition"></a>

`TicketFieldsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFieldsNotCondition"></a>

`TicketFieldsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsAnyCondition`
    :   The type of the None singleton.

<a id="TicketFieldsOrCondition"></a>

`TicketFieldsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketFieldsSearchFilter"></a>

`TicketFieldsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ticket_fields search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: bool | None`
    :   Whether this field is currently available for use

    `agent_description: str | None`
    :   A description of the ticket field that only agents can see

    `collapsed_for_agents: bool | None`
    :   If true, the field is shown to agents by default; if false, it is hidden alongside infrequently used fields

    `created_at: str | None`
    :   Timestamp when the custom ticket field was created

    `custom_field_options: list[typing.Any] | None`
    :   Array of option objects for custom ticket fields of type multiselect or tagger

    `custom_statuses: list[typing.Any] | None`
    :   List of customized ticket statuses, only present for system ticket fields of type custom_status

    `description: str | None`
    :   Text describing the purpose of the ticket field to users

    `editable_in_portal: bool | None`
    :   Whether this field is editable by end users in Help Center

    `id: int | None`
    :   Unique identifier for the ticket field, automatically assigned when created

    `key: str | None`
    :   Internal identifier or reference key for the field

    `position: int | None`
    :   The relative position of the ticket field on a ticket, controlling display order

    `raw_description: str | None`
    :   The dynamic content placeholder if present, or the description value if not

    `raw_title: str | None`
    :   The dynamic content placeholder if present, or the title value if not

    `raw_title_in_portal: str | None`
    :   The dynamic content placeholder if present, or the title_in_portal value if not

    `regexp_for_validation: str | None`
    :   For regexp fields only, the validation pattern for a field value to be deemed valid

    `removable: bool | None`
    :   If false, this field is a system field that must be present on all tickets

    `required: bool | None`
    :   If true, agents must enter a value in the field to change the ticket status to solved

    `required_in_portal: bool | None`
    :   If true, end users must enter a value in the field to create a request

    `sub_type_id: int | None`
    :   For system ticket fields of type priority and status, controlling available options

    `system_field_options: list[typing.Any] | None`
    :   Array of options for system ticket fields of type tickettype, priority, or status

    `tag: str | None`
    :   For checkbox fields only, a tag added to tickets when the checkbox field is selected

    `title: str | None`
    :   The title of the ticket field displayed to agents

    `title_in_portal: str | None`
    :   The title of the ticket field displayed to end users in Help Center

    `type_: str | None`
    :   Field type such as text, textarea, checkbox, date, integer, decimal, regexp, multiselect, or tagger

    `updated_at: str | None`
    :   Timestamp when the custom ticket field was last updated

    `url: str | None`
    :   The API URL for this ticket field resource

    `visible_in_portal: bool | None`
    :   Whether this field is visible to end users in Help Center

<a id="TicketFieldsSearchQuery"></a>

`TicketFieldsSearchQuery(*args, **kwargs)`
:   Search query for ticket_fields entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsSortFilter]`
    :   The type of the None singleton.

<a id="TicketFieldsSortFilter"></a>

`TicketFieldsSortFilter(*args, **kwargs)`
:   Available fields for sorting ticket_fields search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Literal['asc', 'desc']`
    :   Whether this field is currently available for use

    `agent_description: Literal['asc', 'desc']`
    :   A description of the ticket field that only agents can see

    `collapsed_for_agents: Literal['asc', 'desc']`
    :   If true, the field is shown to agents by default; if false, it is hidden alongside infrequently used fields

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the custom ticket field was created

    `custom_field_options: Literal['asc', 'desc']`
    :   Array of option objects for custom ticket fields of type multiselect or tagger

    `custom_statuses: Literal['asc', 'desc']`
    :   List of customized ticket statuses, only present for system ticket fields of type custom_status

    `description: Literal['asc', 'desc']`
    :   Text describing the purpose of the ticket field to users

    `editable_in_portal: Literal['asc', 'desc']`
    :   Whether this field is editable by end users in Help Center

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the ticket field, automatically assigned when created

    `key: Literal['asc', 'desc']`
    :   Internal identifier or reference key for the field

    `position: Literal['asc', 'desc']`
    :   The relative position of the ticket field on a ticket, controlling display order

    `raw_description: Literal['asc', 'desc']`
    :   The dynamic content placeholder if present, or the description value if not

    `raw_title: Literal['asc', 'desc']`
    :   The dynamic content placeholder if present, or the title value if not

    `raw_title_in_portal: Literal['asc', 'desc']`
    :   The dynamic content placeholder if present, or the title_in_portal value if not

    `regexp_for_validation: Literal['asc', 'desc']`
    :   For regexp fields only, the validation pattern for a field value to be deemed valid

    `removable: Literal['asc', 'desc']`
    :   If false, this field is a system field that must be present on all tickets

    `required: Literal['asc', 'desc']`
    :   If true, agents must enter a value in the field to change the ticket status to solved

    `required_in_portal: Literal['asc', 'desc']`
    :   If true, end users must enter a value in the field to create a request

    `sub_type_id: Literal['asc', 'desc']`
    :   For system ticket fields of type priority and status, controlling available options

    `system_field_options: Literal['asc', 'desc']`
    :   Array of options for system ticket fields of type tickettype, priority, or status

    `tag: Literal['asc', 'desc']`
    :   For checkbox fields only, a tag added to tickets when the checkbox field is selected

    `title: Literal['asc', 'desc']`
    :   The title of the ticket field displayed to agents

    `title_in_portal: Literal['asc', 'desc']`
    :   The title of the ticket field displayed to end users in Help Center

    `type_: Literal['asc', 'desc']`
    :   Field type such as text, textarea, checkbox, date, integer, decimal, regexp, multiselect, or tagger

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the custom ticket field was last updated

    `url: Literal['asc', 'desc']`
    :   The API URL for this ticket field resource

    `visible_in_portal: Literal['asc', 'desc']`
    :   Whether this field is visible to end users in Help Center

<a id="TicketFieldsStringFilter"></a>

`TicketFieldsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: str`
    :   Whether this field is currently available for use

    `agent_description: str`
    :   A description of the ticket field that only agents can see

    `collapsed_for_agents: str`
    :   If true, the field is shown to agents by default; if false, it is hidden alongside infrequently used fields

    `created_at: str`
    :   Timestamp when the custom ticket field was created

    `custom_field_options: str`
    :   Array of option objects for custom ticket fields of type multiselect or tagger

    `custom_statuses: str`
    :   List of customized ticket statuses, only present for system ticket fields of type custom_status

    `description: str`
    :   Text describing the purpose of the ticket field to users

    `editable_in_portal: str`
    :   Whether this field is editable by end users in Help Center

    `id: str`
    :   Unique identifier for the ticket field, automatically assigned when created

    `key: str`
    :   Internal identifier or reference key for the field

    `position: str`
    :   The relative position of the ticket field on a ticket, controlling display order

    `raw_description: str`
    :   The dynamic content placeholder if present, or the description value if not

    `raw_title: str`
    :   The dynamic content placeholder if present, or the title value if not

    `raw_title_in_portal: str`
    :   The dynamic content placeholder if present, or the title_in_portal value if not

    `regexp_for_validation: str`
    :   For regexp fields only, the validation pattern for a field value to be deemed valid

    `removable: str`
    :   If false, this field is a system field that must be present on all tickets

    `required: str`
    :   If true, agents must enter a value in the field to change the ticket status to solved

    `required_in_portal: str`
    :   If true, end users must enter a value in the field to create a request

    `sub_type_id: str`
    :   For system ticket fields of type priority and status, controlling available options

    `system_field_options: str`
    :   Array of options for system ticket fields of type tickettype, priority, or status

    `tag: str`
    :   For checkbox fields only, a tag added to tickets when the checkbox field is selected

    `title: str`
    :   The title of the ticket field displayed to agents

    `title_in_portal: str`
    :   The title of the ticket field displayed to end users in Help Center

    `type_: str`
    :   Field type such as text, textarea, checkbox, date, integer, decimal, regexp, multiselect, or tagger

    `updated_at: str`
    :   Timestamp when the custom ticket field was last updated

    `url: str`
    :   The API URL for this ticket field resource

    `visible_in_portal: str`
    :   Whether this field is visible to end users in Help Center

<a id="TicketFormsAndCondition"></a>

`TicketFormsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketFormsAnyCondition"></a>

`TicketFormsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketFormsAnyValueFilter"></a>

`TicketFormsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Any`
    :   Indicates if the form is set as active

    `agent_conditions: Any`
    :   Array of condition sets for agent workspaces

    `created_at: Any`
    :   Timestamp when the ticket form was created

    `default: Any`
    :   Indicates if the form is the default form for this account

    `display_name: Any`
    :   The name of the form that is displayed to an end user

    `end_user_conditions: Any`
    :   Array of condition sets for end user products

    `end_user_visible: Any`
    :   Indicates if the form is visible to the end user

    `id: Any`
    :   Unique identifier for the ticket form, automatically assigned when creating the form

    `in_all_brands: Any`
    :   Indicates if the form is available for use in all brands on this account

    `name: Any`
    :   The name of the ticket form

    `position: Any`
    :   The position of this form among other forms in the account, such as in a dropdown

    `raw_display_name: Any`
    :   The dynamic content placeholder if present, or the display_name value if not

    `raw_name: Any`
    :   The dynamic content placeholder if present, or the name value if not

    `restricted_brand_ids: Any`
    :   IDs of all brands that this ticket form is restricted to

    `ticket_field_ids: Any`
    :   IDs of all ticket fields included in this ticket form

    `updated_at: Any`
    :   Timestamp of the last update to the ticket form

    `url: Any`
    :   URL of the ticket form

<a id="TicketFormsContainsCondition"></a>

`TicketFormsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketFormsEqCondition"></a>

`TicketFormsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFormsFuzzyCondition"></a>

`TicketFormsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsStringFilter`
    :   The type of the None singleton.

<a id="TicketFormsGetParams"></a>

`TicketFormsGetParams(*args, **kwargs)`
:   Parameters for ticket_forms.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ticket_form_id: str`
    :   The type of the None singleton.

<a id="TicketFormsGtCondition"></a>

`TicketFormsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFormsGteCondition"></a>

`TicketFormsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFormsInCondition"></a>

`TicketFormsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsInFilter`
    :   The type of the None singleton.

<a id="TicketFormsInFilter"></a>

`TicketFormsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: list[bool]`
    :   Indicates if the form is set as active

    `agent_conditions: list[list[typing.Any]]`
    :   Array of condition sets for agent workspaces

    `created_at: list[str]`
    :   Timestamp when the ticket form was created

    `default: list[bool]`
    :   Indicates if the form is the default form for this account

    `display_name: list[str]`
    :   The name of the form that is displayed to an end user

    `end_user_conditions: list[list[typing.Any]]`
    :   Array of condition sets for end user products

    `end_user_visible: list[bool]`
    :   Indicates if the form is visible to the end user

    `id: list[int]`
    :   Unique identifier for the ticket form, automatically assigned when creating the form

    `in_all_brands: list[bool]`
    :   Indicates if the form is available for use in all brands on this account

    `name: list[str]`
    :   The name of the ticket form

    `position: list[int]`
    :   The position of this form among other forms in the account, such as in a dropdown

    `raw_display_name: list[str]`
    :   The dynamic content placeholder if present, or the display_name value if not

    `raw_name: list[str]`
    :   The dynamic content placeholder if present, or the name value if not

    `restricted_brand_ids: list[list[typing.Any]]`
    :   IDs of all brands that this ticket form is restricted to

    `ticket_field_ids: list[list[typing.Any]]`
    :   IDs of all ticket fields included in this ticket form

    `updated_at: list[str]`
    :   Timestamp of the last update to the ticket form

    `url: list[str]`
    :   URL of the ticket form

<a id="TicketFormsKeywordCondition"></a>

`TicketFormsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsStringFilter`
    :   The type of the None singleton.

<a id="TicketFormsLikeCondition"></a>

`TicketFormsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsStringFilter`
    :   The type of the None singleton.

<a id="TicketFormsListParams"></a>

`TicketFormsListParams(*args, **kwargs)`
:   Parameters for ticket_forms.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: bool`
    :   The type of the None singleton.

    `end_user_visible: bool`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="TicketFormsLtCondition"></a>

`TicketFormsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFormsLteCondition"></a>

`TicketFormsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFormsNeqCondition"></a>

`TicketFormsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFormsNotCondition"></a>

`TicketFormsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsAnyCondition`
    :   The type of the None singleton.

<a id="TicketFormsOrCondition"></a>

`TicketFormsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketFormsSearchFilter"></a>

`TicketFormsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ticket_forms search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: bool | None`
    :   Indicates if the form is set as active

    `agent_conditions: list[typing.Any] | None`
    :   Array of condition sets for agent workspaces

    `created_at: str | None`
    :   Timestamp when the ticket form was created

    `default: bool | None`
    :   Indicates if the form is the default form for this account

    `display_name: str | None`
    :   The name of the form that is displayed to an end user

    `end_user_conditions: list[typing.Any] | None`
    :   Array of condition sets for end user products

    `end_user_visible: bool | None`
    :   Indicates if the form is visible to the end user

    `id: int | None`
    :   Unique identifier for the ticket form, automatically assigned when creating the form

    `in_all_brands: bool | None`
    :   Indicates if the form is available for use in all brands on this account

    `name: str | None`
    :   The name of the ticket form

    `position: int | None`
    :   The position of this form among other forms in the account, such as in a dropdown

    `raw_display_name: str | None`
    :   The dynamic content placeholder if present, or the display_name value if not

    `raw_name: str | None`
    :   The dynamic content placeholder if present, or the name value if not

    `restricted_brand_ids: list[typing.Any] | None`
    :   IDs of all brands that this ticket form is restricted to

    `ticket_field_ids: list[typing.Any] | None`
    :   IDs of all ticket fields included in this ticket form

    `updated_at: str | None`
    :   Timestamp of the last update to the ticket form

    `url: str | None`
    :   URL of the ticket form

<a id="TicketFormsSearchQuery"></a>

`TicketFormsSearchQuery(*args, **kwargs)`
:   Search query for ticket_forms entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsSortFilter]`
    :   The type of the None singleton.

<a id="TicketFormsSortFilter"></a>

`TicketFormsSortFilter(*args, **kwargs)`
:   Available fields for sorting ticket_forms search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Literal['asc', 'desc']`
    :   Indicates if the form is set as active

    `agent_conditions: Literal['asc', 'desc']`
    :   Array of condition sets for agent workspaces

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the ticket form was created

    `default: Literal['asc', 'desc']`
    :   Indicates if the form is the default form for this account

    `display_name: Literal['asc', 'desc']`
    :   The name of the form that is displayed to an end user

    `end_user_conditions: Literal['asc', 'desc']`
    :   Array of condition sets for end user products

    `end_user_visible: Literal['asc', 'desc']`
    :   Indicates if the form is visible to the end user

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the ticket form, automatically assigned when creating the form

    `in_all_brands: Literal['asc', 'desc']`
    :   Indicates if the form is available for use in all brands on this account

    `name: Literal['asc', 'desc']`
    :   The name of the ticket form

    `position: Literal['asc', 'desc']`
    :   The position of this form among other forms in the account, such as in a dropdown

    `raw_display_name: Literal['asc', 'desc']`
    :   The dynamic content placeholder if present, or the display_name value if not

    `raw_name: Literal['asc', 'desc']`
    :   The dynamic content placeholder if present, or the name value if not

    `restricted_brand_ids: Literal['asc', 'desc']`
    :   IDs of all brands that this ticket form is restricted to

    `ticket_field_ids: Literal['asc', 'desc']`
    :   IDs of all ticket fields included in this ticket form

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp of the last update to the ticket form

    `url: Literal['asc', 'desc']`
    :   URL of the ticket form

<a id="TicketFormsStringFilter"></a>

`TicketFormsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: str`
    :   Indicates if the form is set as active

    `agent_conditions: str`
    :   Array of condition sets for agent workspaces

    `created_at: str`
    :   Timestamp when the ticket form was created

    `default: str`
    :   Indicates if the form is the default form for this account

    `display_name: str`
    :   The name of the form that is displayed to an end user

    `end_user_conditions: str`
    :   Array of condition sets for end user products

    `end_user_visible: str`
    :   Indicates if the form is visible to the end user

    `id: str`
    :   Unique identifier for the ticket form, automatically assigned when creating the form

    `in_all_brands: str`
    :   Indicates if the form is available for use in all brands on this account

    `name: str`
    :   The name of the ticket form

    `position: str`
    :   The position of this form among other forms in the account, such as in a dropdown

    `raw_display_name: str`
    :   The dynamic content placeholder if present, or the display_name value if not

    `raw_name: str`
    :   The dynamic content placeholder if present, or the name value if not

    `restricted_brand_ids: str`
    :   IDs of all brands that this ticket form is restricted to

    `ticket_field_ids: str`
    :   IDs of all ticket fields included in this ticket form

    `updated_at: str`
    :   Timestamp of the last update to the ticket form

    `url: str`
    :   URL of the ticket form

<a id="TicketMetricsAndCondition"></a>

`TicketMetricsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketMetricsAnyCondition"></a>

`TicketMetricsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketMetricsAnyValueFilter"></a>

`TicketMetricsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_wait_time_in_minutes: Any`
    :   Number of minutes the agent spent waiting during calendar and business hours

    `assigned_at: Any`
    :   Timestamp when the ticket was assigned

    `assignee_stations: Any`
    :   Number of assignees the ticket had

    `assignee_updated_at: Any`
    :   Timestamp when the assignee last updated the ticket

    `created_at: Any`
    :   Timestamp when the metric record was created

    `custom_status_updated_at: Any`
    :   Timestamp when the ticket's custom status was last updated

    `first_resolution_time_in_minutes: Any`
    :   Number of minutes to the first resolution time during calendar and business hours

    `full_resolution_time_in_minutes: Any`
    :   Number of minutes to the full resolution during calendar and business hours

    `generated_timestamp: Any`
    :   Timestamp of when record was last updated

    `group_stations: Any`
    :   Number of groups the ticket passed through

    `id: Any`
    :   Unique identifier for the ticket metric record

    `initially_assigned_at: Any`
    :   Timestamp when the ticket was initially assigned

    `instance_id: Any`
    :   ID of the Zendesk instance associated with the ticket

    `latest_comment_added_at: Any`
    :   Timestamp when the latest comment was added

    `metric: Any`
    :   Ticket metrics data

    `on_hold_time_in_minutes: Any`
    :   Number of minutes on hold

    `reopens: Any`
    :   Total number of times the ticket was reopened

    `replies: Any`
    :   The number of public replies added to a ticket by an agent

    `reply_time_in_minutes: Any`
    :   Number of minutes to the first reply during calendar and business hours

    `reply_time_in_seconds: Any`
    :   Number of seconds to the first reply during calendar hours, only available for Messaging tickets

    `requester_updated_at: Any`
    :   Timestamp when the requester last updated the ticket

    `requester_wait_time_in_minutes: Any`
    :   Number of minutes the requester spent waiting during calendar and business hours

    `solved_at: Any`
    :   Timestamp when the ticket was solved

    `status: Any`
    :   The current status of the ticket (open, pending, solved, etc.).

    `status_updated_at: Any`
    :   Timestamp when the status of the ticket was last updated

    `ticket_id: Any`
    :   Identifier of the associated ticket

    `time: Any`
    :   Time related to the ticket

    `type_: Any`
    :   Type of ticket

    `updated_at: Any`
    :   Timestamp when the metric record was last updated

    `url: Any`
    :   The API url of the ticket metric

<a id="TicketMetricsContainsCondition"></a>

`TicketMetricsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketMetricsEqCondition"></a>

`TicketMetricsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsSearchFilter`
    :   The type of the None singleton.

<a id="TicketMetricsFuzzyCondition"></a>

`TicketMetricsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsStringFilter`
    :   The type of the None singleton.

<a id="TicketMetricsGtCondition"></a>

`TicketMetricsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsSearchFilter`
    :   The type of the None singleton.

<a id="TicketMetricsGteCondition"></a>

`TicketMetricsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsSearchFilter`
    :   The type of the None singleton.

<a id="TicketMetricsInCondition"></a>

`TicketMetricsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsInFilter`
    :   The type of the None singleton.

<a id="TicketMetricsInFilter"></a>

`TicketMetricsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_wait_time_in_minutes: list[dict[str, typing.Any]]`
    :   Number of minutes the agent spent waiting during calendar and business hours

    `assigned_at: list[str]`
    :   Timestamp when the ticket was assigned

    `assignee_stations: list[int]`
    :   Number of assignees the ticket had

    `assignee_updated_at: list[str]`
    :   Timestamp when the assignee last updated the ticket

    `created_at: list[str]`
    :   Timestamp when the metric record was created

    `custom_status_updated_at: list[str]`
    :   Timestamp when the ticket's custom status was last updated

    `first_resolution_time_in_minutes: list[dict[str, typing.Any]]`
    :   Number of minutes to the first resolution time during calendar and business hours

    `full_resolution_time_in_minutes: list[dict[str, typing.Any]]`
    :   Number of minutes to the full resolution during calendar and business hours

    `generated_timestamp: list[int]`
    :   Timestamp of when record was last updated

    `group_stations: list[int]`
    :   Number of groups the ticket passed through

    `id: list[int]`
    :   Unique identifier for the ticket metric record

    `initially_assigned_at: list[str]`
    :   Timestamp when the ticket was initially assigned

    `instance_id: list[int]`
    :   ID of the Zendesk instance associated with the ticket

    `latest_comment_added_at: list[str]`
    :   Timestamp when the latest comment was added

    `metric: list[str]`
    :   Ticket metrics data

    `on_hold_time_in_minutes: list[dict[str, typing.Any]]`
    :   Number of minutes on hold

    `reopens: list[int]`
    :   Total number of times the ticket was reopened

    `replies: list[int]`
    :   The number of public replies added to a ticket by an agent

    `reply_time_in_minutes: list[dict[str, typing.Any]]`
    :   Number of minutes to the first reply during calendar and business hours

    `reply_time_in_seconds: list[dict[str, typing.Any]]`
    :   Number of seconds to the first reply during calendar hours, only available for Messaging tickets

    `requester_updated_at: list[str]`
    :   Timestamp when the requester last updated the ticket

    `requester_wait_time_in_minutes: list[dict[str, typing.Any]]`
    :   Number of minutes the requester spent waiting during calendar and business hours

    `solved_at: list[str]`
    :   Timestamp when the ticket was solved

    `status: list[dict[str, typing.Any]]`
    :   The current status of the ticket (open, pending, solved, etc.).

    `status_updated_at: list[str]`
    :   Timestamp when the status of the ticket was last updated

    `ticket_id: list[int]`
    :   Identifier of the associated ticket

    `time: list[str]`
    :   Time related to the ticket

    `type_: list[str]`
    :   Type of ticket

    `updated_at: list[str]`
    :   Timestamp when the metric record was last updated

    `url: list[str]`
    :   The API url of the ticket metric

<a id="TicketMetricsKeywordCondition"></a>

`TicketMetricsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsStringFilter`
    :   The type of the None singleton.

<a id="TicketMetricsLikeCondition"></a>

`TicketMetricsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsStringFilter`
    :   The type of the None singleton.

<a id="TicketMetricsListParams"></a>

`TicketMetricsListParams(*args, **kwargs)`
:   Parameters for ticket_metrics.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

<a id="TicketMetricsLtCondition"></a>

`TicketMetricsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsSearchFilter`
    :   The type of the None singleton.

<a id="TicketMetricsLteCondition"></a>

`TicketMetricsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsSearchFilter`
    :   The type of the None singleton.

<a id="TicketMetricsNeqCondition"></a>

`TicketMetricsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsSearchFilter`
    :   The type of the None singleton.

<a id="TicketMetricsNotCondition"></a>

`TicketMetricsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsAnyCondition`
    :   The type of the None singleton.

<a id="TicketMetricsOrCondition"></a>

`TicketMetricsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketMetricsSearchFilter"></a>

`TicketMetricsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ticket_metrics search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_wait_time_in_minutes: dict[str, typing.Any] | None`
    :   Number of minutes the agent spent waiting during calendar and business hours

    `assigned_at: str | None`
    :   Timestamp when the ticket was assigned

    `assignee_stations: int | None`
    :   Number of assignees the ticket had

    `assignee_updated_at: str | None`
    :   Timestamp when the assignee last updated the ticket

    `created_at: str | None`
    :   Timestamp when the metric record was created

    `custom_status_updated_at: str | None`
    :   Timestamp when the ticket's custom status was last updated

    `first_resolution_time_in_minutes: dict[str, typing.Any] | None`
    :   Number of minutes to the first resolution time during calendar and business hours

    `full_resolution_time_in_minutes: dict[str, typing.Any] | None`
    :   Number of minutes to the full resolution during calendar and business hours

    `generated_timestamp: int | None`
    :   Timestamp of when record was last updated

    `group_stations: int | None`
    :   Number of groups the ticket passed through

    `id: int | None`
    :   Unique identifier for the ticket metric record

    `initially_assigned_at: str | None`
    :   Timestamp when the ticket was initially assigned

    `instance_id: int | None`
    :   ID of the Zendesk instance associated with the ticket

    `latest_comment_added_at: str | None`
    :   Timestamp when the latest comment was added

    `metric: str | None`
    :   Ticket metrics data

    `on_hold_time_in_minutes: dict[str, typing.Any] | None`
    :   Number of minutes on hold

    `reopens: int | None`
    :   Total number of times the ticket was reopened

    `replies: int | None`
    :   The number of public replies added to a ticket by an agent

    `reply_time_in_minutes: dict[str, typing.Any] | None`
    :   Number of minutes to the first reply during calendar and business hours

    `reply_time_in_seconds: dict[str, typing.Any] | None`
    :   Number of seconds to the first reply during calendar hours, only available for Messaging tickets

    `requester_updated_at: str | None`
    :   Timestamp when the requester last updated the ticket

    `requester_wait_time_in_minutes: dict[str, typing.Any] | None`
    :   Number of minutes the requester spent waiting during calendar and business hours

    `solved_at: str | None`
    :   Timestamp when the ticket was solved

    `status: dict[str, typing.Any] | None`
    :   The current status of the ticket (open, pending, solved, etc.).

    `status_updated_at: str | None`
    :   Timestamp when the status of the ticket was last updated

    `ticket_id: int | None`
    :   Identifier of the associated ticket

    `time: str | None`
    :   Time related to the ticket

    `type_: str | None`
    :   Type of ticket

    `updated_at: str | None`
    :   Timestamp when the metric record was last updated

    `url: str | None`
    :   The API url of the ticket metric

<a id="TicketMetricsSearchQuery"></a>

`TicketMetricsSearchQuery(*args, **kwargs)`
:   Search query for ticket_metrics entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsSortFilter]`
    :   The type of the None singleton.

<a id="TicketMetricsSortFilter"></a>

`TicketMetricsSortFilter(*args, **kwargs)`
:   Available fields for sorting ticket_metrics search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_wait_time_in_minutes: Literal['asc', 'desc']`
    :   Number of minutes the agent spent waiting during calendar and business hours

    `assigned_at: Literal['asc', 'desc']`
    :   Timestamp when the ticket was assigned

    `assignee_stations: Literal['asc', 'desc']`
    :   Number of assignees the ticket had

    `assignee_updated_at: Literal['asc', 'desc']`
    :   Timestamp when the assignee last updated the ticket

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the metric record was created

    `custom_status_updated_at: Literal['asc', 'desc']`
    :   Timestamp when the ticket's custom status was last updated

    `first_resolution_time_in_minutes: Literal['asc', 'desc']`
    :   Number of minutes to the first resolution time during calendar and business hours

    `full_resolution_time_in_minutes: Literal['asc', 'desc']`
    :   Number of minutes to the full resolution during calendar and business hours

    `generated_timestamp: Literal['asc', 'desc']`
    :   Timestamp of when record was last updated

    `group_stations: Literal['asc', 'desc']`
    :   Number of groups the ticket passed through

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the ticket metric record

    `initially_assigned_at: Literal['asc', 'desc']`
    :   Timestamp when the ticket was initially assigned

    `instance_id: Literal['asc', 'desc']`
    :   ID of the Zendesk instance associated with the ticket

    `latest_comment_added_at: Literal['asc', 'desc']`
    :   Timestamp when the latest comment was added

    `metric: Literal['asc', 'desc']`
    :   Ticket metrics data

    `on_hold_time_in_minutes: Literal['asc', 'desc']`
    :   Number of minutes on hold

    `reopens: Literal['asc', 'desc']`
    :   Total number of times the ticket was reopened

    `replies: Literal['asc', 'desc']`
    :   The number of public replies added to a ticket by an agent

    `reply_time_in_minutes: Literal['asc', 'desc']`
    :   Number of minutes to the first reply during calendar and business hours

    `reply_time_in_seconds: Literal['asc', 'desc']`
    :   Number of seconds to the first reply during calendar hours, only available for Messaging tickets

    `requester_updated_at: Literal['asc', 'desc']`
    :   Timestamp when the requester last updated the ticket

    `requester_wait_time_in_minutes: Literal['asc', 'desc']`
    :   Number of minutes the requester spent waiting during calendar and business hours

    `solved_at: Literal['asc', 'desc']`
    :   Timestamp when the ticket was solved

    `status: Literal['asc', 'desc']`
    :   The current status of the ticket (open, pending, solved, etc.).

    `status_updated_at: Literal['asc', 'desc']`
    :   Timestamp when the status of the ticket was last updated

    `ticket_id: Literal['asc', 'desc']`
    :   Identifier of the associated ticket

    `time: Literal['asc', 'desc']`
    :   Time related to the ticket

    `type_: Literal['asc', 'desc']`
    :   Type of ticket

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the metric record was last updated

    `url: Literal['asc', 'desc']`
    :   The API url of the ticket metric

<a id="TicketMetricsStringFilter"></a>

`TicketMetricsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `agent_wait_time_in_minutes: str`
    :   Number of minutes the agent spent waiting during calendar and business hours

    `assigned_at: str`
    :   Timestamp when the ticket was assigned

    `assignee_stations: str`
    :   Number of assignees the ticket had

    `assignee_updated_at: str`
    :   Timestamp when the assignee last updated the ticket

    `created_at: str`
    :   Timestamp when the metric record was created

    `custom_status_updated_at: str`
    :   Timestamp when the ticket's custom status was last updated

    `first_resolution_time_in_minutes: str`
    :   Number of minutes to the first resolution time during calendar and business hours

    `full_resolution_time_in_minutes: str`
    :   Number of minutes to the full resolution during calendar and business hours

    `generated_timestamp: str`
    :   Timestamp of when record was last updated

    `group_stations: str`
    :   Number of groups the ticket passed through

    `id: str`
    :   Unique identifier for the ticket metric record

    `initially_assigned_at: str`
    :   Timestamp when the ticket was initially assigned

    `instance_id: str`
    :   ID of the Zendesk instance associated with the ticket

    `latest_comment_added_at: str`
    :   Timestamp when the latest comment was added

    `metric: str`
    :   Ticket metrics data

    `on_hold_time_in_minutes: str`
    :   Number of minutes on hold

    `reopens: str`
    :   Total number of times the ticket was reopened

    `replies: str`
    :   The number of public replies added to a ticket by an agent

    `reply_time_in_minutes: str`
    :   Number of minutes to the first reply during calendar and business hours

    `reply_time_in_seconds: str`
    :   Number of seconds to the first reply during calendar hours, only available for Messaging tickets

    `requester_updated_at: str`
    :   Timestamp when the requester last updated the ticket

    `requester_wait_time_in_minutes: str`
    :   Number of minutes the requester spent waiting during calendar and business hours

    `solved_at: str`
    :   Timestamp when the ticket was solved

    `status: str`
    :   The current status of the ticket (open, pending, solved, etc.).

    `status_updated_at: str`
    :   Timestamp when the status of the ticket was last updated

    `ticket_id: str`
    :   Identifier of the associated ticket

    `time: str`
    :   Time related to the ticket

    `type_: str`
    :   Type of ticket

    `updated_at: str`
    :   Timestamp when the metric record was last updated

    `url: str`
    :   The API url of the ticket metric

<a id="TicketsAndCondition"></a>

`TicketsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketsAnyCondition"></a>

`TicketsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketsAnyValueFilter"></a>

`TicketsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allow_attachments: Any`
    :   Boolean indicating whether attachments are allowed on the ticket

    `allow_channelback: Any`
    :   Boolean indicating whether agents can reply to the ticket through the original channel

    `assignee_id: Any`
    :   Unique identifier of the agent currently assigned to the ticket

    `brand_id: Any`
    :   Unique identifier of the brand associated with the ticket in multi-brand accounts

    `collaborator_ids: Any`
    :   Array of user identifiers who are collaborating on the ticket

    `created_at: Any`
    :   Timestamp indicating when the ticket was created

    `custom_fields: Any`
    :   Array of custom field values specific to the account's ticket configuration

    `custom_status_id: Any`
    :   Unique identifier of the custom status applied to the ticket

    `deleted_ticket_form_id: Any`
    :   The ID of the ticket form that was previously associated with this ticket but has since been deleted

    `description: Any`
    :   Initial description or content of the ticket when it was created

    `due_at: Any`
    :   Timestamp indicating when the ticket is due for completion or resolution

    `email_cc_ids: Any`
    :   Array of user identifiers who are CC'd on ticket email notifications

    `external_id: Any`
    :   External identifier for the ticket, used for integrations with other systems

    `fields: Any`
    :   Array of ticket field values including both system and custom fields

    `follower_ids: Any`
    :   Array of user identifiers who are following the ticket for updates

    `followup_ids: Any`
    :   Array of identifiers for follow-up tickets related to this ticket

    `forum_topic_id: Any`
    :   Unique identifier linking the ticket to a forum topic if applicable

    `from_messaging_channel: Any`
    :   Boolean indicating whether the ticket originated from a messaging channel

    `generated_timestamp: Any`
    :   Timestamp updated for all ticket updates including system changes, used for incremental export

    `group_id: Any`
    :   Unique identifier of the agent group assigned to handle the ticket

    `has_incidents: Any`
    :   Boolean indicating whether this problem ticket has related incident tickets

    `id: Any`
    :   Unique identifier for the ticket

    `is_public: Any`
    :   Boolean indicating whether the ticket is publicly visible

    `organization_id: Any`
    :   Unique identifier of the organization associated with the ticket

    `priority: Any`
    :   Priority level assigned to the ticket (e.g., urgent, high, normal, low)

    `problem_id: Any`
    :   Unique identifier of the problem ticket if this is an incident ticket

    `raw_subject: Any`
    :   Original unprocessed subject line before any system modifications

    `recipient: Any`
    :   Email address or identifier of the ticket recipient

    `requester_id: Any`
    :   Unique identifier of the user who requested or created the ticket

    `result_type: Any`
    :   The type of the search result (e.g. ticket) when returned from search endpoints

    `satisfaction_rating: Any`
    :   Object containing customer satisfaction rating data for the ticket

    `sharing_agreement_ids: Any`
    :   Array of sharing agreement identifiers if the ticket is shared across Zendesk instances

    `status: Any`
    :   Current status of the ticket (e.g., new, open, pending, solved, closed)

    `subject: Any`
    :   Subject line of the ticket describing the issue or request

    `submitter_id: Any`
    :   Unique identifier of the user who submitted the ticket on behalf of the requester

    `tags: Any`
    :   Array of tags applied to the ticket for categorization and filtering

    `ticket_form_id: Any`
    :   Unique identifier of the ticket form used when creating the ticket

    `type_: Any`
    :   Type of ticket (e.g., problem, incident, question, task)

    `updated_at: Any`
    :   Timestamp indicating when the ticket was last updated with a ticket event

    `url: Any`
    :   API URL to access the full ticket resource

    `via: Any`
    :   Object describing the channel and method through which the ticket was created

<a id="TicketsContainsCondition"></a>

`TicketsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketsCreateParams"></a>

`TicketsCreateParams(*args, **kwargs)`
:   Parameters for tickets.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ticket: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsCreateParamsTicket`
    :   The type of the None singleton.

<a id="TicketsCreateParamsTicket"></a>

`TicketsCreateParamsTicket(*args, **kwargs)`
:   The ticket object to create

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee_id: int`
    :   The type of the None singleton.

    `collaborator_ids: list[int]`
    :   The type of the None singleton.

    `comment: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsCreateParamsTicketComment`
    :   The type of the None singleton.

    `custom_fields: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketsCreateParamsTicketCustomFieldsItem]`
    :   The type of the None singleton.

    `description: str`
    :   The type of the None singleton.

    `due_at: str`
    :   The type of the None singleton.

    `external_id: str`
    :   The type of the None singleton.

    `group_id: int`
    :   The type of the None singleton.

    `organization_id: int`
    :   The type of the None singleton.

    `priority: str`
    :   The type of the None singleton.

    `requester_id: int`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `subject: str`
    :   The type of the None singleton.

    `tags: list[str]`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="TicketsCreateParamsTicketComment"></a>

`TicketsCreateParamsTicketComment(*args, **kwargs)`
:   An object that defines the initial comment on the ticket

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body: str`
    :   The type of the None singleton.

    `html_body: str`
    :   The type of the None singleton.

    `public: bool`
    :   The type of the None singleton.

<a id="TicketsCreateParamsTicketCustomFieldsItem"></a>

`TicketsCreateParamsTicketCustomFieldsItem(*args, **kwargs)`
:   Nested schema for TicketsCreateParamsTicket.custom_fields_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: int`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

<a id="TicketsEqCondition"></a>

`TicketsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsFuzzyCondition"></a>

`TicketsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsStringFilter`
    :   The type of the None singleton.

<a id="TicketsGetParams"></a>

`TicketsGetParams(*args, **kwargs)`
:   Parameters for tickets.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ticket_id: str`
    :   The type of the None singleton.

<a id="TicketsGtCondition"></a>

`TicketsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsGteCondition"></a>

`TicketsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsInCondition"></a>

`TicketsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsInFilter`
    :   The type of the None singleton.

<a id="TicketsInFilter"></a>

`TicketsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allow_attachments: list[bool]`
    :   Boolean indicating whether attachments are allowed on the ticket

    `allow_channelback: list[bool]`
    :   Boolean indicating whether agents can reply to the ticket through the original channel

    `assignee_id: list[int]`
    :   Unique identifier of the agent currently assigned to the ticket

    `brand_id: list[int]`
    :   Unique identifier of the brand associated with the ticket in multi-brand accounts

    `collaborator_ids: list[list[typing.Any]]`
    :   Array of user identifiers who are collaborating on the ticket

    `created_at: list[str]`
    :   Timestamp indicating when the ticket was created

    `custom_fields: list[list[typing.Any]]`
    :   Array of custom field values specific to the account's ticket configuration

    `custom_status_id: list[int]`
    :   Unique identifier of the custom status applied to the ticket

    `deleted_ticket_form_id: list[int]`
    :   The ID of the ticket form that was previously associated with this ticket but has since been deleted

    `description: list[str]`
    :   Initial description or content of the ticket when it was created

    `due_at: list[str]`
    :   Timestamp indicating when the ticket is due for completion or resolution

    `email_cc_ids: list[list[typing.Any]]`
    :   Array of user identifiers who are CC'd on ticket email notifications

    `external_id: list[str]`
    :   External identifier for the ticket, used for integrations with other systems

    `fields: list[list[typing.Any]]`
    :   Array of ticket field values including both system and custom fields

    `follower_ids: list[list[typing.Any]]`
    :   Array of user identifiers who are following the ticket for updates

    `followup_ids: list[list[typing.Any]]`
    :   Array of identifiers for follow-up tickets related to this ticket

    `forum_topic_id: list[int]`
    :   Unique identifier linking the ticket to a forum topic if applicable

    `from_messaging_channel: list[bool]`
    :   Boolean indicating whether the ticket originated from a messaging channel

    `generated_timestamp: list[int]`
    :   Timestamp updated for all ticket updates including system changes, used for incremental export

    `group_id: list[int]`
    :   Unique identifier of the agent group assigned to handle the ticket

    `has_incidents: list[bool]`
    :   Boolean indicating whether this problem ticket has related incident tickets

    `id: list[int]`
    :   Unique identifier for the ticket

    `is_public: list[bool]`
    :   Boolean indicating whether the ticket is publicly visible

    `organization_id: list[int]`
    :   Unique identifier of the organization associated with the ticket

    `priority: list[str]`
    :   Priority level assigned to the ticket (e.g., urgent, high, normal, low)

    `problem_id: list[int]`
    :   Unique identifier of the problem ticket if this is an incident ticket

    `raw_subject: list[str]`
    :   Original unprocessed subject line before any system modifications

    `recipient: list[str]`
    :   Email address or identifier of the ticket recipient

    `requester_id: list[int]`
    :   Unique identifier of the user who requested or created the ticket

    `result_type: list[str]`
    :   The type of the search result (e.g. ticket) when returned from search endpoints

    `satisfaction_rating: list[typing.Any]`
    :   Object containing customer satisfaction rating data for the ticket

    `sharing_agreement_ids: list[list[typing.Any]]`
    :   Array of sharing agreement identifiers if the ticket is shared across Zendesk instances

    `status: list[str]`
    :   Current status of the ticket (e.g., new, open, pending, solved, closed)

    `subject: list[str]`
    :   Subject line of the ticket describing the issue or request

    `submitter_id: list[int]`
    :   Unique identifier of the user who submitted the ticket on behalf of the requester

    `tags: list[list[typing.Any]]`
    :   Array of tags applied to the ticket for categorization and filtering

    `ticket_form_id: list[int]`
    :   Unique identifier of the ticket form used when creating the ticket

    `type_: list[str]`
    :   Type of ticket (e.g., problem, incident, question, task)

    `updated_at: list[str]`
    :   Timestamp indicating when the ticket was last updated with a ticket event

    `url: list[str]`
    :   API URL to access the full ticket resource

    `via: list[dict[str, typing.Any]]`
    :   Object describing the channel and method through which the ticket was created

<a id="TicketsKeywordCondition"></a>

`TicketsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsStringFilter`
    :   The type of the None singleton.

<a id="TicketsLikeCondition"></a>

`TicketsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsStringFilter`
    :   The type of the None singleton.

<a id="TicketsListParams"></a>

`TicketsListParams(*args, **kwargs)`
:   Parameters for tickets.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `external_id: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

<a id="TicketsLtCondition"></a>

`TicketsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsLteCondition"></a>

`TicketsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsNeqCondition"></a>

`TicketsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsSearchFilter`
    :   The type of the None singleton.

<a id="TicketsNotCondition"></a>

`TicketsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsAnyCondition`
    :   The type of the None singleton.

<a id="TicketsOrCondition"></a>

`TicketsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketsSearchFilter"></a>

`TicketsSearchFilter(*args, **kwargs)`
:   Available fields for filtering tickets search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allow_attachments: bool | None`
    :   Boolean indicating whether attachments are allowed on the ticket

    `allow_channelback: bool | None`
    :   Boolean indicating whether agents can reply to the ticket through the original channel

    `assignee_id: int | None`
    :   Unique identifier of the agent currently assigned to the ticket

    `brand_id: int | None`
    :   Unique identifier of the brand associated with the ticket in multi-brand accounts

    `collaborator_ids: list[typing.Any] | None`
    :   Array of user identifiers who are collaborating on the ticket

    `created_at: str | None`
    :   Timestamp indicating when the ticket was created

    `custom_fields: list[typing.Any] | None`
    :   Array of custom field values specific to the account's ticket configuration

    `custom_status_id: int | None`
    :   Unique identifier of the custom status applied to the ticket

    `deleted_ticket_form_id: int | None`
    :   The ID of the ticket form that was previously associated with this ticket but has since been deleted

    `description: str | None`
    :   Initial description or content of the ticket when it was created

    `due_at: str | None`
    :   Timestamp indicating when the ticket is due for completion or resolution

    `email_cc_ids: list[typing.Any] | None`
    :   Array of user identifiers who are CC'd on ticket email notifications

    `external_id: str | None`
    :   External identifier for the ticket, used for integrations with other systems

    `fields: list[typing.Any] | None`
    :   Array of ticket field values including both system and custom fields

    `follower_ids: list[typing.Any] | None`
    :   Array of user identifiers who are following the ticket for updates

    `followup_ids: list[typing.Any] | None`
    :   Array of identifiers for follow-up tickets related to this ticket

    `forum_topic_id: int | None`
    :   Unique identifier linking the ticket to a forum topic if applicable

    `from_messaging_channel: bool | None`
    :   Boolean indicating whether the ticket originated from a messaging channel

    `generated_timestamp: int | None`
    :   Timestamp updated for all ticket updates including system changes, used for incremental export

    `group_id: int | None`
    :   Unique identifier of the agent group assigned to handle the ticket

    `has_incidents: bool | None`
    :   Boolean indicating whether this problem ticket has related incident tickets

    `id: int | None`
    :   Unique identifier for the ticket

    `is_public: bool | None`
    :   Boolean indicating whether the ticket is publicly visible

    `organization_id: int | None`
    :   Unique identifier of the organization associated with the ticket

    `priority: str | None`
    :   Priority level assigned to the ticket (e.g., urgent, high, normal, low)

    `problem_id: int | None`
    :   Unique identifier of the problem ticket if this is an incident ticket

    `raw_subject: str | None`
    :   Original unprocessed subject line before any system modifications

    `recipient: str | None`
    :   Email address or identifier of the ticket recipient

    `requester_id: int | None`
    :   Unique identifier of the user who requested or created the ticket

    `result_type: str | None`
    :   The type of the search result (e.g. ticket) when returned from search endpoints

    `satisfaction_rating: Any`
    :   Object containing customer satisfaction rating data for the ticket

    `sharing_agreement_ids: list[typing.Any] | None`
    :   Array of sharing agreement identifiers if the ticket is shared across Zendesk instances

    `status: str | None`
    :   Current status of the ticket (e.g., new, open, pending, solved, closed)

    `subject: str | None`
    :   Subject line of the ticket describing the issue or request

    `submitter_id: int | None`
    :   Unique identifier of the user who submitted the ticket on behalf of the requester

    `tags: list[typing.Any] | None`
    :   Array of tags applied to the ticket for categorization and filtering

    `ticket_form_id: int | None`
    :   Unique identifier of the ticket form used when creating the ticket

    `type_: str | None`
    :   Type of ticket (e.g., problem, incident, question, task)

    `updated_at: str | None`
    :   Timestamp indicating when the ticket was last updated with a ticket event

    `url: str | None`
    :   API URL to access the full ticket resource

    `via: dict[str, typing.Any] | None`
    :   Object describing the channel and method through which the ticket was created

<a id="TicketsSearchQuery"></a>

`TicketsSearchQuery(*args, **kwargs)`
:   Search query for tickets entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketsSortFilter]`
    :   The type of the None singleton.

<a id="TicketsSortFilter"></a>

`TicketsSortFilter(*args, **kwargs)`
:   Available fields for sorting tickets search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allow_attachments: Literal['asc', 'desc']`
    :   Boolean indicating whether attachments are allowed on the ticket

    `allow_channelback: Literal['asc', 'desc']`
    :   Boolean indicating whether agents can reply to the ticket through the original channel

    `assignee_id: Literal['asc', 'desc']`
    :   Unique identifier of the agent currently assigned to the ticket

    `brand_id: Literal['asc', 'desc']`
    :   Unique identifier of the brand associated with the ticket in multi-brand accounts

    `collaborator_ids: Literal['asc', 'desc']`
    :   Array of user identifiers who are collaborating on the ticket

    `created_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the ticket was created

    `custom_fields: Literal['asc', 'desc']`
    :   Array of custom field values specific to the account's ticket configuration

    `custom_status_id: Literal['asc', 'desc']`
    :   Unique identifier of the custom status applied to the ticket

    `deleted_ticket_form_id: Literal['asc', 'desc']`
    :   The ID of the ticket form that was previously associated with this ticket but has since been deleted

    `description: Literal['asc', 'desc']`
    :   Initial description or content of the ticket when it was created

    `due_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the ticket is due for completion or resolution

    `email_cc_ids: Literal['asc', 'desc']`
    :   Array of user identifiers who are CC'd on ticket email notifications

    `external_id: Literal['asc', 'desc']`
    :   External identifier for the ticket, used for integrations with other systems

    `fields: Literal['asc', 'desc']`
    :   Array of ticket field values including both system and custom fields

    `follower_ids: Literal['asc', 'desc']`
    :   Array of user identifiers who are following the ticket for updates

    `followup_ids: Literal['asc', 'desc']`
    :   Array of identifiers for follow-up tickets related to this ticket

    `forum_topic_id: Literal['asc', 'desc']`
    :   Unique identifier linking the ticket to a forum topic if applicable

    `from_messaging_channel: Literal['asc', 'desc']`
    :   Boolean indicating whether the ticket originated from a messaging channel

    `generated_timestamp: Literal['asc', 'desc']`
    :   Timestamp updated for all ticket updates including system changes, used for incremental export

    `group_id: Literal['asc', 'desc']`
    :   Unique identifier of the agent group assigned to handle the ticket

    `has_incidents: Literal['asc', 'desc']`
    :   Boolean indicating whether this problem ticket has related incident tickets

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the ticket

    `is_public: Literal['asc', 'desc']`
    :   Boolean indicating whether the ticket is publicly visible

    `organization_id: Literal['asc', 'desc']`
    :   Unique identifier of the organization associated with the ticket

    `priority: Literal['asc', 'desc']`
    :   Priority level assigned to the ticket (e.g., urgent, high, normal, low)

    `problem_id: Literal['asc', 'desc']`
    :   Unique identifier of the problem ticket if this is an incident ticket

    `raw_subject: Literal['asc', 'desc']`
    :   Original unprocessed subject line before any system modifications

    `recipient: Literal['asc', 'desc']`
    :   Email address or identifier of the ticket recipient

    `requester_id: Literal['asc', 'desc']`
    :   Unique identifier of the user who requested or created the ticket

    `result_type: Literal['asc', 'desc']`
    :   The type of the search result (e.g. ticket) when returned from search endpoints

    `satisfaction_rating: Literal['asc', 'desc']`
    :   Object containing customer satisfaction rating data for the ticket

    `sharing_agreement_ids: Literal['asc', 'desc']`
    :   Array of sharing agreement identifiers if the ticket is shared across Zendesk instances

    `status: Literal['asc', 'desc']`
    :   Current status of the ticket (e.g., new, open, pending, solved, closed)

    `subject: Literal['asc', 'desc']`
    :   Subject line of the ticket describing the issue or request

    `submitter_id: Literal['asc', 'desc']`
    :   Unique identifier of the user who submitted the ticket on behalf of the requester

    `tags: Literal['asc', 'desc']`
    :   Array of tags applied to the ticket for categorization and filtering

    `ticket_form_id: Literal['asc', 'desc']`
    :   Unique identifier of the ticket form used when creating the ticket

    `type_: Literal['asc', 'desc']`
    :   Type of ticket (e.g., problem, incident, question, task)

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the ticket was last updated with a ticket event

    `url: Literal['asc', 'desc']`
    :   API URL to access the full ticket resource

    `via: Literal['asc', 'desc']`
    :   Object describing the channel and method through which the ticket was created

<a id="TicketsStringFilter"></a>

`TicketsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `allow_attachments: str`
    :   Boolean indicating whether attachments are allowed on the ticket

    `allow_channelback: str`
    :   Boolean indicating whether agents can reply to the ticket through the original channel

    `assignee_id: str`
    :   Unique identifier of the agent currently assigned to the ticket

    `brand_id: str`
    :   Unique identifier of the brand associated with the ticket in multi-brand accounts

    `collaborator_ids: str`
    :   Array of user identifiers who are collaborating on the ticket

    `created_at: str`
    :   Timestamp indicating when the ticket was created

    `custom_fields: str`
    :   Array of custom field values specific to the account's ticket configuration

    `custom_status_id: str`
    :   Unique identifier of the custom status applied to the ticket

    `deleted_ticket_form_id: str`
    :   The ID of the ticket form that was previously associated with this ticket but has since been deleted

    `description: str`
    :   Initial description or content of the ticket when it was created

    `due_at: str`
    :   Timestamp indicating when the ticket is due for completion or resolution

    `email_cc_ids: str`
    :   Array of user identifiers who are CC'd on ticket email notifications

    `external_id: str`
    :   External identifier for the ticket, used for integrations with other systems

    `fields: str`
    :   Array of ticket field values including both system and custom fields

    `follower_ids: str`
    :   Array of user identifiers who are following the ticket for updates

    `followup_ids: str`
    :   Array of identifiers for follow-up tickets related to this ticket

    `forum_topic_id: str`
    :   Unique identifier linking the ticket to a forum topic if applicable

    `from_messaging_channel: str`
    :   Boolean indicating whether the ticket originated from a messaging channel

    `generated_timestamp: str`
    :   Timestamp updated for all ticket updates including system changes, used for incremental export

    `group_id: str`
    :   Unique identifier of the agent group assigned to handle the ticket

    `has_incidents: str`
    :   Boolean indicating whether this problem ticket has related incident tickets

    `id: str`
    :   Unique identifier for the ticket

    `is_public: str`
    :   Boolean indicating whether the ticket is publicly visible

    `organization_id: str`
    :   Unique identifier of the organization associated with the ticket

    `priority: str`
    :   Priority level assigned to the ticket (e.g., urgent, high, normal, low)

    `problem_id: str`
    :   Unique identifier of the problem ticket if this is an incident ticket

    `raw_subject: str`
    :   Original unprocessed subject line before any system modifications

    `recipient: str`
    :   Email address or identifier of the ticket recipient

    `requester_id: str`
    :   Unique identifier of the user who requested or created the ticket

    `result_type: str`
    :   The type of the search result (e.g. ticket) when returned from search endpoints

    `satisfaction_rating: str`
    :   Object containing customer satisfaction rating data for the ticket

    `sharing_agreement_ids: str`
    :   Array of sharing agreement identifiers if the ticket is shared across Zendesk instances

    `status: str`
    :   Current status of the ticket (e.g., new, open, pending, solved, closed)

    `subject: str`
    :   Subject line of the ticket describing the issue or request

    `submitter_id: str`
    :   Unique identifier of the user who submitted the ticket on behalf of the requester

    `tags: str`
    :   Array of tags applied to the ticket for categorization and filtering

    `ticket_form_id: str`
    :   Unique identifier of the ticket form used when creating the ticket

    `type_: str`
    :   Type of ticket (e.g., problem, incident, question, task)

    `updated_at: str`
    :   Timestamp indicating when the ticket was last updated with a ticket event

    `url: str`
    :   API URL to access the full ticket resource

    `via: str`
    :   Object describing the channel and method through which the ticket was created

<a id="TicketsUpdateParams"></a>

`TicketsUpdateParams(*args, **kwargs)`
:   Parameters for tickets.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ticket: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsUpdateParamsTicket`
    :   The type of the None singleton.

    `ticket_id: str`
    :   The type of the None singleton.

<a id="TicketsUpdateParamsTicket"></a>

`TicketsUpdateParamsTicket(*args, **kwargs)`
:   The ticket fields to update

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee_id: int`
    :   The type of the None singleton.

    `collaborator_ids: list[int]`
    :   The type of the None singleton.

    `comment: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsUpdateParamsTicketComment`
    :   The type of the None singleton.

    `custom_fields: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketsUpdateParamsTicketCustomFieldsItem]`
    :   The type of the None singleton.

    `due_at: str`
    :   The type of the None singleton.

    `external_id: str`
    :   The type of the None singleton.

    `group_id: int`
    :   The type of the None singleton.

    `priority: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `subject: str`
    :   The type of the None singleton.

    `tags: list[str]`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="TicketsUpdateParamsTicketComment"></a>

`TicketsUpdateParamsTicketComment(*args, **kwargs)`
:   A comment to add to the ticket

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: int`
    :   The type of the None singleton.

    `body: str`
    :   The type of the None singleton.

    `html_body: str`
    :   The type of the None singleton.

    `public: bool`
    :   The type of the None singleton.

<a id="TicketsUpdateParamsTicketCustomFieldsItem"></a>

`TicketsUpdateParamsTicketCustomFieldsItem(*args, **kwargs)`
:   Nested schema for TicketsUpdateParamsTicket.custom_fields_item

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: int`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

<a id="TriggersAndCondition"></a>

`TriggersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.TriggersEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersAnyCondition]`
    :   The type of the None singleton.

<a id="TriggersAnyCondition"></a>

`TriggersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.TriggersAnyValueFilter`
    :   The type of the None singleton.

<a id="TriggersAnyValueFilter"></a>

`TriggersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: Any`
    :   An array of actions

    `active: Any`
    :   Whether the trigger is active

    `category_id: Any`
    :   The ID of the category the trigger belongs to

    `conditions: Any`
    :   An object that describes the conditions under which the trigger will execute

    `created_at: Any`
    :   The time the trigger was created

    `description: Any`
    :   The description of the trigger

    `id: Any`
    :   Automatically assigned when created

    `position: Any`
    :   Position of the trigger

    `raw_title: Any`
    :   The dynamic content placeholder for title

    `title: Any`
    :   The title of the trigger

    `updated_at: Any`
    :   The time the trigger was last updated

    `url: Any`
    :   The URL of the trigger

<a id="TriggersContainsCondition"></a>

`TriggersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.TriggersAnyValueFilter`
    :   The type of the None singleton.

<a id="TriggersEqCondition"></a>

`TriggersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.TriggersSearchFilter`
    :   The type of the None singleton.

<a id="TriggersFuzzyCondition"></a>

`TriggersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.TriggersStringFilter`
    :   The type of the None singleton.

<a id="TriggersGetParams"></a>

`TriggersGetParams(*args, **kwargs)`
:   Parameters for triggers.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `trigger_id: str`
    :   The type of the None singleton.

<a id="TriggersGtCondition"></a>

`TriggersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.TriggersSearchFilter`
    :   The type of the None singleton.

<a id="TriggersGteCondition"></a>

`TriggersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.TriggersSearchFilter`
    :   The type of the None singleton.

<a id="TriggersInCondition"></a>

`TriggersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.TriggersInFilter`
    :   The type of the None singleton.

<a id="TriggersInFilter"></a>

`TriggersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: list[list[typing.Any]]`
    :   An array of actions

    `active: list[bool]`
    :   Whether the trigger is active

    `category_id: list[str]`
    :   The ID of the category the trigger belongs to

    `conditions: list[dict[str, typing.Any]]`
    :   An object that describes the conditions under which the trigger will execute

    `created_at: list[str]`
    :   The time the trigger was created

    `description: list[str]`
    :   The description of the trigger

    `id: list[int]`
    :   Automatically assigned when created

    `position: list[int]`
    :   Position of the trigger

    `raw_title: list[str]`
    :   The dynamic content placeholder for title

    `title: list[str]`
    :   The title of the trigger

    `updated_at: list[str]`
    :   The time the trigger was last updated

    `url: list[str]`
    :   The URL of the trigger

<a id="TriggersKeywordCondition"></a>

`TriggersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.TriggersStringFilter`
    :   The type of the None singleton.

<a id="TriggersLikeCondition"></a>

`TriggersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.TriggersStringFilter`
    :   The type of the None singleton.

<a id="TriggersListParams"></a>

`TriggersListParams(*args, **kwargs)`
:   Parameters for triggers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: bool`
    :   The type of the None singleton.

    `category_id: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.

<a id="TriggersLtCondition"></a>

`TriggersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.TriggersSearchFilter`
    :   The type of the None singleton.

<a id="TriggersLteCondition"></a>

`TriggersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.TriggersSearchFilter`
    :   The type of the None singleton.

<a id="TriggersNeqCondition"></a>

`TriggersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.TriggersSearchFilter`
    :   The type of the None singleton.

<a id="TriggersNotCondition"></a>

`TriggersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.TriggersEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersAnyCondition`
    :   The type of the None singleton.

<a id="TriggersOrCondition"></a>

`TriggersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.TriggersEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersAnyCondition]`
    :   The type of the None singleton.

<a id="TriggersSearchFilter"></a>

`TriggersSearchFilter(*args, **kwargs)`
:   Available fields for filtering triggers search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: list[typing.Any] | None`
    :   An array of actions

    `active: bool | None`
    :   Whether the trigger is active

    `category_id: str | None`
    :   The ID of the category the trigger belongs to

    `conditions: dict[str, typing.Any] | None`
    :   An object that describes the conditions under which the trigger will execute

    `created_at: str | None`
    :   The time the trigger was created

    `description: str | None`
    :   The description of the trigger

    `id: int | None`
    :   Automatically assigned when created

    `position: int | None`
    :   Position of the trigger

    `raw_title: str | None`
    :   The dynamic content placeholder for title

    `title: str | None`
    :   The title of the trigger

    `updated_at: str | None`
    :   The time the trigger was last updated

    `url: str | None`
    :   The URL of the trigger

<a id="TriggersSearchQuery"></a>

`TriggersSearchQuery(*args, **kwargs)`
:   Search query for triggers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.TriggersEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TriggersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.TriggersSortFilter]`
    :   The type of the None singleton.

<a id="TriggersSortFilter"></a>

`TriggersSortFilter(*args, **kwargs)`
:   Available fields for sorting triggers search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: Literal['asc', 'desc']`
    :   An array of actions

    `active: Literal['asc', 'desc']`
    :   Whether the trigger is active

    `category_id: Literal['asc', 'desc']`
    :   The ID of the category the trigger belongs to

    `conditions: Literal['asc', 'desc']`
    :   An object that describes the conditions under which the trigger will execute

    `created_at: Literal['asc', 'desc']`
    :   The time the trigger was created

    `description: Literal['asc', 'desc']`
    :   The description of the trigger

    `id: Literal['asc', 'desc']`
    :   Automatically assigned when created

    `position: Literal['asc', 'desc']`
    :   Position of the trigger

    `raw_title: Literal['asc', 'desc']`
    :   The dynamic content placeholder for title

    `title: Literal['asc', 'desc']`
    :   The title of the trigger

    `updated_at: Literal['asc', 'desc']`
    :   The time the trigger was last updated

    `url: Literal['asc', 'desc']`
    :   The URL of the trigger

<a id="TriggersStringFilter"></a>

`TriggersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `actions: str`
    :   An array of actions

    `active: str`
    :   Whether the trigger is active

    `category_id: str`
    :   The ID of the category the trigger belongs to

    `conditions: str`
    :   An object that describes the conditions under which the trigger will execute

    `created_at: str`
    :   The time the trigger was created

    `description: str`
    :   The description of the trigger

    `id: str`
    :   Automatically assigned when created

    `position: str`
    :   Position of the trigger

    `raw_title: str`
    :   The dynamic content placeholder for title

    `title: str`
    :   The title of the trigger

    `updated_at: str`
    :   The time the trigger was last updated

    `url: str`
    :   The URL of the trigger

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

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.UsersEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersAnyValueFilter"></a>

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Any`
    :   Indicates if the user account is currently active

    `alias: Any`
    :   Alternative name or nickname for the user

    `chat_only: Any`
    :   Indicates if the user can only interact via chat

    `created_at: Any`
    :   Timestamp indicating when the user was created

    `custom_role_id: Any`
    :   Identifier for a custom role assigned to the user

    `default_group_id: Any`
    :   Identifier of the default group assigned to the user

    `details: Any`
    :   Additional descriptive information about the user

    `email: Any`
    :   Email address of the user

    `external_id: Any`
    :   External system identifier for the user, used for integrations

    `iana_time_zone: Any`
    :   IANA standard time zone identifier for the user

    `id: Any`
    :   Unique identifier for the user

    `last_login_at: Any`
    :   Timestamp of the user's most recent login

    `locale: Any`
    :   Locale setting determining language and regional format preferences

    `locale_id: Any`
    :   Identifier for the user's locale preference

    `moderator: Any`
    :   Indicates if the user has moderator privileges

    `name: Any`
    :   Display name of the user

    `notes: Any`
    :   Internal notes about the user, visible only to agents

    `only_private_comments: Any`
    :   Indicates if the user can only make private comments on tickets

    `organization_id: Any`
    :   Identifier of the organization the user belongs to

    `permanently_deleted: Any`
    :   Indicates if the user has been permanently deleted from the system

    `phone: Any`
    :   Phone number of the user

    `photo: Any`
    :   Profile photo or avatar of the user

    `report_csv: Any`
    :   Indicates if the user receives reports in CSV format

    `restricted_agent: Any`
    :   Indicates if the agent has restricted access permissions

    `role: Any`
    :   Role assigned to the user defining their permissions level

    `role_type: Any`
    :   Type classification of the user's role

    `shared: Any`
    :   Indicates if the user is shared across multiple accounts

    `shared_agent: Any`
    :   Indicates if the user is a shared agent across multiple brands or accounts

    `shared_phone_number: Any`
    :   Indicates if the phone number is shared with other users

    `signature: Any`
    :   Email signature text for the user

    `suspended: Any`
    :   Indicates if the user account is suspended

    `tags: Any`
    :   Labels or tags associated with the user for categorization

    `ticket_restriction: Any`
    :   Defines which tickets the user can access based on restrictions

    `time_zone: Any`
    :   Time zone setting for the user

    `two_factor_auth_enabled: Any`
    :   Indicates if two-factor authentication is enabled for the user

    `updated_at: Any`
    :   Timestamp indicating when the user was last updated

    `url: Any`
    :   API endpoint URL for accessing the user's detailed information

    `user_fields: Any`
    :   Custom field values specific to the user, stored as key-value pairs

    `verified: Any`
    :   Indicates if the user's identity has been verified

<a id="UsersContainsCondition"></a>

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersCreateParams"></a>

`UsersCreateParams(*args, **kwargs)`
:   Parameters for users.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `user: airbyte_agent_sdk.connectors.zendesk_support.types.UsersCreateParamsUser`
    :   The type of the None singleton.

<a id="UsersCreateParamsUser"></a>

`UsersCreateParamsUser(*args, **kwargs)`
:   The user object to create

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `alias: str`
    :   The type of the None singleton.

    `details: str`
    :   The type of the None singleton.

    `email: str`
    :   The type of the None singleton.

    `external_id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `notes: str`
    :   The type of the None singleton.

    `organization_id: int`
    :   The type of the None singleton.

    `phone: str`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

    `tags: list[str]`
    :   The type of the None singleton.

    `user_fields: dict[str, typing.Any]`
    :   The type of the None singleton.

    `verified: bool`
    :   The type of the None singleton.

<a id="UsersEqCondition"></a>

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersFuzzyCondition"></a>

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersGetParams"></a>

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `user_id: str`
    :   The type of the None singleton.

<a id="UsersGtCondition"></a>

`UsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersGteCondition"></a>

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.UsersSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.UsersInFilter`
    :   The type of the None singleton.

<a id="UsersInFilter"></a>

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: list[bool]`
    :   Indicates if the user account is currently active

    `alias: list[str]`
    :   Alternative name or nickname for the user

    `chat_only: list[bool]`
    :   Indicates if the user can only interact via chat

    `created_at: list[str]`
    :   Timestamp indicating when the user was created

    `custom_role_id: list[int]`
    :   Identifier for a custom role assigned to the user

    `default_group_id: list[int]`
    :   Identifier of the default group assigned to the user

    `details: list[str]`
    :   Additional descriptive information about the user

    `email: list[str]`
    :   Email address of the user

    `external_id: list[str]`
    :   External system identifier for the user, used for integrations

    `iana_time_zone: list[str]`
    :   IANA standard time zone identifier for the user

    `id: list[int]`
    :   Unique identifier for the user

    `last_login_at: list[str]`
    :   Timestamp of the user's most recent login

    `locale: list[str]`
    :   Locale setting determining language and regional format preferences

    `locale_id: list[int]`
    :   Identifier for the user's locale preference

    `moderator: list[bool]`
    :   Indicates if the user has moderator privileges

    `name: list[str]`
    :   Display name of the user

    `notes: list[str]`
    :   Internal notes about the user, visible only to agents

    `only_private_comments: list[bool]`
    :   Indicates if the user can only make private comments on tickets

    `organization_id: list[int]`
    :   Identifier of the organization the user belongs to

    `permanently_deleted: list[bool]`
    :   Indicates if the user has been permanently deleted from the system

    `phone: list[str]`
    :   Phone number of the user

    `photo: list[dict[str, typing.Any]]`
    :   Profile photo or avatar of the user

    `report_csv: list[bool]`
    :   Indicates if the user receives reports in CSV format

    `restricted_agent: list[bool]`
    :   Indicates if the agent has restricted access permissions

    `role: list[str]`
    :   Role assigned to the user defining their permissions level

    `role_type: list[int]`
    :   Type classification of the user's role

    `shared: list[bool]`
    :   Indicates if the user is shared across multiple accounts

    `shared_agent: list[bool]`
    :   Indicates if the user is a shared agent across multiple brands or accounts

    `shared_phone_number: list[bool]`
    :   Indicates if the phone number is shared with other users

    `signature: list[str]`
    :   Email signature text for the user

    `suspended: list[bool]`
    :   Indicates if the user account is suspended

    `tags: list[list[typing.Any]]`
    :   Labels or tags associated with the user for categorization

    `ticket_restriction: list[str]`
    :   Defines which tickets the user can access based on restrictions

    `time_zone: list[str]`
    :   Time zone setting for the user

    `two_factor_auth_enabled: list[bool]`
    :   Indicates if two-factor authentication is enabled for the user

    `updated_at: list[str]`
    :   Timestamp indicating when the user was last updated

    `url: list[str]`
    :   API endpoint URL for accessing the user's detailed information

    `user_fields: list[dict[str, typing.Any]]`
    :   Custom field values specific to the user, stored as key-value pairs

    `verified: list[bool]`
    :   Indicates if the user's identity has been verified

<a id="UsersKeywordCondition"></a>

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersLikeCondition"></a>

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersListParams"></a>

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `external_id: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

<a id="UsersLtCondition"></a>

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersLteCondition"></a>

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNeqCondition"></a>

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.UsersSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.UsersEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.UsersEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersSearchFilter"></a>

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: bool | None`
    :   Indicates if the user account is currently active

    `alias: str | None`
    :   Alternative name or nickname for the user

    `chat_only: bool | None`
    :   Indicates if the user can only interact via chat

    `created_at: str | None`
    :   Timestamp indicating when the user was created

    `custom_role_id: int | None`
    :   Identifier for a custom role assigned to the user

    `default_group_id: int | None`
    :   Identifier of the default group assigned to the user

    `details: str | None`
    :   Additional descriptive information about the user

    `email: str | None`
    :   Email address of the user

    `external_id: str | None`
    :   External system identifier for the user, used for integrations

    `iana_time_zone: str | None`
    :   IANA standard time zone identifier for the user

    `id: int | None`
    :   Unique identifier for the user

    `last_login_at: str | None`
    :   Timestamp of the user's most recent login

    `locale: str | None`
    :   Locale setting determining language and regional format preferences

    `locale_id: int | None`
    :   Identifier for the user's locale preference

    `moderator: bool | None`
    :   Indicates if the user has moderator privileges

    `name: str | None`
    :   Display name of the user

    `notes: str | None`
    :   Internal notes about the user, visible only to agents

    `only_private_comments: bool | None`
    :   Indicates if the user can only make private comments on tickets

    `organization_id: int | None`
    :   Identifier of the organization the user belongs to

    `permanently_deleted: bool | None`
    :   Indicates if the user has been permanently deleted from the system

    `phone: str | None`
    :   Phone number of the user

    `photo: dict[str, typing.Any] | None`
    :   Profile photo or avatar of the user

    `report_csv: bool | None`
    :   Indicates if the user receives reports in CSV format

    `restricted_agent: bool | None`
    :   Indicates if the agent has restricted access permissions

    `role: str | None`
    :   Role assigned to the user defining their permissions level

    `role_type: int | None`
    :   Type classification of the user's role

    `shared: bool | None`
    :   Indicates if the user is shared across multiple accounts

    `shared_agent: bool | None`
    :   Indicates if the user is a shared agent across multiple brands or accounts

    `shared_phone_number: bool | None`
    :   Indicates if the phone number is shared with other users

    `signature: str | None`
    :   Email signature text for the user

    `suspended: bool | None`
    :   Indicates if the user account is suspended

    `tags: list[typing.Any] | None`
    :   Labels or tags associated with the user for categorization

    `ticket_restriction: str | None`
    :   Defines which tickets the user can access based on restrictions

    `time_zone: str | None`
    :   Time zone setting for the user

    `two_factor_auth_enabled: bool | None`
    :   Indicates if two-factor authentication is enabled for the user

    `updated_at: str | None`
    :   Timestamp indicating when the user was last updated

    `url: str | None`
    :   API endpoint URL for accessing the user's detailed information

    `user_fields: dict[str, typing.Any] | None`
    :   Custom field values specific to the user, stored as key-value pairs

    `verified: bool | None`
    :   Indicates if the user's identity has been verified

<a id="UsersSearchQuery"></a>

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.UsersEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.UsersSortFilter]`
    :   The type of the None singleton.

<a id="UsersSortFilter"></a>

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: Literal['asc', 'desc']`
    :   Indicates if the user account is currently active

    `alias: Literal['asc', 'desc']`
    :   Alternative name or nickname for the user

    `chat_only: Literal['asc', 'desc']`
    :   Indicates if the user can only interact via chat

    `created_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the user was created

    `custom_role_id: Literal['asc', 'desc']`
    :   Identifier for a custom role assigned to the user

    `default_group_id: Literal['asc', 'desc']`
    :   Identifier of the default group assigned to the user

    `details: Literal['asc', 'desc']`
    :   Additional descriptive information about the user

    `email: Literal['asc', 'desc']`
    :   Email address of the user

    `external_id: Literal['asc', 'desc']`
    :   External system identifier for the user, used for integrations

    `iana_time_zone: Literal['asc', 'desc']`
    :   IANA standard time zone identifier for the user

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the user

    `last_login_at: Literal['asc', 'desc']`
    :   Timestamp of the user's most recent login

    `locale: Literal['asc', 'desc']`
    :   Locale setting determining language and regional format preferences

    `locale_id: Literal['asc', 'desc']`
    :   Identifier for the user's locale preference

    `moderator: Literal['asc', 'desc']`
    :   Indicates if the user has moderator privileges

    `name: Literal['asc', 'desc']`
    :   Display name of the user

    `notes: Literal['asc', 'desc']`
    :   Internal notes about the user, visible only to agents

    `only_private_comments: Literal['asc', 'desc']`
    :   Indicates if the user can only make private comments on tickets

    `organization_id: Literal['asc', 'desc']`
    :   Identifier of the organization the user belongs to

    `permanently_deleted: Literal['asc', 'desc']`
    :   Indicates if the user has been permanently deleted from the system

    `phone: Literal['asc', 'desc']`
    :   Phone number of the user

    `photo: Literal['asc', 'desc']`
    :   Profile photo or avatar of the user

    `report_csv: Literal['asc', 'desc']`
    :   Indicates if the user receives reports in CSV format

    `restricted_agent: Literal['asc', 'desc']`
    :   Indicates if the agent has restricted access permissions

    `role: Literal['asc', 'desc']`
    :   Role assigned to the user defining their permissions level

    `role_type: Literal['asc', 'desc']`
    :   Type classification of the user's role

    `shared: Literal['asc', 'desc']`
    :   Indicates if the user is shared across multiple accounts

    `shared_agent: Literal['asc', 'desc']`
    :   Indicates if the user is a shared agent across multiple brands or accounts

    `shared_phone_number: Literal['asc', 'desc']`
    :   Indicates if the phone number is shared with other users

    `signature: Literal['asc', 'desc']`
    :   Email signature text for the user

    `suspended: Literal['asc', 'desc']`
    :   Indicates if the user account is suspended

    `tags: Literal['asc', 'desc']`
    :   Labels or tags associated with the user for categorization

    `ticket_restriction: Literal['asc', 'desc']`
    :   Defines which tickets the user can access based on restrictions

    `time_zone: Literal['asc', 'desc']`
    :   Time zone setting for the user

    `two_factor_auth_enabled: Literal['asc', 'desc']`
    :   Indicates if two-factor authentication is enabled for the user

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the user was last updated

    `url: Literal['asc', 'desc']`
    :   API endpoint URL for accessing the user's detailed information

    `user_fields: Literal['asc', 'desc']`
    :   Custom field values specific to the user, stored as key-value pairs

    `verified: Literal['asc', 'desc']`
    :   Indicates if the user's identity has been verified

<a id="UsersStringFilter"></a>

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: str`
    :   Indicates if the user account is currently active

    `alias: str`
    :   Alternative name or nickname for the user

    `chat_only: str`
    :   Indicates if the user can only interact via chat

    `created_at: str`
    :   Timestamp indicating when the user was created

    `custom_role_id: str`
    :   Identifier for a custom role assigned to the user

    `default_group_id: str`
    :   Identifier of the default group assigned to the user

    `details: str`
    :   Additional descriptive information about the user

    `email: str`
    :   Email address of the user

    `external_id: str`
    :   External system identifier for the user, used for integrations

    `iana_time_zone: str`
    :   IANA standard time zone identifier for the user

    `id: str`
    :   Unique identifier for the user

    `last_login_at: str`
    :   Timestamp of the user's most recent login

    `locale: str`
    :   Locale setting determining language and regional format preferences

    `locale_id: str`
    :   Identifier for the user's locale preference

    `moderator: str`
    :   Indicates if the user has moderator privileges

    `name: str`
    :   Display name of the user

    `notes: str`
    :   Internal notes about the user, visible only to agents

    `only_private_comments: str`
    :   Indicates if the user can only make private comments on tickets

    `organization_id: str`
    :   Identifier of the organization the user belongs to

    `permanently_deleted: str`
    :   Indicates if the user has been permanently deleted from the system

    `phone: str`
    :   Phone number of the user

    `photo: str`
    :   Profile photo or avatar of the user

    `report_csv: str`
    :   Indicates if the user receives reports in CSV format

    `restricted_agent: str`
    :   Indicates if the agent has restricted access permissions

    `role: str`
    :   Role assigned to the user defining their permissions level

    `role_type: str`
    :   Type classification of the user's role

    `shared: str`
    :   Indicates if the user is shared across multiple accounts

    `shared_agent: str`
    :   Indicates if the user is a shared agent across multiple brands or accounts

    `shared_phone_number: str`
    :   Indicates if the phone number is shared with other users

    `signature: str`
    :   Email signature text for the user

    `suspended: str`
    :   Indicates if the user account is suspended

    `tags: str`
    :   Labels or tags associated with the user for categorization

    `ticket_restriction: str`
    :   Defines which tickets the user can access based on restrictions

    `time_zone: str`
    :   Time zone setting for the user

    `two_factor_auth_enabled: str`
    :   Indicates if two-factor authentication is enabled for the user

    `updated_at: str`
    :   Timestamp indicating when the user was last updated

    `url: str`
    :   API endpoint URL for accessing the user's detailed information

    `user_fields: str`
    :   Custom field values specific to the user, stored as key-value pairs

    `verified: str`
    :   Indicates if the user's identity has been verified

<a id="UsersUpdateParams"></a>

`UsersUpdateParams(*args, **kwargs)`
:   Parameters for users.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `user: airbyte_agent_sdk.connectors.zendesk_support.types.UsersUpdateParamsUser`
    :   The type of the None singleton.

    `user_id: str`
    :   The type of the None singleton.

<a id="UsersUpdateParamsUser"></a>

`UsersUpdateParamsUser(*args, **kwargs)`
:   The user fields to update

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `alias: str`
    :   The type of the None singleton.

    `details: str`
    :   The type of the None singleton.

    `email: str`
    :   The type of the None singleton.

    `external_id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `notes: str`
    :   The type of the None singleton.

    `organization_id: int`
    :   The type of the None singleton.

    `phone: str`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

    `suspended: bool`
    :   The type of the None singleton.

    `tags: list[str]`
    :   The type of the None singleton.

    `user_fields: dict[str, typing.Any]`
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

    `access: str`
    :   The type of the None singleton.

    `active: bool`
    :   The type of the None singleton.

    `group_id: int`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

    `sort_by: str`
    :   The type of the None singleton.

    `sort_order: str`
    :   The type of the None singleton.