---
id: airbyte_agent_sdk-connectors-zendesk_support-types
title: airbyte_agent_sdk.connectors.zendesk_support.types
---

Module airbyte_agent_sdk.connectors.zendesk_support.types
=========================================================
Type definitions for zendesk-support connector.

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

`ArticleAttachmentsGetParams(*args, **kwargs)`
:   Parameters for article_attachments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `article_id: str`
    :   The type of the None singleton.

    `attachment_id: str`
    :   The type of the None singleton.

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

`ArticlesGetParams(*args, **kwargs)`
:   Parameters for articles.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

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

`AttachmentsDownloadParams(*args, **kwargs)`
:   Parameters for attachments.download operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachment_id: str`
    :   The type of the None singleton.

    `range_header: str`
    :   The type of the None singleton.

`AttachmentsGetParams(*args, **kwargs)`
:   Parameters for attachments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachment_id: str`
    :   The type of the None singleton.

`AutomationsGetParams(*args, **kwargs)`
:   Parameters for automations.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `automation_id: str`
    :   The type of the None singleton.

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

`BrandsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsAnyValueFilter`
    :   The type of the None singleton.

`BrandsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsSearchFilter`
    :   The type of the None singleton.

`BrandsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsStringFilter`
    :   The type of the None singleton.

`BrandsGetParams(*args, **kwargs)`
:   Parameters for brands.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `brand_id: str`
    :   The type of the None singleton.

`BrandsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsSearchFilter`
    :   The type of the None singleton.

`BrandsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsSearchFilter`
    :   The type of the None singleton.

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

`BrandsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsStringFilter`
    :   The type of the None singleton.

`BrandsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsStringFilter`
    :   The type of the None singleton.

`BrandsListParams(*args, **kwargs)`
:   Parameters for brands.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

`BrandsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsSearchFilter`
    :   The type of the None singleton.

`BrandsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsSearchFilter`
    :   The type of the None singleton.

`BrandsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsSearchFilter`
    :   The type of the None singleton.

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

`BrandsSearchQuery(*args, **kwargs)`
:   Search query for brands entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.BrandsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.BrandsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.BrandsSortFilter]`
    :   The type of the None singleton.

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

`DeletedTicketsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsAnyValueFilter`
    :   The type of the None singleton.

`DeletedTicketsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsSearchFilter`
    :   The type of the None singleton.

`DeletedTicketsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsStringFilter`
    :   The type of the None singleton.

`DeletedTicketsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsSearchFilter`
    :   The type of the None singleton.

`DeletedTicketsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsSearchFilter`
    :   The type of the None singleton.

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

`DeletedTicketsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsStringFilter`
    :   The type of the None singleton.

`DeletedTicketsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsStringFilter`
    :   The type of the None singleton.

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

`DeletedTicketsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsSearchFilter`
    :   The type of the None singleton.

`DeletedTicketsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsSearchFilter`
    :   The type of the None singleton.

`DeletedTicketsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsSearchFilter`
    :   The type of the None singleton.

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

`DeletedTicketsSearchQuery(*args, **kwargs)`
:   Search query for deleted_tickets entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.DeletedTicketsSortFilter]`
    :   The type of the None singleton.

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

`GroupMembershipsListParams(*args, **kwargs)`
:   Parameters for group_memberships.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

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

`GroupsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsAnyValueFilter`
    :   The type of the None singleton.

`GroupsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsSearchFilter`
    :   The type of the None singleton.

`GroupsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsStringFilter`
    :   The type of the None singleton.

`GroupsGetParams(*args, **kwargs)`
:   Parameters for groups.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `group_id: str`
    :   The type of the None singleton.

`GroupsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsSearchFilter`
    :   The type of the None singleton.

`GroupsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsInFilter`
    :   The type of the None singleton.

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

`GroupsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsStringFilter`
    :   The type of the None singleton.

`GroupsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsStringFilter`
    :   The type of the None singleton.

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

`GroupsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsSearchFilter`
    :   The type of the None singleton.

`GroupsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsSearchFilter`
    :   The type of the None singleton.

`GroupsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.GroupsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsAnyCondition]`
    :   The type of the None singleton.

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

`GroupsSearchQuery(*args, **kwargs)`
:   Search query for groups entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.GroupsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.GroupsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.GroupsSortFilter]`
    :   The type of the None singleton.

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

`MacrosGetParams(*args, **kwargs)`
:   Parameters for macros.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `macro_id: str`
    :   The type of the None singleton.

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

`OrganizationMembershipsListParams(*args, **kwargs)`
:   Parameters for organization_memberships.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
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

    `and: list[airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAnyValueFilter`
    :   The type of the None singleton.

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

`OrganizationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAnyValueFilter`
    :   The type of the None singleton.

`OrganizationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

`OrganizationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsStringFilter`
    :   The type of the None singleton.

`OrganizationsGetParams(*args, **kwargs)`
:   Parameters for organizations.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `organization_id: str`
    :   The type of the None singleton.

`OrganizationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

`OrganizationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsInFilter`
    :   The type of the None singleton.

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

`OrganizationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsStringFilter`
    :   The type of the None singleton.

`OrganizationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsStringFilter`
    :   The type of the None singleton.

`OrganizationsListParams(*args, **kwargs)`
:   Parameters for organizations.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

`OrganizationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

`OrganizationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

`OrganizationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAnyCondition]`
    :   The type of the None singleton.

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

`OrganizationsSearchQuery(*args, **kwargs)`
:   Search query for organizations entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.OrganizationsSortFilter]`
    :   The type of the None singleton.

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

`SatisfactionRatingsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsAnyValueFilter`
    :   The type of the None singleton.

`SatisfactionRatingsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

`SatisfactionRatingsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsStringFilter`
    :   The type of the None singleton.

`SatisfactionRatingsGetParams(*args, **kwargs)`
:   Parameters for satisfaction_ratings.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `satisfaction_rating_id: str`
    :   The type of the None singleton.

`SatisfactionRatingsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

`SatisfactionRatingsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

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

`SatisfactionRatingsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsStringFilter`
    :   The type of the None singleton.

`SatisfactionRatingsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsStringFilter`
    :   The type of the None singleton.

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

`SatisfactionRatingsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

`SatisfactionRatingsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

`SatisfactionRatingsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsSearchFilter`
    :   The type of the None singleton.

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

`SatisfactionRatingsSearchQuery(*args, **kwargs)`
:   Search query for satisfaction_ratings entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.SatisfactionRatingsSortFilter]`
    :   The type of the None singleton.

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

`SlaPoliciesGetParams(*args, **kwargs)`
:   Parameters for sla_policies.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `sla_policy_id: str`
    :   The type of the None singleton.

`SlaPoliciesListParams(*args, **kwargs)`
:   Parameters for sla_policies.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

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

`TagsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: Any`
    :   The number of times this tag has been used across resources

    `name: Any`
    :   The tag name string used to label and categorize resources

`TagsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.TagsAnyValueFilter`
    :   The type of the None singleton.

`TagsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.TagsStringFilter`
    :   The type of the None singleton.

`TagsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.TagsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.TagsInFilter`
    :   The type of the None singleton.

`TagsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: list[int]`
    :   The number of times this tag has been used across resources

    `name: list[str]`
    :   The tag name string used to label and categorize resources

`TagsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.TagsStringFilter`
    :   The type of the None singleton.

`TagsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.TagsStringFilter`
    :   The type of the None singleton.

`TagsListParams(*args, **kwargs)`
:   Parameters for tags.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

`TagsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.TagsSearchFilter`
    :   The type of the None singleton.

`TagsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.TagsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.TagsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.TagsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsAnyCondition]`
    :   The type of the None singleton.

`TagsSearchFilter(*args, **kwargs)`
:   Available fields for filtering tags search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: int | None`
    :   The number of times this tag has been used across resources

    `name: str | None`
    :   The tag name string used to label and categorize resources

`TagsSearchQuery(*args, **kwargs)`
:   Search query for tags entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.TagsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TagsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.TagsSortFilter]`
    :   The type of the None singleton.

