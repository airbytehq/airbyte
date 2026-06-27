---
id: airbyte_agent_sdk-connectors-typeform-types
title: airbyte_agent_sdk.connectors.typeform.types
---

Module airbyte_agent_sdk.connectors.typeform.types
==================================================
Type definitions for typeform connector.

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

<a id="FormsAndCondition"></a>

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

<a id="FormsAnyCondition"></a>

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

<a id="FormsAnyValueFilter"></a>

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

<a id="FormsContainsCondition"></a>

`FormsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.typeform.types.FormsAnyValueFilter`
    :   The type of the None singleton.

<a id="FormsEqCondition"></a>

`FormsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.typeform.types.FormsSearchFilter`
    :   The type of the None singleton.

<a id="FormsFuzzyCondition"></a>

`FormsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.typeform.types.FormsStringFilter`
    :   The type of the None singleton.

<a id="FormsGetParams"></a>

`FormsGetParams(*args, **kwargs)`
:   Parameters for forms.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `form_id: str`
    :   The type of the None singleton.

<a id="FormsGtCondition"></a>

`FormsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.typeform.types.FormsSearchFilter`
    :   The type of the None singleton.

<a id="FormsGteCondition"></a>

`FormsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.typeform.types.FormsSearchFilter`
    :   The type of the None singleton.

<a id="FormsInCondition"></a>

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

<a id="FormsInFilter"></a>

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

<a id="FormsKeywordCondition"></a>

`FormsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.typeform.types.FormsStringFilter`
    :   The type of the None singleton.

<a id="FormsLikeCondition"></a>

`FormsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.typeform.types.FormsStringFilter`
    :   The type of the None singleton.

<a id="FormsListParams"></a>

`FormsListParams(*args, **kwargs)`
:   Parameters for forms.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="FormsLtCondition"></a>

`FormsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.typeform.types.FormsSearchFilter`
    :   The type of the None singleton.

<a id="FormsLteCondition"></a>

`FormsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.typeform.types.FormsSearchFilter`
    :   The type of the None singleton.

<a id="FormsNeqCondition"></a>

`FormsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.typeform.types.FormsSearchFilter`
    :   The type of the None singleton.

<a id="FormsNotCondition"></a>

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

<a id="FormsOrCondition"></a>

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

<a id="FormsSearchFilter"></a>

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

<a id="FormsSearchQuery"></a>

