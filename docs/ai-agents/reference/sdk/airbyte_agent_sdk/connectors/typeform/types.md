---
id: airbyte_agent_sdk-connectors-typeform-types
title: airbyte_agent_sdk.connectors.typeform.types
---

Module airbyte_agent_sdk.connectors.typeform.types
==================================================
Type definitions for typeform connector.

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

`FormsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.typeform.types.FormsEqCondition | airbyte_agent_sdk.connectors.typeform.types.FormsNeqCondition | airbyte_agent_sdk.connectors.typeform.types.FormsGtCondition | airbyte_agent_sdk.connectors.typeform.types.FormsGteCondition | airbyte_agent_sdk.connectors.typeform.types.FormsLtCondition | airbyte_agent_sdk.connectors.typeform.types.FormsLteCondition | airbyte_agent_sdk.connectors.typeform.types.FormsInCondition | airbyte_agent_sdk.connectors.typeform.types.FormsLikeCondition | airbyte_agent_sdk.connectors.typeform.types.FormsFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.FormsKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.FormsContainsCondition | airbyte_agent_sdk.connectors.typeform.types.FormsNotCondition | airbyte_agent_sdk.connectors.typeform.types.FormsAndCondition | airbyte_agent_sdk.connectors.typeform.types.FormsOrCondition | airbyte_agent_sdk.connectors.typeform.types.FormsAnyCondition]`
    :   The type of the None singleton.

`FormsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.typeform.types.FormsAnyValueFilter`
    :   The type of the None singleton.

`FormsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   Date and time when the form was created

    `fields: Any`
    :   List of fields within the form

    `id: Any`
    :   Unique identifier of the form

    `last_updated_at: Any`
    :   Date and time when the form was last updated

    `links: Any`
    :   Links to related resources

    `logic: Any`
    :   Logic rules or conditions applied to the form fields

    `published_at: Any`
    :   Date and time when the form was published

    `settings: Any`
    :   Settings and configurations for the form

    `thankyou_screens: Any`
    :   Thank you screen configurations

    `theme: Any`
    :   Theme settings for the form

    `title: Any`
    :   Title of the form

    `type_: Any`
    :   Type of the form

    `welcome_screens: Any`
    :   Welcome screen configurations

    `workspace: Any`
    :   Workspace details where the form belongs

`FormsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.typeform.types.FormsAnyValueFilter`
    :   The type of the None singleton.

`FormsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.typeform.types.FormsSearchFilter`
    :   The type of the None singleton.

`FormsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.typeform.types.FormsStringFilter`
    :   The type of the None singleton.

`FormsGetParams(*args, **kwargs)`
:   Parameters for forms.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `form_id: str`
    :   The type of the None singleton.

`FormsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.typeform.types.FormsSearchFilter`
    :   The type of the None singleton.

`FormsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.typeform.types.FormsSearchFilter`
    :   The type of the None singleton.

`FormsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.typeform.types.FormsInFilter`
    :   The type of the None singleton.

`FormsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   Date and time when the form was created

    `fields: list[list[typing.Any]]`
    :   List of fields within the form

    `id: list[str]`
    :   Unique identifier of the form

    `last_updated_at: list[str]`
    :   Date and time when the form was last updated

    `links: list[dict[str, typing.Any]]`
    :   Links to related resources

    `logic: list[list[typing.Any]]`
    :   Logic rules or conditions applied to the form fields

    `published_at: list[str]`
    :   Date and time when the form was published

    `settings: list[dict[str, typing.Any]]`
    :   Settings and configurations for the form

    `thankyou_screens: list[list[typing.Any]]`
    :   Thank you screen configurations

    `theme: list[dict[str, typing.Any]]`
    :   Theme settings for the form

    `title: list[str]`
    :   Title of the form

    `type_: list[str]`
    :   Type of the form

    `welcome_screens: list[list[typing.Any]]`
    :   Welcome screen configurations

    `workspace: list[dict[str, typing.Any]]`
    :   Workspace details where the form belongs

`FormsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.typeform.types.FormsStringFilter`
    :   The type of the None singleton.

`FormsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.typeform.types.FormsStringFilter`
    :   The type of the None singleton.

`FormsListParams(*args, **kwargs)`
:   Parameters for forms.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`FormsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.typeform.types.FormsSearchFilter`
    :   The type of the None singleton.

`FormsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.typeform.types.FormsSearchFilter`
    :   The type of the None singleton.

`FormsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.typeform.types.FormsSearchFilter`
    :   The type of the None singleton.

`FormsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.typeform.types.FormsEqCondition | airbyte_agent_sdk.connectors.typeform.types.FormsNeqCondition | airbyte_agent_sdk.connectors.typeform.types.FormsGtCondition | airbyte_agent_sdk.connectors.typeform.types.FormsGteCondition | airbyte_agent_sdk.connectors.typeform.types.FormsLtCondition | airbyte_agent_sdk.connectors.typeform.types.FormsLteCondition | airbyte_agent_sdk.connectors.typeform.types.FormsInCondition | airbyte_agent_sdk.connectors.typeform.types.FormsLikeCondition | airbyte_agent_sdk.connectors.typeform.types.FormsFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.FormsKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.FormsContainsCondition | airbyte_agent_sdk.connectors.typeform.types.FormsNotCondition | airbyte_agent_sdk.connectors.typeform.types.FormsAndCondition | airbyte_agent_sdk.connectors.typeform.types.FormsOrCondition | airbyte_agent_sdk.connectors.typeform.types.FormsAnyCondition`
    :   The type of the None singleton.

`FormsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.typeform.types.FormsEqCondition | airbyte_agent_sdk.connectors.typeform.types.FormsNeqCondition | airbyte_agent_sdk.connectors.typeform.types.FormsGtCondition | airbyte_agent_sdk.connectors.typeform.types.FormsGteCondition | airbyte_agent_sdk.connectors.typeform.types.FormsLtCondition | airbyte_agent_sdk.connectors.typeform.types.FormsLteCondition | airbyte_agent_sdk.connectors.typeform.types.FormsInCondition | airbyte_agent_sdk.connectors.typeform.types.FormsLikeCondition | airbyte_agent_sdk.connectors.typeform.types.FormsFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.FormsKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.FormsContainsCondition | airbyte_agent_sdk.connectors.typeform.types.FormsNotCondition | airbyte_agent_sdk.connectors.typeform.types.FormsAndCondition | airbyte_agent_sdk.connectors.typeform.types.FormsOrCondition | airbyte_agent_sdk.connectors.typeform.types.FormsAnyCondition]`
    :   The type of the None singleton.

`FormsSearchFilter(*args, **kwargs)`
:   Available fields for filtering forms search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   Date and time when the form was created

    `fields: list[typing.Any] | None`
    :   List of fields within the form

    `id: str | None`
    :   Unique identifier of the form

    `last_updated_at: str | None`
    :   Date and time when the form was last updated

    `links: dict[str, typing.Any] | None`
    :   Links to related resources

    `logic: list[typing.Any] | None`
    :   Logic rules or conditions applied to the form fields

    `published_at: str | None`
    :   Date and time when the form was published

    `settings: dict[str, typing.Any] | None`
    :   Settings and configurations for the form

    `thankyou_screens: list[typing.Any] | None`
    :   Thank you screen configurations

    `theme: dict[str, typing.Any] | None`
    :   Theme settings for the form

    `title: str | None`
    :   Title of the form

    `type_: str | None`
    :   Type of the form

    `welcome_screens: list[typing.Any] | None`
    :   Welcome screen configurations

    `workspace: dict[str, typing.Any] | None`
    :   Workspace details where the form belongs

`FormsSearchQuery(*args, **kwargs)`
:   Search query for forms entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.typeform.types.FormsEqCondition | airbyte_agent_sdk.connectors.typeform.types.FormsNeqCondition | airbyte_agent_sdk.connectors.typeform.types.FormsGtCondition | airbyte_agent_sdk.connectors.typeform.types.FormsGteCondition | airbyte_agent_sdk.connectors.typeform.types.FormsLtCondition | airbyte_agent_sdk.connectors.typeform.types.FormsLteCondition | airbyte_agent_sdk.connectors.typeform.types.FormsInCondition | airbyte_agent_sdk.connectors.typeform.types.FormsLikeCondition | airbyte_agent_sdk.connectors.typeform.types.FormsFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.FormsKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.FormsContainsCondition | airbyte_agent_sdk.connectors.typeform.types.FormsNotCondition | airbyte_agent_sdk.connectors.typeform.types.FormsAndCondition | airbyte_agent_sdk.connectors.typeform.types.FormsOrCondition | airbyte_agent_sdk.connectors.typeform.types.FormsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.typeform.types.FormsSortFilter]`
    :   The type of the None singleton.

`FormsSortFilter(*args, **kwargs)`
:   Available fields for sorting forms search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   Date and time when the form was created

    `fields: Literal['asc', 'desc']`
    :   List of fields within the form

    `id: Literal['asc', 'desc']`
    :   Unique identifier of the form

    `last_updated_at: Literal['asc', 'desc']`
    :   Date and time when the form was last updated

    `links: Literal['asc', 'desc']`
    :   Links to related resources

    `logic: Literal['asc', 'desc']`
    :   Logic rules or conditions applied to the form fields

    `published_at: Literal['asc', 'desc']`
    :   Date and time when the form was published

    `settings: Literal['asc', 'desc']`
    :   Settings and configurations for the form

    `thankyou_screens: Literal['asc', 'desc']`
    :   Thank you screen configurations

    `theme: Literal['asc', 'desc']`
    :   Theme settings for the form

    `title: Literal['asc', 'desc']`
    :   Title of the form

    `type_: Literal['asc', 'desc']`
    :   Type of the form

    `welcome_screens: Literal['asc', 'desc']`
    :   Welcome screen configurations

    `workspace: Literal['asc', 'desc']`
    :   Workspace details where the form belongs

`FormsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   Date and time when the form was created

    `fields: str`
    :   List of fields within the form

    `id: str`
    :   Unique identifier of the form

    `last_updated_at: str`
    :   Date and time when the form was last updated

    `links: str`
    :   Links to related resources

    `logic: str`
    :   Logic rules or conditions applied to the form fields

    `published_at: str`
    :   Date and time when the form was published

    `settings: str`
    :   Settings and configurations for the form

    `thankyou_screens: str`
    :   Thank you screen configurations

    `theme: str`
    :   Theme settings for the form

    `title: str`
    :   Title of the form

    `type_: str`
    :   Type of the form

    `welcome_screens: str`
    :   Welcome screen configurations

    `workspace: str`
    :   Workspace details where the form belongs

`ImagesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.typeform.types.ImagesEqCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesGtCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesGteCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesLtCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesLteCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesInCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesNotCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesAndCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesOrCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesAnyCondition]`
    :   The type of the None singleton.

`ImagesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.typeform.types.ImagesAnyValueFilter`
    :   The type of the None singleton.

`ImagesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avg_color: Any`
    :   Average color of the image

    `file_name: Any`
    :   Name of the image file

    `has_alpha: Any`
    :   Whether the image has an alpha channel

    `height: Any`
    :   Height of the image in pixels

    `id: Any`
    :   Unique identifier of the image

    `media_type: Any`
    :   MIME type of the image

    `src: Any`
    :   URL to access the image

    `width: Any`
    :   Width of the image in pixels

`ImagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.typeform.types.ImagesAnyValueFilter`
    :   The type of the None singleton.

`ImagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.typeform.types.ImagesSearchFilter`
    :   The type of the None singleton.

`ImagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.typeform.types.ImagesStringFilter`
    :   The type of the None singleton.

`ImagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.typeform.types.ImagesSearchFilter`
    :   The type of the None singleton.

`ImagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.typeform.types.ImagesSearchFilter`
    :   The type of the None singleton.

`ImagesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.typeform.types.ImagesInFilter`
    :   The type of the None singleton.

`ImagesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avg_color: list[str]`
    :   Average color of the image

    `file_name: list[str]`
    :   Name of the image file

    `has_alpha: list[bool]`
    :   Whether the image has an alpha channel

    `height: list[int]`
    :   Height of the image in pixels

    `id: list[str]`
    :   Unique identifier of the image

    `media_type: list[str]`
    :   MIME type of the image

    `src: list[str]`
    :   URL to access the image

    `width: list[int]`
    :   Width of the image in pixels

`ImagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.typeform.types.ImagesStringFilter`
    :   The type of the None singleton.

`ImagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.typeform.types.ImagesStringFilter`
    :   The type of the None singleton.

`ImagesListParams(*args, **kwargs)`
:   Parameters for images.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`ImagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.typeform.types.ImagesSearchFilter`
    :   The type of the None singleton.

`ImagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.typeform.types.ImagesSearchFilter`
    :   The type of the None singleton.

`ImagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.typeform.types.ImagesSearchFilter`
    :   The type of the None singleton.

`ImagesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.typeform.types.ImagesEqCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesGtCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesGteCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesLtCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesLteCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesInCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesNotCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesAndCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesOrCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesAnyCondition`
    :   The type of the None singleton.

`ImagesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.typeform.types.ImagesEqCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesGtCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesGteCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesLtCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesLteCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesInCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesNotCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesAndCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesOrCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesAnyCondition]`
    :   The type of the None singleton.

`ImagesSearchFilter(*args, **kwargs)`
:   Available fields for filtering images search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avg_color: str | None`
    :   Average color of the image

    `file_name: str | None`
    :   Name of the image file

    `has_alpha: bool | None`
    :   Whether the image has an alpha channel

    `height: int | None`
    :   Height of the image in pixels

    `id: str | None`
    :   Unique identifier of the image

    `media_type: str | None`
    :   MIME type of the image

    `src: str | None`
    :   URL to access the image

    `width: int | None`
    :   Width of the image in pixels

`ImagesSearchQuery(*args, **kwargs)`
:   Search query for images entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.typeform.types.ImagesEqCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesGtCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesGteCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesLtCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesLteCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesInCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesNotCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesAndCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesOrCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.typeform.types.ImagesSortFilter]`
    :   The type of the None singleton.