`TagsSortFilter(*args, **kwargs)`
:   Available fields for sorting tags search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: Literal['asc', 'desc']`
    :   The number of times this tag has been used across resources

    `name: Literal['asc', 'desc']`
    :   The tag name string used to label and categorize resources

`TagsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: str`
    :   The number of times this tag has been used across resources

    `name: str`
    :   The tag name string used to label and categorize resources

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

`TicketAuditsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsAnyValueFilter`
    :   The type of the None singleton.

`TicketAuditsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsSearchFilter`
    :   The type of the None singleton.

`TicketAuditsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsStringFilter`
    :   The type of the None singleton.

`TicketAuditsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsSearchFilter`
    :   The type of the None singleton.

`TicketAuditsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsSearchFilter`
    :   The type of the None singleton.

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

`TicketAuditsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsStringFilter`
    :   The type of the None singleton.

`TicketAuditsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsStringFilter`
    :   The type of the None singleton.

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

`TicketAuditsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsSearchFilter`
    :   The type of the None singleton.

`TicketAuditsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsSearchFilter`
    :   The type of the None singleton.

`TicketAuditsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsSearchFilter`
    :   The type of the None singleton.

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

`TicketAuditsSearchQuery(*args, **kwargs)`
:   Search query for ticket_audits entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketAuditsSortFilter]`
    :   The type of the None singleton.

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

`TicketCommentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsAnyValueFilter`
    :   The type of the None singleton.

`TicketCommentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsSearchFilter`
    :   The type of the None singleton.

`TicketCommentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsStringFilter`
    :   The type of the None singleton.

`TicketCommentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsSearchFilter`
    :   The type of the None singleton.

`TicketCommentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsSearchFilter`
    :   The type of the None singleton.

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

`TicketCommentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsStringFilter`
    :   The type of the None singleton.

`TicketCommentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsStringFilter`
    :   The type of the None singleton.

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

`TicketCommentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsSearchFilter`
    :   The type of the None singleton.

`TicketCommentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsSearchFilter`
    :   The type of the None singleton.

`TicketCommentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsSearchFilter`
    :   The type of the None singleton.

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

`TicketCommentsSearchQuery(*args, **kwargs)`
:   Search query for ticket_comments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketCommentsSortFilter]`
    :   The type of the None singleton.

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

`TicketFieldsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsAnyValueFilter`
    :   The type of the None singleton.

`TicketFieldsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

`TicketFieldsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsStringFilter`
    :   The type of the None singleton.

`TicketFieldsGetParams(*args, **kwargs)`
:   Parameters for ticket_fields.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ticket_field_id: str`
    :   The type of the None singleton.

`TicketFieldsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

`TicketFieldsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

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

`TicketFieldsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsStringFilter`
    :   The type of the None singleton.

`TicketFieldsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsStringFilter`
    :   The type of the None singleton.

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

`TicketFieldsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

`TicketFieldsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

`TicketFieldsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsSearchFilter`
    :   The type of the None singleton.

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

`TicketFieldsSearchQuery(*args, **kwargs)`
:   Search query for ticket_fields entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketFieldsSortFilter]`
    :   The type of the None singleton.

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

`TicketFormsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsAnyValueFilter`
    :   The type of the None singleton.

`TicketFormsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsSearchFilter`
    :   The type of the None singleton.

`TicketFormsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsStringFilter`
    :   The type of the None singleton.

`TicketFormsGetParams(*args, **kwargs)`
:   Parameters for ticket_forms.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ticket_form_id: str`
    :   The type of the None singleton.

`TicketFormsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsSearchFilter`
    :   The type of the None singleton.

`TicketFormsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsSearchFilter`
    :   The type of the None singleton.

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

`TicketFormsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsStringFilter`
    :   The type of the None singleton.

`TicketFormsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsStringFilter`
    :   The type of the None singleton.

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

`TicketFormsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsSearchFilter`
    :   The type of the None singleton.

`TicketFormsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsSearchFilter`
    :   The type of the None singleton.

`TicketFormsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsSearchFilter`
    :   The type of the None singleton.

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

`TicketFormsSearchQuery(*args, **kwargs)`
:   Search query for ticket_forms entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketFormsSortFilter]`
    :   The type of the None singleton.

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

`TicketMetricsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsAnyValueFilter`
    :   The type of the None singleton.

`TicketMetricsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsSearchFilter`
    :   The type of the None singleton.

`TicketMetricsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsStringFilter`
    :   The type of the None singleton.

`TicketMetricsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsSearchFilter`
    :   The type of the None singleton.

`TicketMetricsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsSearchFilter`
    :   The type of the None singleton.

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

`TicketMetricsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsStringFilter`
    :   The type of the None singleton.

`TicketMetricsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsStringFilter`
    :   The type of the None singleton.

`TicketMetricsListParams(*args, **kwargs)`
:   Parameters for ticket_metrics.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `per_page: int`
    :   The type of the None singleton.

`TicketMetricsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsSearchFilter`
    :   The type of the None singleton.

`TicketMetricsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsSearchFilter`
    :   The type of the None singleton.

`TicketMetricsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsSearchFilter`
    :   The type of the None singleton.

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

`TicketMetricsSearchQuery(*args, **kwargs)`
:   Search query for ticket_metrics entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketMetricsSortFilter]`
    :   The type of the None singleton.

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

`TicketsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsAnyValueFilter`
    :   The type of the None singleton.

`TicketsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsSearchFilter`
    :   The type of the None singleton.

`TicketsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsStringFilter`
    :   The type of the None singleton.

`TicketsGetParams(*args, **kwargs)`
:   Parameters for tickets.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ticket_id: str`
    :   The type of the None singleton.

`TicketsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsSearchFilter`
    :   The type of the None singleton.

`TicketsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsSearchFilter`
    :   The type of the None singleton.

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

`TicketsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsStringFilter`
    :   The type of the None singleton.

`TicketsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsStringFilter`
    :   The type of the None singleton.

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

`TicketsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsSearchFilter`
    :   The type of the None singleton.

`TicketsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsSearchFilter`
    :   The type of the None singleton.

`TicketsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsSearchFilter`
    :   The type of the None singleton.

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

`TicketsSearchQuery(*args, **kwargs)`
:   Search query for tickets entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.TicketsEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.TicketsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.TicketsSortFilter]`
    :   The type of the None singleton.

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

`TriggersGetParams(*args, **kwargs)`
:   Parameters for triggers.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `trigger_id: str`
    :   The type of the None singleton.

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

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.zendesk_support.types.UsersAnyValueFilter`
    :   The type of the None singleton.

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.zendesk_support.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.zendesk_support.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `user_id: str`
    :   The type of the None singleton.

`UsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.zendesk_support.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.zendesk_support.types.UsersSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.zendesk_support.types.UsersInFilter`
    :   The type of the None singleton.

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

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.zendesk_support.types.UsersStringFilter`
    :   The type of the None singleton.

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.zendesk_support.types.UsersStringFilter`
    :   The type of the None singleton.

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

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.zendesk_support.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.zendesk_support.types.UsersSearchFilter`
    :   The type of the None singleton.

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.zendesk_support.types.UsersSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.zendesk_support.types.UsersEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.zendesk_support.types.UsersEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersAnyCondition]`
    :   The type of the None singleton.

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

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.zendesk_support.types.UsersEqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersNeqCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersGtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersGteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLtCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLteCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersInCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersLikeCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersContainsCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersNotCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersAndCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersOrCondition | airbyte_agent_sdk.connectors.zendesk_support.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.zendesk_support.types.UsersSortFilter]`
    :   The type of the None singleton.

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

`ViewsGetParams(*args, **kwargs)`
:   Parameters for views.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `view_id: str`
    :   The type of the None singleton.

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