`FormsSearchQuery(*args, **kwargs)`
:   Search query for forms entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.typeform.types.FormsEqCondition | airbyte_agent_sdk.connectors.typeform.types.FormsNeqCondition | airbyte_agent_sdk.connectors.typeform.types.FormsGtCondition | airbyte_agent_sdk.connectors.typeform.types.FormsGteCondition | airbyte_agent_sdk.connectors.typeform.types.FormsLtCondition | airbyte_agent_sdk.connectors.typeform.types.FormsLteCondition | airbyte_agent_sdk.connectors.typeform.types.FormsInCondition | airbyte_agent_sdk.connectors.typeform.types.FormsLikeCondition | airbyte_agent_sdk.connectors.typeform.types.FormsFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.FormsKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.FormsContainsCondition | airbyte_agent_sdk.connectors.typeform.types.FormsNotCondition | airbyte_agent_sdk.connectors.typeform.types.FormsAndCondition | airbyte_agent_sdk.connectors.typeform.types.FormsOrCondition | airbyte_agent_sdk.connectors.typeform.types.FormsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.typeform.types.FormsSortFilter]`
    :   The type of the None singleton.

<a id="FormsSortFilter"></a>

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

<a id="FormsStringFilter"></a>

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

<a id="ImagesAndCondition"></a>

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

<a id="ImagesAnyCondition"></a>

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

<a id="ImagesAnyValueFilter"></a>

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

<a id="ImagesContainsCondition"></a>

`ImagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.typeform.types.ImagesAnyValueFilter`
    :   The type of the None singleton.

<a id="ImagesEqCondition"></a>

`ImagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.typeform.types.ImagesSearchFilter`
    :   The type of the None singleton.

<a id="ImagesFuzzyCondition"></a>

`ImagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.typeform.types.ImagesStringFilter`
    :   The type of the None singleton.

<a id="ImagesGtCondition"></a>

`ImagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.typeform.types.ImagesSearchFilter`
    :   The type of the None singleton.

<a id="ImagesGteCondition"></a>

`ImagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.typeform.types.ImagesSearchFilter`
    :   The type of the None singleton.

<a id="ImagesInCondition"></a>

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

<a id="ImagesInFilter"></a>

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

<a id="ImagesKeywordCondition"></a>

`ImagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.typeform.types.ImagesStringFilter`
    :   The type of the None singleton.

<a id="ImagesLikeCondition"></a>

`ImagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.typeform.types.ImagesStringFilter`
    :   The type of the None singleton.

<a id="ImagesListParams"></a>

`ImagesListParams(*args, **kwargs)`
:   Parameters for images.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ImagesLtCondition"></a>

`ImagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.typeform.types.ImagesSearchFilter`
    :   The type of the None singleton.

<a id="ImagesLteCondition"></a>

`ImagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.typeform.types.ImagesSearchFilter`
    :   The type of the None singleton.

<a id="ImagesNeqCondition"></a>

`ImagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.typeform.types.ImagesSearchFilter`
    :   The type of the None singleton.

<a id="ImagesNotCondition"></a>

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

<a id="ImagesOrCondition"></a>

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

<a id="ImagesSearchFilter"></a>

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

<a id="ImagesSearchQuery"></a>

`ImagesSearchQuery(*args, **kwargs)`
:   Search query for images entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.typeform.types.ImagesEqCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesGtCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesGteCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesLtCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesLteCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesInCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesNotCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesAndCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesOrCondition | airbyte_agent_sdk.connectors.typeform.types.ImagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.typeform.types.ImagesSortFilter]`
    :   The type of the None singleton.

<a id="ImagesSortFilter"></a>

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

<a id="ImagesStringFilter"></a>

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

<a id="ResponsesAndCondition"></a>

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

<a id="ResponsesAnyCondition"></a>

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

<a id="ResponsesAnyValueFilter"></a>

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

<a id="ResponsesContainsCondition"></a>

`ResponsesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.typeform.types.ResponsesAnyValueFilter`
    :   The type of the None singleton.

<a id="ResponsesEqCondition"></a>

`ResponsesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.typeform.types.ResponsesSearchFilter`
    :   The type of the None singleton.

<a id="ResponsesFuzzyCondition"></a>

`ResponsesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.typeform.types.ResponsesStringFilter`
    :   The type of the None singleton.

<a id="ResponsesGtCondition"></a>

`ResponsesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.typeform.types.ResponsesSearchFilter`
    :   The type of the None singleton.

<a id="ResponsesGteCondition"></a>

`ResponsesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.typeform.types.ResponsesSearchFilter`
    :   The type of the None singleton.

<a id="ResponsesInCondition"></a>

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

<a id="ResponsesInFilter"></a>

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

<a id="ResponsesKeywordCondition"></a>

`ResponsesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.typeform.types.ResponsesStringFilter`
    :   The type of the None singleton.

<a id="ResponsesLikeCondition"></a>

`ResponsesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.typeform.types.ResponsesStringFilter`
    :   The type of the None singleton.

<a id="ResponsesListParams"></a>

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

<a id="ResponsesLtCondition"></a>

`ResponsesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.typeform.types.ResponsesSearchFilter`
    :   The type of the None singleton.

<a id="ResponsesLteCondition"></a>

`ResponsesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.typeform.types.ResponsesSearchFilter`
    :   The type of the None singleton.

<a id="ResponsesNeqCondition"></a>

`ResponsesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.typeform.types.ResponsesSearchFilter`
    :   The type of the None singleton.

<a id="ResponsesNotCondition"></a>

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

<a id="ResponsesOrCondition"></a>

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

<a id="ResponsesSearchFilter"></a>

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

<a id="ResponsesSearchQuery"></a>