`ImagesSortFilter(*args, **kwargs)`
:   Available fields for sorting images search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avg_color: Literal['asc', 'desc']`
    :   Average color of the image

    `file_name: Literal['asc', 'desc']`
    :   Name of the image file

    `has_alpha: Literal['asc', 'desc']`
    :   Whether the image has an alpha channel

    `height: Literal['asc', 'desc']`
    :   Height of the image in pixels

    `id: Literal['asc', 'desc']`
    :   Unique identifier of the image

    `media_type: Literal['asc', 'desc']`
    :   MIME type of the image

    `src: Literal['asc', 'desc']`
    :   URL to access the image

    `width: Literal['asc', 'desc']`
    :   Width of the image in pixels

`ImagesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avg_color: str`
    :   Average color of the image

    `file_name: str`
    :   Name of the image file

    `has_alpha: str`
    :   Whether the image has an alpha channel

    `height: str`
    :   Height of the image in pixels

    `id: str`
    :   Unique identifier of the image

    `media_type: str`
    :   MIME type of the image

    `src: str`
    :   URL to access the image

    `width: str`
    :   Width of the image in pixels

`ResponsesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.typeform.types.ResponsesEqCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesGtCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesGteCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesLtCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesLteCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesInCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesNotCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesAndCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesOrCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesAnyCondition]`
    :   The type of the None singleton.

`ResponsesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.typeform.types.ResponsesAnyValueFilter`
    :   The type of the None singleton.

`ResponsesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `answers: Any`
    :   Response data for each question in the form

    `calculated: Any`
    :   Calculated data related to the response

    `form_id: Any`
    :   ID of the form

    `hidden: Any`
    :   Hidden fields in the response

    `landed_at: Any`
    :   Timestamp when the respondent landed on the form

    `landing_id: Any`
    :   ID of the landing page

    `metadata: Any`
    :   Metadata related to the response

    `response_id: Any`
    :   ID of the response

    `response_type: Any`
    :   Type of the response

    `submitted_at: Any`
    :   Timestamp when the response was submitted

    `token: Any`
    :   Token associated with the response

    `variables: Any`
    :   Variables associated with the response

`ResponsesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.typeform.types.ResponsesAnyValueFilter`
    :   The type of the None singleton.

`ResponsesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.typeform.types.ResponsesSearchFilter`
    :   The type of the None singleton.

`ResponsesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.typeform.types.ResponsesStringFilter`
    :   The type of the None singleton.

`ResponsesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.typeform.types.ResponsesSearchFilter`
    :   The type of the None singleton.

`ResponsesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.typeform.types.ResponsesSearchFilter`
    :   The type of the None singleton.

`ResponsesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.typeform.types.ResponsesInFilter`
    :   The type of the None singleton.

`ResponsesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `answers: list[list[typing.Any]]`
    :   Response data for each question in the form

    `calculated: list[dict[str, typing.Any]]`
    :   Calculated data related to the response

    `form_id: list[str]`
    :   ID of the form

    `hidden: list[dict[str, typing.Any]]`
    :   Hidden fields in the response

    `landed_at: list[str]`
    :   Timestamp when the respondent landed on the form

    `landing_id: list[str]`
    :   ID of the landing page

    `metadata: list[dict[str, typing.Any]]`
    :   Metadata related to the response

    `response_id: list[str]`
    :   ID of the response

    `response_type: list[str]`
    :   Type of the response

    `submitted_at: list[str]`
    :   Timestamp when the response was submitted

    `token: list[str]`
    :   Token associated with the response

    `variables: list[list[typing.Any]]`
    :   Variables associated with the response

`ResponsesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.typeform.types.ResponsesStringFilter`
    :   The type of the None singleton.

`ResponsesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.typeform.types.ResponsesStringFilter`
    :   The type of the None singleton.

`ResponsesListParams(*args, **kwargs)`
:   Parameters for responses.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `before: str`
    :   The type of the None singleton.

    `completed: bool`
    :   The type of the None singleton.

    `form_id: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

    `since: str`
    :   The type of the None singleton.

    `sort: str`
    :   The type of the None singleton.

    `until: str`
    :   The type of the None singleton.

`ResponsesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.typeform.types.ResponsesSearchFilter`
    :   The type of the None singleton.

`ResponsesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.typeform.types.ResponsesSearchFilter`
    :   The type of the None singleton.

`ResponsesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.typeform.types.ResponsesSearchFilter`
    :   The type of the None singleton.

`ResponsesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.typeform.types.ResponsesEqCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesGtCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesGteCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesLtCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesLteCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesInCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesNotCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesAndCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesOrCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesAnyCondition`
    :   The type of the None singleton.

`ResponsesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.typeform.types.ResponsesEqCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesGtCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesGteCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesLtCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesLteCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesInCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesNotCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesAndCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesOrCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesAnyCondition]`
    :   The type of the None singleton.

`ResponsesSearchFilter(*args, **kwargs)`
:   Available fields for filtering responses search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `answers: list[typing.Any] | None`
    :   Response data for each question in the form

    `calculated: dict[str, typing.Any] | None`
    :   Calculated data related to the response

    `form_id: str | None`
    :   ID of the form

    `hidden: dict[str, typing.Any] | None`
    :   Hidden fields in the response

    `landed_at: str | None`
    :   Timestamp when the respondent landed on the form

    `landing_id: str | None`
    :   ID of the landing page

    `metadata: dict[str, typing.Any] | None`
    :   Metadata related to the response

    `response_id: str | None`
    :   ID of the response

    `response_type: str | None`
    :   Type of the response

    `submitted_at: str | None`
    :   Timestamp when the response was submitted

    `token: str | None`
    :   Token associated with the response

    `variables: list[typing.Any] | None`
    :   Variables associated with the response

`ResponsesSearchQuery(*args, **kwargs)`
:   Search query for responses entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.typeform.types.ResponsesEqCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesGtCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesGteCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesLtCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesLteCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesInCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesNotCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesAndCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesOrCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.typeform.types.ResponsesSortFilter]`
    :   The type of the None singleton.

`ResponsesSortFilter(*args, **kwargs)`
:   Available fields for sorting responses search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `answers: Literal['asc', 'desc']`
    :   Response data for each question in the form

    `calculated: Literal['asc', 'desc']`
    :   Calculated data related to the response

    `form_id: Literal['asc', 'desc']`
    :   ID of the form

    `hidden: Literal['asc', 'desc']`
    :   Hidden fields in the response

    `landed_at: Literal['asc', 'desc']`
    :   Timestamp when the respondent landed on the form

    `landing_id: Literal['asc', 'desc']`
    :   ID of the landing page

    `metadata: Literal['asc', 'desc']`
    :   Metadata related to the response

    `response_id: Literal['asc', 'desc']`
    :   ID of the response

    `response_type: Literal['asc', 'desc']`
    :   Type of the response

    `submitted_at: Literal['asc', 'desc']`
    :   Timestamp when the response was submitted

    `token: Literal['asc', 'desc']`
    :   Token associated with the response

    `variables: Literal['asc', 'desc']`
    :   Variables associated with the response

`ResponsesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `answers: str`
    :   Response data for each question in the form

    `calculated: str`
    :   Calculated data related to the response

    `form_id: str`
    :   ID of the form

    `hidden: str`
    :   Hidden fields in the response

    `landed_at: str`
    :   Timestamp when the respondent landed on the form

    `landing_id: str`
    :   ID of the landing page

    `metadata: str`
    :   Metadata related to the response

    `response_id: str`
    :   ID of the response

    `response_type: str`
    :   Type of the response

    `submitted_at: str`
    :   Timestamp when the response was submitted

    `token: str`
    :   Token associated with the response

    `variables: str`
    :   Variables associated with the response

`ThemesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.typeform.types.ThemesEqCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesGtCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesGteCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesLtCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesLteCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesInCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesNotCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesAndCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesOrCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesAnyCondition]`
    :   The type of the None singleton.

`ThemesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.typeform.types.ThemesAnyValueFilter`
    :   The type of the None singleton.

`ThemesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `background: Any`
    :   Background settings for the theme

    `colors: Any`
    :   Color settings

    `created_at: Any`
    :   Timestamp when the theme was created

    `fields: Any`
    :   Field display settings

    `font: Any`
    :   Font used in the theme

    `has_transparent_button: Any`
    :   Whether the theme has a transparent button

    `id: Any`
    :   Unique identifier of the theme

    `name: Any`
    :   Name of the theme

    `rounded_corners: Any`
    :   Rounded corners setting

    `screens: Any`
    :   Screen display settings

    `updated_at: Any`
    :   Timestamp when the theme was last updated

    `visibility: Any`
    :   Visibility setting of the theme

`ThemesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.typeform.types.ThemesAnyValueFilter`
    :   The type of the None singleton.

`ThemesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.typeform.types.ThemesSearchFilter`
    :   The type of the None singleton.

`ThemesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.typeform.types.ThemesStringFilter`
    :   The type of the None singleton.

`ThemesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.typeform.types.ThemesSearchFilter`
    :   The type of the None singleton.

`ThemesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.typeform.types.ThemesSearchFilter`
    :   The type of the None singleton.

`ThemesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.typeform.types.ThemesInFilter`
    :   The type of the None singleton.

`ThemesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `background: list[dict[str, typing.Any]]`
    :   Background settings for the theme

    `colors: list[dict[str, typing.Any]]`
    :   Color settings

    `created_at: list[str]`
    :   Timestamp when the theme was created

    `fields: list[dict[str, typing.Any]]`
    :   Field display settings

    `font: list[str]`
    :   Font used in the theme

    `has_transparent_button: list[bool]`
    :   Whether the theme has a transparent button

    `id: list[str]`
    :   Unique identifier of the theme

    `name: list[str]`
    :   Name of the theme

    `rounded_corners: list[str]`
    :   Rounded corners setting

    `screens: list[dict[str, typing.Any]]`
    :   Screen display settings

    `updated_at: list[str]`
    :   Timestamp when the theme was last updated

    `visibility: list[str]`
    :   Visibility setting of the theme

`ThemesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.typeform.types.ThemesStringFilter`
    :   The type of the None singleton.

`ThemesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.typeform.types.ThemesStringFilter`
    :   The type of the None singleton.

`ThemesListParams(*args, **kwargs)`
:   Parameters for themes.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`ThemesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.typeform.types.ThemesSearchFilter`
    :   The type of the None singleton.

`ThemesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.typeform.types.ThemesSearchFilter`
    :   The type of the None singleton.

`ThemesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.typeform.types.ThemesSearchFilter`
    :   The type of the None singleton.

`ThemesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.typeform.types.ThemesEqCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesGtCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesGteCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesLtCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesLteCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesInCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesNotCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesAndCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesOrCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesAnyCondition`
    :   The type of the None singleton.

`ThemesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.typeform.types.ThemesEqCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesGtCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesGteCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesLtCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesLteCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesInCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesNotCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesAndCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesOrCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesAnyCondition]`
    :   The type of the None singleton.

`ThemesSearchFilter(*args, **kwargs)`
:   Available fields for filtering themes search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `background: dict[str, typing.Any] | None`
    :   Background settings for the theme

    `colors: dict[str, typing.Any] | None`
    :   Color settings

    `created_at: str | None`
    :   Timestamp when the theme was created

    `fields: dict[str, typing.Any] | None`
    :   Field display settings

    `font: str | None`
    :   Font used in the theme

    `has_transparent_button: bool | None`
    :   Whether the theme has a transparent button

    `id: str | None`
    :   Unique identifier of the theme

    `name: str | None`
    :   Name of the theme

    `rounded_corners: str | None`
    :   Rounded corners setting

    `screens: dict[str, typing.Any] | None`
    :   Screen display settings

    `updated_at: str | None`
    :   Timestamp when the theme was last updated

    `visibility: str | None`
    :   Visibility setting of the theme

`ThemesSearchQuery(*args, **kwargs)`
:   Search query for themes entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.typeform.types.ThemesEqCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesGtCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesGteCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesLtCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesLteCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesInCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesNotCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesAndCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesOrCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.typeform.types.ThemesSortFilter]`
    :   The type of the None singleton.

`ThemesSortFilter(*args, **kwargs)`
:   Available fields for sorting themes search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `background: Literal['asc', 'desc']`
    :   Background settings for the theme

    `colors: Literal['asc', 'desc']`
    :   Color settings

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the theme was created

    `fields: Literal['asc', 'desc']`
    :   Field display settings

    `font: Literal['asc', 'desc']`
    :   Font used in the theme

    `has_transparent_button: Literal['asc', 'desc']`
    :   Whether the theme has a transparent button

    `id: Literal['asc', 'desc']`
    :   Unique identifier of the theme

    `name: Literal['asc', 'desc']`
    :   Name of the theme

    `rounded_corners: Literal['asc', 'desc']`
    :   Rounded corners setting

    `screens: Literal['asc', 'desc']`
    :   Screen display settings

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the theme was last updated

    `visibility: Literal['asc', 'desc']`
    :   Visibility setting of the theme

`ThemesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `background: str`
    :   Background settings for the theme

    `colors: str`
    :   Color settings

    `created_at: str`
    :   Timestamp when the theme was created

    `fields: str`
    :   Field display settings

    `font: str`
    :   Font used in the theme

    `has_transparent_button: str`
    :   Whether the theme has a transparent button

    `id: str`
    :   Unique identifier of the theme

    `name: str`
    :   Name of the theme

    `rounded_corners: str`
    :   Rounded corners setting

    `screens: str`
    :   Screen display settings

    `updated_at: str`
    :   Timestamp when the theme was last updated

    `visibility: str`
    :   Visibility setting of the theme

`WebhooksAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.typeform.types.WebhooksEqCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksNeqCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksGtCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksGteCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksLtCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksLteCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksInCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksLikeCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksContainsCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksNotCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksAndCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksOrCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksAnyCondition]`
    :   The type of the None singleton.

`WebhooksAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.typeform.types.WebhooksAnyValueFilter`
    :   The type of the None singleton.

`WebhooksAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   Timestamp when the webhook was created

    `enabled: Any`
    :   Whether the webhook is currently enabled

    `form_id: Any`
    :   ID of the form associated with the webhook

    `id: Any`
    :   Unique identifier of the webhook

    `tag: Any`
    :   Tag to categorize or label the webhook

    `updated_at: Any`
    :   Timestamp when the webhook was last updated

    `url: Any`
    :   URL where webhook data is sent

    `verify_ssl: Any`
    :   Whether SSL verification is enforced

`WebhooksContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.typeform.types.WebhooksAnyValueFilter`
    :   The type of the None singleton.

`WebhooksEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.typeform.types.WebhooksSearchFilter`
    :   The type of the None singleton.

`WebhooksFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.typeform.types.WebhooksStringFilter`
    :   The type of the None singleton.

`WebhooksGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.typeform.types.WebhooksSearchFilter`
    :   The type of the None singleton.

`WebhooksGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.typeform.types.WebhooksSearchFilter`
    :   The type of the None singleton.

`WebhooksInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.typeform.types.WebhooksInFilter`
    :   The type of the None singleton.

`WebhooksInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   Timestamp when the webhook was created

    `enabled: list[bool]`
    :   Whether the webhook is currently enabled

    `form_id: list[str]`
    :   ID of the form associated with the webhook

    `id: list[str]`
    :   Unique identifier of the webhook

    `tag: list[str]`
    :   Tag to categorize or label the webhook

    `updated_at: list[str]`
    :   Timestamp when the webhook was last updated

    `url: list[str]`
    :   URL where webhook data is sent

    `verify_ssl: list[bool]`
    :   Whether SSL verification is enforced

`WebhooksKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.typeform.types.WebhooksStringFilter`
    :   The type of the None singleton.

`WebhooksLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.typeform.types.WebhooksStringFilter`
    :   The type of the None singleton.

`WebhooksListParams(*args, **kwargs)`
:   Parameters for webhooks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `form_id: str`
    :   The type of the None singleton.

`WebhooksLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.typeform.types.WebhooksSearchFilter`
    :   The type of the None singleton.

`WebhooksLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.typeform.types.WebhooksSearchFilter`
    :   The type of the None singleton.

`WebhooksNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.typeform.types.WebhooksSearchFilter`
    :   The type of the None singleton.

`WebhooksNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.typeform.types.WebhooksEqCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksNeqCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksGtCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksGteCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksLtCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksLteCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksInCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksLikeCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksContainsCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksNotCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksAndCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksOrCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksAnyCondition`
    :   The type of the None singleton.

`WebhooksOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.typeform.types.WebhooksEqCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksNeqCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksGtCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksGteCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksLtCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksLteCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksInCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksLikeCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksContainsCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksNotCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksAndCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksOrCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksAnyCondition]`
    :   The type of the None singleton.

`WebhooksSearchFilter(*args, **kwargs)`
:   Available fields for filtering webhooks search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the webhook was created

    `enabled: bool | None`
    :   Whether the webhook is currently enabled

    `form_id: str | None`
    :   ID of the form associated with the webhook

    `id: str | None`
    :   Unique identifier of the webhook

    `tag: str | None`
    :   Tag to categorize or label the webhook

    `updated_at: str | None`
    :   Timestamp when the webhook was last updated

    `url: str | None`
    :   URL where webhook data is sent

    `verify_ssl: bool | None`
    :   Whether SSL verification is enforced

`WebhooksSearchQuery(*args, **kwargs)`
:   Search query for webhooks entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.typeform.types.WebhooksEqCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksNeqCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksGtCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksGteCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksLtCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksLteCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksInCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksLikeCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksContainsCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksNotCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksAndCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksOrCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.typeform.types.WebhooksSortFilter]`
    :   The type of the None singleton.

`WebhooksSortFilter(*args, **kwargs)`
:   Available fields for sorting webhooks search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the webhook was created

    `enabled: Literal['asc', 'desc']`
    :   Whether the webhook is currently enabled

    `form_id: Literal['asc', 'desc']`
    :   ID of the form associated with the webhook

    `id: Literal['asc', 'desc']`
    :   Unique identifier of the webhook

    `tag: Literal['asc', 'desc']`
    :   Tag to categorize or label the webhook

    `updated_at: Literal['asc', 'desc']`
    :   Timestamp when the webhook was last updated

    `url: Literal['asc', 'desc']`
    :   URL where webhook data is sent

    `verify_ssl: Literal['asc', 'desc']`
    :   Whether SSL verification is enforced

`WebhooksStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   Timestamp when the webhook was created

    `enabled: str`
    :   Whether the webhook is currently enabled

    `form_id: str`
    :   ID of the form associated with the webhook

    `id: str`
    :   Unique identifier of the webhook

    `tag: str`
    :   Tag to categorize or label the webhook

    `updated_at: str`
    :   Timestamp when the webhook was last updated

    `url: str`
    :   URL where webhook data is sent

    `verify_ssl: str`
    :   Whether SSL verification is enforced

`WorkspacesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.typeform.types.WorkspacesEqCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesGtCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesGteCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesLtCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesLteCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesInCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesNotCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesAndCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesOrCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesAnyCondition]`
    :   The type of the None singleton.

`WorkspacesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.typeform.types.WorkspacesAnyValueFilter`
    :   The type of the None singleton.

`WorkspacesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Any`
    :   Account ID associated with the workspace

    `default: Any`
    :   Whether this is the default workspace

    `forms: Any`
    :   Information about forms in the workspace

    `id: Any`
    :   Unique identifier of the workspace

    `name: Any`
    :   Name of the workspace

    `self: Any`
    :   Self-referential link

    `shared: Any`
    :   Whether this workspace is shared

`WorkspacesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.typeform.types.WorkspacesAnyValueFilter`
    :   The type of the None singleton.

`WorkspacesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.typeform.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.typeform.types.WorkspacesStringFilter`
    :   The type of the None singleton.

`WorkspacesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.typeform.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.typeform.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.typeform.types.WorkspacesInFilter`
    :   The type of the None singleton.

`WorkspacesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: list[str]`
    :   Account ID associated with the workspace

    `default: list[bool]`
    :   Whether this is the default workspace

    `forms: list[dict[str, typing.Any]]`
    :   Information about forms in the workspace

    `id: list[str]`
    :   Unique identifier of the workspace

    `name: list[str]`
    :   Name of the workspace

    `self: list[dict[str, typing.Any]]`
    :   Self-referential link

    `shared: list[bool]`
    :   Whether this workspace is shared

`WorkspacesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.typeform.types.WorkspacesStringFilter`
    :   The type of the None singleton.

`WorkspacesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.typeform.types.WorkspacesStringFilter`
    :   The type of the None singleton.

`WorkspacesListParams(*args, **kwargs)`
:   Parameters for workspaces.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

`WorkspacesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.typeform.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.typeform.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.typeform.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

`WorkspacesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.typeform.types.WorkspacesEqCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesGtCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesGteCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesLtCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesLteCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesInCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesNotCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesAndCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesOrCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesAnyCondition`
    :   The type of the None singleton.

`WorkspacesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.typeform.types.WorkspacesEqCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesGtCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesGteCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesLtCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesLteCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesInCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesNotCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesAndCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesOrCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesAnyCondition]`
    :   The type of the None singleton.

`WorkspacesSearchFilter(*args, **kwargs)`
:   Available fields for filtering workspaces search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str | None`
    :   Account ID associated with the workspace

    `default: bool | None`
    :   Whether this is the default workspace

    `forms: dict[str, typing.Any] | None`
    :   Information about forms in the workspace

    `id: str | None`
    :   Unique identifier of the workspace

    `name: str | None`
    :   Name of the workspace

    `self: dict[str, typing.Any] | None`
    :   Self-referential link

    `shared: bool | None`
    :   Whether this workspace is shared

`WorkspacesSearchQuery(*args, **kwargs)`
:   Search query for workspaces entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.typeform.types.WorkspacesEqCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesGtCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesGteCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesLtCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesLteCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesInCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesNotCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesAndCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesOrCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.typeform.types.WorkspacesSortFilter]`
    :   The type of the None singleton.

`WorkspacesSortFilter(*args, **kwargs)`
:   Available fields for sorting workspaces search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Literal['asc', 'desc']`
    :   Account ID associated with the workspace

    `default: Literal['asc', 'desc']`
    :   Whether this is the default workspace

    `forms: Literal['asc', 'desc']`
    :   Information about forms in the workspace

    `id: Literal['asc', 'desc']`
    :   Unique identifier of the workspace

    `name: Literal['asc', 'desc']`
    :   Name of the workspace

    `self: Literal['asc', 'desc']`
    :   Self-referential link

    `shared: Literal['asc', 'desc']`
    :   Whether this workspace is shared

`WorkspacesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   Account ID associated with the workspace

    `default: str`
    :   Whether this is the default workspace

    `forms: str`
    :   Information about forms in the workspace

    `id: str`
    :   Unique identifier of the workspace

    `name: str`
    :   Name of the workspace

    `self: str`
    :   Self-referential link

    `shared: str`
    :   Whether this workspace is shared