`ResponsesSearchQuery(*args, **kwargs)`
:   Search query for responses entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.typeform.types.ResponsesEqCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesGtCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesGteCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesLtCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesLteCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesInCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesNotCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesAndCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesOrCondition | airbyte_agent_sdk.connectors.typeform.types.ResponsesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.typeform.types.ResponsesSortFilter]`
    :   The type of the None singleton.

<a id="ResponsesSortFilter"></a>

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

<a id="ResponsesStringFilter"></a>

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

<a id="ThemesAndCondition"></a>

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

<a id="ThemesAnyCondition"></a>

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

<a id="ThemesAnyValueFilter"></a>

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

<a id="ThemesContainsCondition"></a>

`ThemesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.typeform.types.ThemesAnyValueFilter`
    :   The type of the None singleton.

<a id="ThemesEqCondition"></a>

`ThemesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.typeform.types.ThemesSearchFilter`
    :   The type of the None singleton.

<a id="ThemesFuzzyCondition"></a>

`ThemesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.typeform.types.ThemesStringFilter`
    :   The type of the None singleton.

<a id="ThemesGtCondition"></a>

`ThemesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.typeform.types.ThemesSearchFilter`
    :   The type of the None singleton.

<a id="ThemesGteCondition"></a>

`ThemesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.typeform.types.ThemesSearchFilter`
    :   The type of the None singleton.

<a id="ThemesInCondition"></a>

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

<a id="ThemesInFilter"></a>

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

<a id="ThemesKeywordCondition"></a>

`ThemesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.typeform.types.ThemesStringFilter`
    :   The type of the None singleton.

<a id="ThemesLikeCondition"></a>

`ThemesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.typeform.types.ThemesStringFilter`
    :   The type of the None singleton.

<a id="ThemesListParams"></a>

`ThemesListParams(*args, **kwargs)`
:   Parameters for themes.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="ThemesLtCondition"></a>

`ThemesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.typeform.types.ThemesSearchFilter`
    :   The type of the None singleton.

<a id="ThemesLteCondition"></a>

`ThemesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.typeform.types.ThemesSearchFilter`
    :   The type of the None singleton.

<a id="ThemesNeqCondition"></a>

`ThemesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.typeform.types.ThemesSearchFilter`
    :   The type of the None singleton.

<a id="ThemesNotCondition"></a>

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

<a id="ThemesOrCondition"></a>

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

<a id="ThemesSearchFilter"></a>

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

<a id="ThemesSearchQuery"></a>

`ThemesSearchQuery(*args, **kwargs)`
:   Search query for themes entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.typeform.types.ThemesEqCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesGtCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesGteCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesLtCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesLteCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesInCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesNotCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesAndCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesOrCondition | airbyte_agent_sdk.connectors.typeform.types.ThemesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.typeform.types.ThemesSortFilter]`
    :   The type of the None singleton.

<a id="ThemesSortFilter"></a>

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

<a id="ThemesStringFilter"></a>

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

<a id="WebhooksAndCondition"></a>

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

<a id="WebhooksAnyCondition"></a>

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

<a id="WebhooksAnyValueFilter"></a>

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

<a id="WebhooksContainsCondition"></a>

`WebhooksContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.typeform.types.WebhooksAnyValueFilter`
    :   The type of the None singleton.

<a id="WebhooksEqCondition"></a>

`WebhooksEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.typeform.types.WebhooksSearchFilter`
    :   The type of the None singleton.

<a id="WebhooksFuzzyCondition"></a>

`WebhooksFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.typeform.types.WebhooksStringFilter`
    :   The type of the None singleton.

<a id="WebhooksGtCondition"></a>

`WebhooksGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.typeform.types.WebhooksSearchFilter`
    :   The type of the None singleton.

<a id="WebhooksGteCondition"></a>

`WebhooksGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.typeform.types.WebhooksSearchFilter`
    :   The type of the None singleton.

<a id="WebhooksInCondition"></a>

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

<a id="WebhooksInFilter"></a>

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

<a id="WebhooksKeywordCondition"></a>

`WebhooksKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.typeform.types.WebhooksStringFilter`
    :   The type of the None singleton.

<a id="WebhooksLikeCondition"></a>

`WebhooksLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.typeform.types.WebhooksStringFilter`
    :   The type of the None singleton.

<a id="WebhooksListParams"></a>

`WebhooksListParams(*args, **kwargs)`
:   Parameters for webhooks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `form_id: str`
    :   The type of the None singleton.

<a id="WebhooksLtCondition"></a>

`WebhooksLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.typeform.types.WebhooksSearchFilter`
    :   The type of the None singleton.

<a id="WebhooksLteCondition"></a>

`WebhooksLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.typeform.types.WebhooksSearchFilter`
    :   The type of the None singleton.

<a id="WebhooksNeqCondition"></a>

`WebhooksNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.typeform.types.WebhooksSearchFilter`
    :   The type of the None singleton.

<a id="WebhooksNotCondition"></a>

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

<a id="WebhooksOrCondition"></a>

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

<a id="WebhooksSearchFilter"></a>

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

<a id="WebhooksSearchQuery"></a>

`WebhooksSearchQuery(*args, **kwargs)`
:   Search query for webhooks entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.typeform.types.WebhooksEqCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksNeqCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksGtCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksGteCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksLtCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksLteCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksInCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksLikeCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksContainsCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksNotCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksAndCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksOrCondition | airbyte_agent_sdk.connectors.typeform.types.WebhooksAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.typeform.types.WebhooksSortFilter]`
    :   The type of the None singleton.

<a id="WebhooksSortFilter"></a>

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

<a id="WebhooksStringFilter"></a>

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

<a id="WorkspacesAndCondition"></a>

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

<a id="WorkspacesAnyCondition"></a>

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

<a id="WorkspacesAnyValueFilter"></a>

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

<a id="WorkspacesContainsCondition"></a>

`WorkspacesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.typeform.types.WorkspacesAnyValueFilter`
    :   The type of the None singleton.

<a id="WorkspacesEqCondition"></a>

`WorkspacesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.typeform.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

<a id="WorkspacesFuzzyCondition"></a>

`WorkspacesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.typeform.types.WorkspacesStringFilter`
    :   The type of the None singleton.

<a id="WorkspacesGtCondition"></a>

`WorkspacesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.typeform.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

<a id="WorkspacesGteCondition"></a>

`WorkspacesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.typeform.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

<a id="WorkspacesInCondition"></a>

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

<a id="WorkspacesInFilter"></a>

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

<a id="WorkspacesKeywordCondition"></a>

`WorkspacesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.typeform.types.WorkspacesStringFilter`
    :   The type of the None singleton.

<a id="WorkspacesLikeCondition"></a>

`WorkspacesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.typeform.types.WorkspacesStringFilter`
    :   The type of the None singleton.

<a id="WorkspacesListParams"></a>

`WorkspacesListParams(*args, **kwargs)`
:   Parameters for workspaces.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="WorkspacesLtCondition"></a>

`WorkspacesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.typeform.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

<a id="WorkspacesLteCondition"></a>

`WorkspacesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.typeform.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

<a id="WorkspacesNeqCondition"></a>

`WorkspacesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.typeform.types.WorkspacesSearchFilter`
    :   The type of the None singleton.

<a id="WorkspacesNotCondition"></a>

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

<a id="WorkspacesOrCondition"></a>

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

<a id="WorkspacesSearchFilter"></a>

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

<a id="WorkspacesSearchQuery"></a>

`WorkspacesSearchQuery(*args, **kwargs)`
:   Search query for workspaces entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.typeform.types.WorkspacesEqCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesNeqCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesGtCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesGteCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesLtCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesLteCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesInCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesLikeCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesFuzzyCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesKeywordCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesContainsCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesNotCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesAndCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesOrCondition | airbyte_agent_sdk.connectors.typeform.types.WorkspacesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.typeform.types.WorkspacesSortFilter]`
    :   The type of the None singleton.

<a id="WorkspacesSortFilter"></a>

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

<a id="WorkspacesStringFilter"></a>

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