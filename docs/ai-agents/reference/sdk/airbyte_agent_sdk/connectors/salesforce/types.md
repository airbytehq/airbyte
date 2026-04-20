---
id: airbyte_agent_sdk-connectors-salesforce-types
title: airbyte_agent_sdk.connectors.salesforce.types
---

Module airbyte_agent_sdk.connectors.salesforce.types
====================================================
Type definitions for salesforce connector.

Classes
-------

`AccountsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.salesforce.types.AccountsEqCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsGtCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsGteCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsLtCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsLteCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsInCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsNotCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsAndCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsOrCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsAnyCondition]`
    :   The type of the None singleton.

`AccountsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.salesforce.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

`AccountsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_source: Any`
    :   Source of the account record (e.g., Web, Referral)

    `billing_address: Any`
    :   Complete billing address as a compound field

    `billing_city: Any`
    :   City portion of the billing address

    `billing_country: Any`
    :   Country portion of the billing address

    `billing_postal_code: Any`
    :   Postal code portion of the billing address

    `billing_state: Any`
    :   State or province portion of the billing address

    `billing_street: Any`
    :   Street address portion of the billing address

    `created_by_id: Any`
    :   ID of the user who created this account

    `created_date: Any`
    :   Date and time when the account was created

    `description: Any`
    :   Text description of the account

    `id: Any`
    :   Unique identifier for the account record

    `industry: Any`
    :   Primary business industry of the account

    `is_deleted: Any`
    :   Whether the account has been moved to the Recycle Bin

    `last_activity_date: Any`
    :   Date of the last activity associated with this account

    `last_modified_by_id: Any`
    :   ID of the user who last modified this account

    `last_modified_date: Any`
    :   Date and time when the account was last modified

    `name: Any`
    :   Name of the account or company

    `number_of_employees: Any`
    :   Number of employees at the account

    `owner_id: Any`
    :   ID of the user who owns this account

    `parent_id: Any`
    :   ID of the parent account, if this is a subsidiary

    `phone: Any`
    :   Primary phone number for the account

    `shipping_address: Any`
    :   Complete shipping address as a compound field

    `shipping_city: Any`
    :   City portion of the shipping address

    `shipping_country: Any`
    :   Country portion of the shipping address

    `shipping_postal_code: Any`
    :   Postal code portion of the shipping address

    `shipping_state: Any`
    :   State or province portion of the shipping address

    `shipping_street: Any`
    :   Street address portion of the shipping address

    `system_modstamp: Any`
    :   System timestamp when the record was last modified

    `type_: Any`
    :   Type of account (e.g., Customer, Partner, Competitor)

    `website: Any`
    :   Website URL for the account

`AccountsApiSearchParams(*args, **kwargs)`
:   Parameters for accounts.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`AccountsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.salesforce.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

`AccountsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.salesforce.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.salesforce.types.AccountsStringFilter`
    :   The type of the None singleton.

`AccountsGetParams(*args, **kwargs)`
:   Parameters for accounts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

`AccountsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.salesforce.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.salesforce.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.salesforce.types.AccountsInFilter`
    :   The type of the None singleton.

`AccountsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_source: list[str]`
    :   Source of the account record (e.g., Web, Referral)

    `billing_address: list[dict[str, typing.Any]]`
    :   Complete billing address as a compound field

    `billing_city: list[str]`
    :   City portion of the billing address

    `billing_country: list[str]`
    :   Country portion of the billing address

    `billing_postal_code: list[str]`
    :   Postal code portion of the billing address

    `billing_state: list[str]`
    :   State or province portion of the billing address

    `billing_street: list[str]`
    :   Street address portion of the billing address

    `created_by_id: list[str]`
    :   ID of the user who created this account

    `created_date: list[str]`
    :   Date and time when the account was created

    `description: list[str]`
    :   Text description of the account

    `id: list[str]`
    :   Unique identifier for the account record

    `industry: list[str]`
    :   Primary business industry of the account

    `is_deleted: list[bool]`
    :   Whether the account has been moved to the Recycle Bin

    `last_activity_date: list[str]`
    :   Date of the last activity associated with this account

    `last_modified_by_id: list[str]`
    :   ID of the user who last modified this account

    `last_modified_date: list[str]`
    :   Date and time when the account was last modified

    `name: list[str]`
    :   Name of the account or company

    `number_of_employees: list[int]`
    :   Number of employees at the account

    `owner_id: list[str]`
    :   ID of the user who owns this account

    `parent_id: list[str]`
    :   ID of the parent account, if this is a subsidiary

    `phone: list[str]`
    :   Primary phone number for the account

    `shipping_address: list[dict[str, typing.Any]]`
    :   Complete shipping address as a compound field

    `shipping_city: list[str]`
    :   City portion of the shipping address

    `shipping_country: list[str]`
    :   Country portion of the shipping address

    `shipping_postal_code: list[str]`
    :   Postal code portion of the shipping address

    `shipping_state: list[str]`
    :   State or province portion of the shipping address

    `shipping_street: list[str]`
    :   Street address portion of the shipping address

    `system_modstamp: list[str]`
    :   System timestamp when the record was last modified

    `type_: list[str]`
    :   Type of account (e.g., Customer, Partner, Competitor)

    `website: list[str]`
    :   Website URL for the account

`AccountsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.salesforce.types.AccountsStringFilter`
    :   The type of the None singleton.

`AccountsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.salesforce.types.AccountsStringFilter`
    :   The type of the None singleton.

`AccountsListParams(*args, **kwargs)`
:   Parameters for accounts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`AccountsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.salesforce.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.salesforce.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.salesforce.types.AccountsSearchFilter`
    :   The type of the None singleton.

`AccountsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.salesforce.types.AccountsEqCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsGtCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsGteCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsLtCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsLteCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsInCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsNotCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsAndCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsOrCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsAnyCondition`
    :   The type of the None singleton.

`AccountsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.salesforce.types.AccountsEqCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsGtCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsGteCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsLtCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsLteCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsInCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsNotCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsAndCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsOrCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsAnyCondition]`
    :   The type of the None singleton.

`AccountsSearchFilter(*args, **kwargs)`
:   Available fields for filtering accounts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_source: str | None`
    :   Source of the account record (e.g., Web, Referral)

    `billing_address: dict[str, typing.Any] | None`
    :   Complete billing address as a compound field

    `billing_city: str | None`
    :   City portion of the billing address

    `billing_country: str | None`
    :   Country portion of the billing address

    `billing_postal_code: str | None`
    :   Postal code portion of the billing address

    `billing_state: str | None`
    :   State or province portion of the billing address

    `billing_street: str | None`
    :   Street address portion of the billing address

    `created_by_id: str | None`
    :   ID of the user who created this account

    `created_date: str | None`
    :   Date and time when the account was created

    `description: str | None`
    :   Text description of the account

    `id: str`
    :   Unique identifier for the account record

    `industry: str | None`
    :   Primary business industry of the account

    `is_deleted: bool | None`
    :   Whether the account has been moved to the Recycle Bin

    `last_activity_date: str | None`
    :   Date of the last activity associated with this account

    `last_modified_by_id: str | None`
    :   ID of the user who last modified this account

    `last_modified_date: str | None`
    :   Date and time when the account was last modified

    `name: str | None`
    :   Name of the account or company

    `number_of_employees: int | None`
    :   Number of employees at the account

    `owner_id: str | None`
    :   ID of the user who owns this account

    `parent_id: str | None`
    :   ID of the parent account, if this is a subsidiary

    `phone: str | None`
    :   Primary phone number for the account

    `shipping_address: dict[str, typing.Any] | None`
    :   Complete shipping address as a compound field

    `shipping_city: str | None`
    :   City portion of the shipping address

    `shipping_country: str | None`
    :   Country portion of the shipping address

    `shipping_postal_code: str | None`
    :   Postal code portion of the shipping address

    `shipping_state: str | None`
    :   State or province portion of the shipping address

    `shipping_street: str | None`
    :   Street address portion of the shipping address

    `system_modstamp: str | None`
    :   System timestamp when the record was last modified

    `type_: str | None`
    :   Type of account (e.g., Customer, Partner, Competitor)

    `website: str | None`
    :   Website URL for the account

`AccountsSearchQuery(*args, **kwargs)`
:   Search query for accounts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.salesforce.types.AccountsEqCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsGtCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsGteCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsLtCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsLteCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsInCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsNotCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsAndCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsOrCondition | airbyte_agent_sdk.connectors.salesforce.types.AccountsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.salesforce.types.AccountsSortFilter]`
    :   The type of the None singleton.

`AccountsSortFilter(*args, **kwargs)`
:   Available fields for sorting accounts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_source: Literal['asc', 'desc']`
    :   Source of the account record (e.g., Web, Referral)

    `billing_address: Literal['asc', 'desc']`
    :   Complete billing address as a compound field

    `billing_city: Literal['asc', 'desc']`
    :   City portion of the billing address

    `billing_country: Literal['asc', 'desc']`
    :   Country portion of the billing address

    `billing_postal_code: Literal['asc', 'desc']`
    :   Postal code portion of the billing address

    `billing_state: Literal['asc', 'desc']`
    :   State or province portion of the billing address

    `billing_street: Literal['asc', 'desc']`
    :   Street address portion of the billing address

    `created_by_id: Literal['asc', 'desc']`
    :   ID of the user who created this account

    `created_date: Literal['asc', 'desc']`
    :   Date and time when the account was created

    `description: Literal['asc', 'desc']`
    :   Text description of the account

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the account record

    `industry: Literal['asc', 'desc']`
    :   Primary business industry of the account

    `is_deleted: Literal['asc', 'desc']`
    :   Whether the account has been moved to the Recycle Bin

    `last_activity_date: Literal['asc', 'desc']`
    :   Date of the last activity associated with this account

    `last_modified_by_id: Literal['asc', 'desc']`
    :   ID of the user who last modified this account

    `last_modified_date: Literal['asc', 'desc']`
    :   Date and time when the account was last modified

    `name: Literal['asc', 'desc']`
    :   Name of the account or company

    `number_of_employees: Literal['asc', 'desc']`
    :   Number of employees at the account

    `owner_id: Literal['asc', 'desc']`
    :   ID of the user who owns this account

    `parent_id: Literal['asc', 'desc']`
    :   ID of the parent account, if this is a subsidiary

    `phone: Literal['asc', 'desc']`
    :   Primary phone number for the account

    `shipping_address: Literal['asc', 'desc']`
    :   Complete shipping address as a compound field

    `shipping_city: Literal['asc', 'desc']`
    :   City portion of the shipping address

    `shipping_country: Literal['asc', 'desc']`
    :   Country portion of the shipping address

    `shipping_postal_code: Literal['asc', 'desc']`
    :   Postal code portion of the shipping address

    `shipping_state: Literal['asc', 'desc']`
    :   State or province portion of the shipping address

    `shipping_street: Literal['asc', 'desc']`
    :   Street address portion of the shipping address

    `system_modstamp: Literal['asc', 'desc']`
    :   System timestamp when the record was last modified

    `type_: Literal['asc', 'desc']`
    :   Type of account (e.g., Customer, Partner, Competitor)

    `website: Literal['asc', 'desc']`
    :   Website URL for the account

`AccountsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_source: str`
    :   Source of the account record (e.g., Web, Referral)

    `billing_address: str`
    :   Complete billing address as a compound field

    `billing_city: str`
    :   City portion of the billing address

    `billing_country: str`
    :   Country portion of the billing address

    `billing_postal_code: str`
    :   Postal code portion of the billing address

    `billing_state: str`
    :   State or province portion of the billing address

    `billing_street: str`
    :   Street address portion of the billing address

    `created_by_id: str`
    :   ID of the user who created this account

    `created_date: str`
    :   Date and time when the account was created

    `description: str`
    :   Text description of the account

    `id: str`
    :   Unique identifier for the account record

    `industry: str`
    :   Primary business industry of the account

    `is_deleted: str`
    :   Whether the account has been moved to the Recycle Bin

    `last_activity_date: str`
    :   Date of the last activity associated with this account

    `last_modified_by_id: str`
    :   ID of the user who last modified this account

    `last_modified_date: str`
    :   Date and time when the account was last modified

    `name: str`
    :   Name of the account or company

    `number_of_employees: str`
    :   Number of employees at the account

    `owner_id: str`
    :   ID of the user who owns this account

    `parent_id: str`
    :   ID of the parent account, if this is a subsidiary

    `phone: str`
    :   Primary phone number for the account

    `shipping_address: str`
    :   Complete shipping address as a compound field

    `shipping_city: str`
    :   City portion of the shipping address

    `shipping_country: str`
    :   Country portion of the shipping address

    `shipping_postal_code: str`
    :   Postal code portion of the shipping address

    `shipping_state: str`
    :   State or province portion of the shipping address

    `shipping_street: str`
    :   Street address portion of the shipping address

    `system_modstamp: str`
    :   System timestamp when the record was last modified

    `type_: str`
    :   Type of account (e.g., Customer, Partner, Competitor)

    `website: str`
    :   Website URL for the account

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

`AttachmentsDownloadParams(*args, **kwargs)`
:   Parameters for attachments.download operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `range_header: str`
    :   The type of the None singleton.

`AttachmentsGetParams(*args, **kwargs)`
:   Parameters for attachments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

`AttachmentsListParams(*args, **kwargs)`
:   Parameters for attachments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`CampaignsApiSearchParams(*args, **kwargs)`
:   Parameters for campaigns.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`CampaignsGetParams(*args, **kwargs)`
:   Parameters for campaigns.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

`CampaignsListParams(*args, **kwargs)`
:   Parameters for campaigns.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`CasesApiSearchParams(*args, **kwargs)`
:   Parameters for cases.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`CasesGetParams(*args, **kwargs)`
:   Parameters for cases.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

`CasesListParams(*args, **kwargs)`
:   Parameters for cases.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`ContactsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.salesforce.types.ContactsEqCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsGtCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsGteCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsLtCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsLteCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsInCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsNotCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsAndCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsOrCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsAnyCondition]`
    :   The type of the None singleton.

`ContactsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.salesforce.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

`ContactsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Any`
    :   ID of the account this contact is associated with

    `created_by_id: Any`
    :   ID of the user who created this contact

    `created_date: Any`
    :   Date and time when the contact was created

    `department: Any`
    :   Department within the account where the contact works

    `email: Any`
    :   Email address of the contact

    `first_name: Any`
    :   First name of the contact

    `id: Any`
    :   Unique identifier for the contact record

    `is_deleted: Any`
    :   Whether the contact has been moved to the Recycle Bin

    `last_activity_date: Any`
    :   Date of the last activity associated with this contact

    `last_modified_by_id: Any`
    :   ID of the user who last modified this contact

    `last_modified_date: Any`
    :   Date and time when the contact was last modified

    `last_name: Any`
    :   Last name of the contact

    `lead_source: Any`
    :   Source from which this contact originated

    `mailing_address: Any`
    :   Complete mailing address as a compound field

    `mailing_city: Any`
    :   City portion of the mailing address

    `mailing_country: Any`
    :   Country portion of the mailing address

    `mailing_postal_code: Any`
    :   Postal code portion of the mailing address

    `mailing_state: Any`
    :   State or province portion of the mailing address

    `mailing_street: Any`
    :   Street address portion of the mailing address

    `mobile_phone: Any`
    :   Mobile phone number of the contact

    `name: Any`
    :   Full name of the contact (read-only, concatenation of first and last name)

    `owner_id: Any`
    :   ID of the user who owns this contact

    `phone: Any`
    :   Business phone number of the contact

    `reports_to_id: Any`
    :   ID of the contact this contact reports to

    `system_modstamp: Any`
    :   System timestamp when the record was last modified

    `title: Any`
    :   Job title of the contact

`ContactsApiSearchParams(*args, **kwargs)`
:   Parameters for contacts.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`ContactsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.salesforce.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

`ContactsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.salesforce.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.salesforce.types.ContactsStringFilter`
    :   The type of the None singleton.

`ContactsGetParams(*args, **kwargs)`
:   Parameters for contacts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

`ContactsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.salesforce.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.salesforce.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.salesforce.types.ContactsInFilter`
    :   The type of the None singleton.

`ContactsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: list[str]`
    :   ID of the account this contact is associated with

    `created_by_id: list[str]`
    :   ID of the user who created this contact

    `created_date: list[str]`
    :   Date and time when the contact was created

    `department: list[str]`
    :   Department within the account where the contact works

    `email: list[str]`
    :   Email address of the contact

    `first_name: list[str]`
    :   First name of the contact

    `id: list[str]`
    :   Unique identifier for the contact record

    `is_deleted: list[bool]`
    :   Whether the contact has been moved to the Recycle Bin

    `last_activity_date: list[str]`
    :   Date of the last activity associated with this contact

    `last_modified_by_id: list[str]`
    :   ID of the user who last modified this contact

    `last_modified_date: list[str]`
    :   Date and time when the contact was last modified

    `last_name: list[str]`
    :   Last name of the contact

    `lead_source: list[str]`
    :   Source from which this contact originated

    `mailing_address: list[dict[str, typing.Any]]`
    :   Complete mailing address as a compound field

    `mailing_city: list[str]`
    :   City portion of the mailing address

    `mailing_country: list[str]`
    :   Country portion of the mailing address

    `mailing_postal_code: list[str]`
    :   Postal code portion of the mailing address

    `mailing_state: list[str]`
    :   State or province portion of the mailing address

    `mailing_street: list[str]`
    :   Street address portion of the mailing address

    `mobile_phone: list[str]`
    :   Mobile phone number of the contact

    `name: list[str]`
    :   Full name of the contact (read-only, concatenation of first and last name)

    `owner_id: list[str]`
    :   ID of the user who owns this contact

    `phone: list[str]`
    :   Business phone number of the contact

    `reports_to_id: list[str]`
    :   ID of the contact this contact reports to

    `system_modstamp: list[str]`
    :   System timestamp when the record was last modified

    `title: list[str]`
    :   Job title of the contact

`ContactsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.salesforce.types.ContactsStringFilter`
    :   The type of the None singleton.

`ContactsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.salesforce.types.ContactsStringFilter`
    :   The type of the None singleton.

`ContactsListParams(*args, **kwargs)`
:   Parameters for contacts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`ContactsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.salesforce.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.salesforce.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.salesforce.types.ContactsSearchFilter`
    :   The type of the None singleton.

`ContactsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.salesforce.types.ContactsEqCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsGtCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsGteCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsLtCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsLteCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsInCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsNotCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsAndCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsOrCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsAnyCondition`
    :   The type of the None singleton.

`ContactsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.salesforce.types.ContactsEqCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsGtCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsGteCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsLtCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsLteCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsInCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsNotCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsAndCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsOrCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsAnyCondition]`
    :   The type of the None singleton.

`ContactsSearchFilter(*args, **kwargs)`
:   Available fields for filtering contacts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str | None`
    :   ID of the account this contact is associated with

    `created_by_id: str | None`
    :   ID of the user who created this contact

    `created_date: str | None`
    :   Date and time when the contact was created

    `department: str | None`
    :   Department within the account where the contact works

    `email: str | None`
    :   Email address of the contact

    `first_name: str | None`
    :   First name of the contact

    `id: str`
    :   Unique identifier for the contact record

    `is_deleted: bool | None`
    :   Whether the contact has been moved to the Recycle Bin

    `last_activity_date: str | None`
    :   Date of the last activity associated with this contact

    `last_modified_by_id: str | None`
    :   ID of the user who last modified this contact

    `last_modified_date: str | None`
    :   Date and time when the contact was last modified

    `last_name: str | None`
    :   Last name of the contact

    `lead_source: str | None`
    :   Source from which this contact originated

    `mailing_address: dict[str, typing.Any] | None`
    :   Complete mailing address as a compound field

    `mailing_city: str | None`
    :   City portion of the mailing address

    `mailing_country: str | None`
    :   Country portion of the mailing address

    `mailing_postal_code: str | None`
    :   Postal code portion of the mailing address

    `mailing_state: str | None`
    :   State or province portion of the mailing address

    `mailing_street: str | None`
    :   Street address portion of the mailing address

    `mobile_phone: str | None`
    :   Mobile phone number of the contact

    `name: str | None`
    :   Full name of the contact (read-only, concatenation of first and last name)

    `owner_id: str | None`
    :   ID of the user who owns this contact

    `phone: str | None`
    :   Business phone number of the contact

    `reports_to_id: str | None`
    :   ID of the contact this contact reports to

    `system_modstamp: str | None`
    :   System timestamp when the record was last modified

    `title: str | None`
    :   Job title of the contact

`ContactsSearchQuery(*args, **kwargs)`
:   Search query for contacts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.salesforce.types.ContactsEqCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsGtCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsGteCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsLtCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsLteCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsInCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsNotCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsAndCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsOrCondition | airbyte_agent_sdk.connectors.salesforce.types.ContactsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.salesforce.types.ContactsSortFilter]`
    :   The type of the None singleton.

`ContactsSortFilter(*args, **kwargs)`
:   Available fields for sorting contacts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Literal['asc', 'desc']`
    :   ID of the account this contact is associated with

    `created_by_id: Literal['asc', 'desc']`
    :   ID of the user who created this contact

    `created_date: Literal['asc', 'desc']`
    :   Date and time when the contact was created

    `department: Literal['asc', 'desc']`
    :   Department within the account where the contact works

    `email: Literal['asc', 'desc']`
    :   Email address of the contact

    `first_name: Literal['asc', 'desc']`
    :   First name of the contact

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the contact record

    `is_deleted: Literal['asc', 'desc']`
    :   Whether the contact has been moved to the Recycle Bin

    `last_activity_date: Literal['asc', 'desc']`
    :   Date of the last activity associated with this contact

    `last_modified_by_id: Literal['asc', 'desc']`
    :   ID of the user who last modified this contact

    `last_modified_date: Literal['asc', 'desc']`
    :   Date and time when the contact was last modified

    `last_name: Literal['asc', 'desc']`
    :   Last name of the contact

    `lead_source: Literal['asc', 'desc']`
    :   Source from which this contact originated

    `mailing_address: Literal['asc', 'desc']`
    :   Complete mailing address as a compound field

    `mailing_city: Literal['asc', 'desc']`
    :   City portion of the mailing address

    `mailing_country: Literal['asc', 'desc']`
    :   Country portion of the mailing address

    `mailing_postal_code: Literal['asc', 'desc']`
    :   Postal code portion of the mailing address

    `mailing_state: Literal['asc', 'desc']`
    :   State or province portion of the mailing address

    `mailing_street: Literal['asc', 'desc']`
    :   Street address portion of the mailing address

    `mobile_phone: Literal['asc', 'desc']`
    :   Mobile phone number of the contact

    `name: Literal['asc', 'desc']`
    :   Full name of the contact (read-only, concatenation of first and last name)

    `owner_id: Literal['asc', 'desc']`
    :   ID of the user who owns this contact

    `phone: Literal['asc', 'desc']`
    :   Business phone number of the contact

    `reports_to_id: Literal['asc', 'desc']`
    :   ID of the contact this contact reports to

    `system_modstamp: Literal['asc', 'desc']`
    :   System timestamp when the record was last modified

    `title: Literal['asc', 'desc']`
    :   Job title of the contact

`ContactsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   ID of the account this contact is associated with

    `created_by_id: str`
    :   ID of the user who created this contact

    `created_date: str`
    :   Date and time when the contact was created

    `department: str`
    :   Department within the account where the contact works

    `email: str`
    :   Email address of the contact

    `first_name: str`
    :   First name of the contact

    `id: str`
    :   Unique identifier for the contact record

    `is_deleted: str`
    :   Whether the contact has been moved to the Recycle Bin

    `last_activity_date: str`
    :   Date of the last activity associated with this contact

    `last_modified_by_id: str`
    :   ID of the user who last modified this contact

    `last_modified_date: str`
    :   Date and time when the contact was last modified

    `last_name: str`
    :   Last name of the contact

    `lead_source: str`
    :   Source from which this contact originated

    `mailing_address: str`
    :   Complete mailing address as a compound field

    `mailing_city: str`
    :   City portion of the mailing address

    `mailing_country: str`
    :   Country portion of the mailing address

    `mailing_postal_code: str`
    :   Postal code portion of the mailing address

    `mailing_state: str`
    :   State or province portion of the mailing address

    `mailing_street: str`
    :   Street address portion of the mailing address

    `mobile_phone: str`
    :   Mobile phone number of the contact

    `name: str`
    :   Full name of the contact (read-only, concatenation of first and last name)

    `owner_id: str`
    :   ID of the user who owns this contact

    `phone: str`
    :   Business phone number of the contact

    `reports_to_id: str`
    :   ID of the contact this contact reports to

    `system_modstamp: str`
    :   System timestamp when the record was last modified

    `title: str`
    :   Job title of the contact

`ContentVersionsDownloadParams(*args, **kwargs)`
:   Parameters for content_versions.download operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `range_header: str`
    :   The type of the None singleton.

`ContentVersionsGetParams(*args, **kwargs)`
:   Parameters for content_versions.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

`ContentVersionsListParams(*args, **kwargs)`
:   Parameters for content_versions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`EventsApiSearchParams(*args, **kwargs)`
:   Parameters for events.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`EventsGetParams(*args, **kwargs)`
:   Parameters for events.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

`EventsListParams(*args, **kwargs)`
:   Parameters for events.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`LeadsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.salesforce.types.LeadsEqCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsGtCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsGteCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsLtCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsLteCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsInCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsNotCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsAndCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsOrCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsAnyCondition]`
    :   The type of the None singleton.

`LeadsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.salesforce.types.LeadsAnyValueFilter`
    :   The type of the None singleton.

`LeadsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address: Any`
    :   Complete address as a compound field

    `city: Any`
    :   City portion of the address

    `company: Any`
    :   Company or organization the lead works for

    `converted_account_id: Any`
    :   ID of the account created when lead was converted

    `converted_contact_id: Any`
    :   ID of the contact created when lead was converted

    `converted_date: Any`
    :   Date when the lead was converted

    `converted_opportunity_id: Any`
    :   ID of the opportunity created when lead was converted

    `country: Any`
    :   Country portion of the address

    `created_by_id: Any`
    :   ID of the user who created this lead

    `created_date: Any`
    :   Date and time when the lead was created

    `email: Any`
    :   Email address of the lead

    `first_name: Any`
    :   First name of the lead

    `id: Any`
    :   Unique identifier for the lead record

    `industry: Any`
    :   Industry the lead's company operates in

    `is_converted: Any`
    :   Whether the lead has been converted to an account, contact, and opportunity

    `is_deleted: Any`
    :   Whether the lead has been moved to the Recycle Bin

    `last_activity_date: Any`
    :   Date of the last activity associated with this lead

    `last_modified_by_id: Any`
    :   ID of the user who last modified this lead

    `last_modified_date: Any`
    :   Date and time when the lead was last modified

    `last_name: Any`
    :   Last name of the lead

    `lead_source: Any`
    :   Source from which this lead originated

    `mobile_phone: Any`
    :   Mobile phone number of the lead

    `name: Any`
    :   Full name of the lead (read-only, concatenation of first and last name)

    `number_of_employees: Any`
    :   Number of employees at the lead's company

    `owner_id: Any`
    :   ID of the user who owns this lead

    `phone: Any`
    :   Phone number of the lead

    `postal_code: Any`
    :   Postal code portion of the address

    `rating: Any`
    :   Rating of the lead (e.g., Hot, Warm, Cold)

    `state: Any`
    :   State or province portion of the address

    `status: Any`
    :   Current status of the lead in the sales process

    `street: Any`
    :   Street address portion of the address

    `system_modstamp: Any`
    :   System timestamp when the record was last modified

    `title: Any`
    :   Job title of the lead

    `website: Any`
    :   Website URL for the lead's company

`LeadsApiSearchParams(*args, **kwargs)`
:   Parameters for leads.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`LeadsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.salesforce.types.LeadsAnyValueFilter`
    :   The type of the None singleton.

`LeadsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.salesforce.types.LeadsSearchFilter`
    :   The type of the None singleton.

`LeadsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.salesforce.types.LeadsStringFilter`
    :   The type of the None singleton.

`LeadsGetParams(*args, **kwargs)`
:   Parameters for leads.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

`LeadsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.salesforce.types.LeadsSearchFilter`
    :   The type of the None singleton.

`LeadsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.salesforce.types.LeadsSearchFilter`
    :   The type of the None singleton.

`LeadsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.salesforce.types.LeadsInFilter`
    :   The type of the None singleton.

`LeadsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address: list[dict[str, typing.Any]]`
    :   Complete address as a compound field

    `city: list[str]`
    :   City portion of the address

    `company: list[str]`
    :   Company or organization the lead works for

    `converted_account_id: list[str]`
    :   ID of the account created when lead was converted

    `converted_contact_id: list[str]`
    :   ID of the contact created when lead was converted

    `converted_date: list[str]`
    :   Date when the lead was converted

    `converted_opportunity_id: list[str]`
    :   ID of the opportunity created when lead was converted

    `country: list[str]`
    :   Country portion of the address

    `created_by_id: list[str]`
    :   ID of the user who created this lead

    `created_date: list[str]`
    :   Date and time when the lead was created

    `email: list[str]`
    :   Email address of the lead

    `first_name: list[str]`
    :   First name of the lead

    `id: list[str]`
    :   Unique identifier for the lead record

    `industry: list[str]`
    :   Industry the lead's company operates in

    `is_converted: list[bool]`
    :   Whether the lead has been converted to an account, contact, and opportunity

    `is_deleted: list[bool]`
    :   Whether the lead has been moved to the Recycle Bin

    `last_activity_date: list[str]`
    :   Date of the last activity associated with this lead

    `last_modified_by_id: list[str]`
    :   ID of the user who last modified this lead

    `last_modified_date: list[str]`
    :   Date and time when the lead was last modified

    `last_name: list[str]`
    :   Last name of the lead

    `lead_source: list[str]`
    :   Source from which this lead originated

    `mobile_phone: list[str]`
    :   Mobile phone number of the lead

    `name: list[str]`
    :   Full name of the lead (read-only, concatenation of first and last name)

    `number_of_employees: list[int]`
    :   Number of employees at the lead's company

    `owner_id: list[str]`
    :   ID of the user who owns this lead

    `phone: list[str]`
    :   Phone number of the lead

    `postal_code: list[str]`
    :   Postal code portion of the address

    `rating: list[str]`
    :   Rating of the lead (e.g., Hot, Warm, Cold)

    `state: list[str]`
    :   State or province portion of the address

    `status: list[str]`
    :   Current status of the lead in the sales process

    `street: list[str]`
    :   Street address portion of the address

    `system_modstamp: list[str]`
    :   System timestamp when the record was last modified

    `title: list[str]`
    :   Job title of the lead

    `website: list[str]`
    :   Website URL for the lead's company

`LeadsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.salesforce.types.LeadsStringFilter`
    :   The type of the None singleton.

`LeadsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.salesforce.types.LeadsStringFilter`
    :   The type of the None singleton.

`LeadsListParams(*args, **kwargs)`
:   Parameters for leads.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`LeadsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.salesforce.types.LeadsSearchFilter`
    :   The type of the None singleton.

`LeadsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.salesforce.types.LeadsSearchFilter`
    :   The type of the None singleton.

`LeadsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.salesforce.types.LeadsSearchFilter`
    :   The type of the None singleton.

`LeadsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.salesforce.types.LeadsEqCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsGtCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsGteCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsLtCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsLteCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsInCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsNotCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsAndCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsOrCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsAnyCondition`
    :   The type of the None singleton.

`LeadsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.salesforce.types.LeadsEqCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsGtCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsGteCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsLtCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsLteCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsInCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsNotCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsAndCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsOrCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsAnyCondition]`
    :   The type of the None singleton.

`LeadsSearchFilter(*args, **kwargs)`
:   Available fields for filtering leads search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address: dict[str, typing.Any] | None`
    :   Complete address as a compound field

    `city: str | None`
    :   City portion of the address

    `company: str | None`
    :   Company or organization the lead works for

    `converted_account_id: str | None`
    :   ID of the account created when lead was converted

    `converted_contact_id: str | None`
    :   ID of the contact created when lead was converted

    `converted_date: str | None`
    :   Date when the lead was converted

    `converted_opportunity_id: str | None`
    :   ID of the opportunity created when lead was converted

    `country: str | None`
    :   Country portion of the address

    `created_by_id: str | None`
    :   ID of the user who created this lead

    `created_date: str | None`
    :   Date and time when the lead was created

    `email: str | None`
    :   Email address of the lead

    `first_name: str | None`
    :   First name of the lead

    `id: str`
    :   Unique identifier for the lead record

    `industry: str | None`
    :   Industry the lead's company operates in

    `is_converted: bool | None`
    :   Whether the lead has been converted to an account, contact, and opportunity

    `is_deleted: bool | None`
    :   Whether the lead has been moved to the Recycle Bin

    `last_activity_date: str | None`
    :   Date of the last activity associated with this lead

    `last_modified_by_id: str | None`
    :   ID of the user who last modified this lead

    `last_modified_date: str | None`
    :   Date and time when the lead was last modified

    `last_name: str | None`
    :   Last name of the lead

    `lead_source: str | None`
    :   Source from which this lead originated

    `mobile_phone: str | None`
    :   Mobile phone number of the lead

    `name: str | None`
    :   Full name of the lead (read-only, concatenation of first and last name)

    `number_of_employees: int | None`
    :   Number of employees at the lead's company

    `owner_id: str | None`
    :   ID of the user who owns this lead

    `phone: str | None`
    :   Phone number of the lead

    `postal_code: str | None`
    :   Postal code portion of the address

    `rating: str | None`
    :   Rating of the lead (e.g., Hot, Warm, Cold)

    `state: str | None`
    :   State or province portion of the address

    `status: str | None`
    :   Current status of the lead in the sales process

    `street: str | None`
    :   Street address portion of the address

    `system_modstamp: str | None`
    :   System timestamp when the record was last modified

    `title: str | None`
    :   Job title of the lead

    `website: str | None`
    :   Website URL for the lead's company

`LeadsSearchQuery(*args, **kwargs)`
:   Search query for leads entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.salesforce.types.LeadsEqCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsGtCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsGteCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsLtCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsLteCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsInCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsNotCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsAndCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsOrCondition | airbyte_agent_sdk.connectors.salesforce.types.LeadsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.salesforce.types.LeadsSortFilter]`
    :   The type of the None singleton.

`LeadsSortFilter(*args, **kwargs)`
:   Available fields for sorting leads search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address: Literal['asc', 'desc']`
    :   Complete address as a compound field

    `city: Literal['asc', 'desc']`
    :   City portion of the address

    `company: Literal['asc', 'desc']`
    :   Company or organization the lead works for

    `converted_account_id: Literal['asc', 'desc']`
    :   ID of the account created when lead was converted

    `converted_contact_id: Literal['asc', 'desc']`
    :   ID of the contact created when lead was converted

    `converted_date: Literal['asc', 'desc']`
    :   Date when the lead was converted

    `converted_opportunity_id: Literal['asc', 'desc']`
    :   ID of the opportunity created when lead was converted

    `country: Literal['asc', 'desc']`
    :   Country portion of the address

    `created_by_id: Literal['asc', 'desc']`
    :   ID of the user who created this lead

    `created_date: Literal['asc', 'desc']`
    :   Date and time when the lead was created

    `email: Literal['asc', 'desc']`
    :   Email address of the lead

    `first_name: Literal['asc', 'desc']`
    :   First name of the lead

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the lead record

    `industry: Literal['asc', 'desc']`
    :   Industry the lead's company operates in

    `is_converted: Literal['asc', 'desc']`
    :   Whether the lead has been converted to an account, contact, and opportunity

    `is_deleted: Literal['asc', 'desc']`
    :   Whether the lead has been moved to the Recycle Bin

    `last_activity_date: Literal['asc', 'desc']`
    :   Date of the last activity associated with this lead

    `last_modified_by_id: Literal['asc', 'desc']`
    :   ID of the user who last modified this lead

    `last_modified_date: Literal['asc', 'desc']`
    :   Date and time when the lead was last modified

    `last_name: Literal['asc', 'desc']`
    :   Last name of the lead

    `lead_source: Literal['asc', 'desc']`
    :   Source from which this lead originated

    `mobile_phone: Literal['asc', 'desc']`
    :   Mobile phone number of the lead

    `name: Literal['asc', 'desc']`
    :   Full name of the lead (read-only, concatenation of first and last name)

    `number_of_employees: Literal['asc', 'desc']`
    :   Number of employees at the lead's company

    `owner_id: Literal['asc', 'desc']`
    :   ID of the user who owns this lead

    `phone: Literal['asc', 'desc']`
    :   Phone number of the lead

    `postal_code: Literal['asc', 'desc']`
    :   Postal code portion of the address

    `rating: Literal['asc', 'desc']`
    :   Rating of the lead (e.g., Hot, Warm, Cold)

    `state: Literal['asc', 'desc']`
    :   State or province portion of the address

    `status: Literal['asc', 'desc']`
    :   Current status of the lead in the sales process

    `street: Literal['asc', 'desc']`
    :   Street address portion of the address

    `system_modstamp: Literal['asc', 'desc']`
    :   System timestamp when the record was last modified

    `title: Literal['asc', 'desc']`
    :   Job title of the lead

    `website: Literal['asc', 'desc']`
    :   Website URL for the lead's company

`LeadsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `address: str`
    :   Complete address as a compound field

    `city: str`
    :   City portion of the address

    `company: str`
    :   Company or organization the lead works for

    `converted_account_id: str`
    :   ID of the account created when lead was converted

    `converted_contact_id: str`
    :   ID of the contact created when lead was converted

    `converted_date: str`
    :   Date when the lead was converted

    `converted_opportunity_id: str`
    :   ID of the opportunity created when lead was converted

    `country: str`
    :   Country portion of the address

    `created_by_id: str`
    :   ID of the user who created this lead

    `created_date: str`
    :   Date and time when the lead was created

    `email: str`
    :   Email address of the lead

    `first_name: str`
    :   First name of the lead

    `id: str`
    :   Unique identifier for the lead record

    `industry: str`
    :   Industry the lead's company operates in

    `is_converted: str`
    :   Whether the lead has been converted to an account, contact, and opportunity

    `is_deleted: str`
    :   Whether the lead has been moved to the Recycle Bin

    `last_activity_date: str`
    :   Date of the last activity associated with this lead

    `last_modified_by_id: str`
    :   ID of the user who last modified this lead

    `last_modified_date: str`
    :   Date and time when the lead was last modified

    `last_name: str`
    :   Last name of the lead

    `lead_source: str`
    :   Source from which this lead originated

    `mobile_phone: str`
    :   Mobile phone number of the lead

    `name: str`
    :   Full name of the lead (read-only, concatenation of first and last name)

    `number_of_employees: str`
    :   Number of employees at the lead's company

    `owner_id: str`
    :   ID of the user who owns this lead

    `phone: str`
    :   Phone number of the lead

    `postal_code: str`
    :   Postal code portion of the address

    `rating: str`
    :   Rating of the lead (e.g., Hot, Warm, Cold)

    `state: str`
    :   State or province portion of the address

    `status: str`
    :   Current status of the lead in the sales process

    `street: str`
    :   Street address portion of the address

    `system_modstamp: str`
    :   System timestamp when the record was last modified

    `title: str`
    :   Job title of the lead

    `website: str`
    :   Website URL for the lead's company

`NotesApiSearchParams(*args, **kwargs)`
:   Parameters for notes.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`NotesGetParams(*args, **kwargs)`
:   Parameters for notes.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

`NotesListParams(*args, **kwargs)`
:   Parameters for notes.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`OpportunitiesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesEqCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesGtCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesGteCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesLtCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesLteCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesInCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesNotCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesAndCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesOrCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesAnyCondition]`
    :   The type of the None singleton.

`OpportunitiesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesAnyValueFilter`
    :   The type of the None singleton.

`OpportunitiesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Any`
    :   ID of the account associated with this opportunity

    `amount: Any`
    :   Estimated total sale amount

    `campaign_id: Any`
    :   ID of the campaign that generated this opportunity

    `close_date: Any`
    :   Expected close date for the opportunity

    `contact_id: Any`
    :   ID of the primary contact for this opportunity

    `created_by_id: Any`
    :   ID of the user who created this opportunity

    `created_date: Any`
    :   Date and time when the opportunity was created

    `description: Any`
    :   Text description of the opportunity

    `expected_revenue: Any`
    :   Expected revenue based on amount and probability

    `forecast_category: Any`
    :   Forecast category for this opportunity

    `forecast_category_name: Any`
    :   Name of the forecast category

    `id: Any`
    :   Unique identifier for the opportunity record

    `is_closed: Any`
    :   Whether the opportunity is closed

    `is_deleted: Any`
    :   Whether the opportunity has been moved to the Recycle Bin

    `is_won: Any`
    :   Whether the opportunity was won

    `last_activity_date: Any`
    :   Date of the last activity associated with this opportunity

    `last_modified_by_id: Any`
    :   ID of the user who last modified this opportunity

    `last_modified_date: Any`
    :   Date and time when the opportunity was last modified

    `lead_source: Any`
    :   Source from which this opportunity originated

    `name: Any`
    :   Name of the opportunity

    `next_step: Any`
    :   Description of the next step in closing the opportunity

    `owner_id: Any`
    :   ID of the user who owns this opportunity

    `probability: Any`
    :   Likelihood of closing the opportunity (percentage)

    `stage_name: Any`
    :   Current stage of the opportunity in the sales process

    `system_modstamp: Any`
    :   System timestamp when the record was last modified

    `type_: Any`
    :   Type of opportunity (e.g., New Business, Existing Business)

`OpportunitiesApiSearchParams(*args, **kwargs)`
:   Parameters for opportunities.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`OpportunitiesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesAnyValueFilter`
    :   The type of the None singleton.

`OpportunitiesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesSearchFilter`
    :   The type of the None singleton.

`OpportunitiesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesStringFilter`
    :   The type of the None singleton.

`OpportunitiesGetParams(*args, **kwargs)`
:   Parameters for opportunities.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

`OpportunitiesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesSearchFilter`
    :   The type of the None singleton.

`OpportunitiesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesSearchFilter`
    :   The type of the None singleton.

`OpportunitiesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesInFilter`
    :   The type of the None singleton.

`OpportunitiesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: list[str]`
    :   ID of the account associated with this opportunity

    `amount: list[float]`
    :   Estimated total sale amount

    `campaign_id: list[str]`
    :   ID of the campaign that generated this opportunity

    `close_date: list[str]`
    :   Expected close date for the opportunity

    `contact_id: list[str]`
    :   ID of the primary contact for this opportunity

    `created_by_id: list[str]`
    :   ID of the user who created this opportunity

    `created_date: list[str]`
    :   Date and time when the opportunity was created

    `description: list[str]`
    :   Text description of the opportunity

    `expected_revenue: list[float]`
    :   Expected revenue based on amount and probability

    `forecast_category: list[str]`
    :   Forecast category for this opportunity

    `forecast_category_name: list[str]`
    :   Name of the forecast category

    `id: list[str]`
    :   Unique identifier for the opportunity record

    `is_closed: list[bool]`
    :   Whether the opportunity is closed

    `is_deleted: list[bool]`
    :   Whether the opportunity has been moved to the Recycle Bin

    `is_won: list[bool]`
    :   Whether the opportunity was won

    `last_activity_date: list[str]`
    :   Date of the last activity associated with this opportunity

    `last_modified_by_id: list[str]`
    :   ID of the user who last modified this opportunity

    `last_modified_date: list[str]`
    :   Date and time when the opportunity was last modified

    `lead_source: list[str]`
    :   Source from which this opportunity originated

    `name: list[str]`
    :   Name of the opportunity

    `next_step: list[str]`
    :   Description of the next step in closing the opportunity

    `owner_id: list[str]`
    :   ID of the user who owns this opportunity

    `probability: list[float]`
    :   Likelihood of closing the opportunity (percentage)

    `stage_name: list[str]`
    :   Current stage of the opportunity in the sales process

    `system_modstamp: list[str]`
    :   System timestamp when the record was last modified

    `type_: list[str]`
    :   Type of opportunity (e.g., New Business, Existing Business)

`OpportunitiesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesStringFilter`
    :   The type of the None singleton.

`OpportunitiesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesStringFilter`
    :   The type of the None singleton.

`OpportunitiesListParams(*args, **kwargs)`
:   Parameters for opportunities.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`OpportunitiesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesSearchFilter`
    :   The type of the None singleton.

`OpportunitiesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesSearchFilter`
    :   The type of the None singleton.

`OpportunitiesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesSearchFilter`
    :   The type of the None singleton.

`OpportunitiesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesEqCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesGtCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesGteCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesLtCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesLteCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesInCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesNotCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesAndCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesOrCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesAnyCondition`
    :   The type of the None singleton.

`OpportunitiesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesEqCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesGtCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesGteCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesLtCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesLteCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesInCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesNotCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesAndCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesOrCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesAnyCondition]`
    :   The type of the None singleton.

`OpportunitiesSearchFilter(*args, **kwargs)`
:   Available fields for filtering opportunities search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str | None`
    :   ID of the account associated with this opportunity

    `amount: float | None`
    :   Estimated total sale amount

    `campaign_id: str | None`
    :   ID of the campaign that generated this opportunity

    `close_date: str | None`
    :   Expected close date for the opportunity

    `contact_id: str | None`
    :   ID of the primary contact for this opportunity

    `created_by_id: str | None`
    :   ID of the user who created this opportunity

    `created_date: str | None`
    :   Date and time when the opportunity was created

    `description: str | None`
    :   Text description of the opportunity

    `expected_revenue: float | None`
    :   Expected revenue based on amount and probability

    `forecast_category: str | None`
    :   Forecast category for this opportunity

    `forecast_category_name: str | None`
    :   Name of the forecast category

    `id: str`
    :   Unique identifier for the opportunity record

    `is_closed: bool | None`
    :   Whether the opportunity is closed

    `is_deleted: bool | None`
    :   Whether the opportunity has been moved to the Recycle Bin

    `is_won: bool | None`
    :   Whether the opportunity was won

    `last_activity_date: str | None`
    :   Date of the last activity associated with this opportunity

    `last_modified_by_id: str | None`
    :   ID of the user who last modified this opportunity

    `last_modified_date: str | None`
    :   Date and time when the opportunity was last modified

    `lead_source: str | None`
    :   Source from which this opportunity originated

    `name: str | None`
    :   Name of the opportunity

    `next_step: str | None`
    :   Description of the next step in closing the opportunity

    `owner_id: str | None`
    :   ID of the user who owns this opportunity

    `probability: float | None`
    :   Likelihood of closing the opportunity (percentage)

    `stage_name: str | None`
    :   Current stage of the opportunity in the sales process

    `system_modstamp: str | None`
    :   System timestamp when the record was last modified

    `type_: str | None`
    :   Type of opportunity (e.g., New Business, Existing Business)

`OpportunitiesSearchQuery(*args, **kwargs)`
:   Search query for opportunities entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesEqCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesGtCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesGteCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesLtCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesLteCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesInCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesNotCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesAndCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesOrCondition | airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.salesforce.types.OpportunitiesSortFilter]`
    :   The type of the None singleton.

`OpportunitiesSortFilter(*args, **kwargs)`
:   Available fields for sorting opportunities search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Literal['asc', 'desc']`
    :   ID of the account associated with this opportunity

    `amount: Literal['asc', 'desc']`
    :   Estimated total sale amount

    `campaign_id: Literal['asc', 'desc']`
    :   ID of the campaign that generated this opportunity

    `close_date: Literal['asc', 'desc']`
    :   Expected close date for the opportunity

    `contact_id: Literal['asc', 'desc']`
    :   ID of the primary contact for this opportunity

    `created_by_id: Literal['asc', 'desc']`
    :   ID of the user who created this opportunity

    `created_date: Literal['asc', 'desc']`
    :   Date and time when the opportunity was created

    `description: Literal['asc', 'desc']`
    :   Text description of the opportunity

    `expected_revenue: Literal['asc', 'desc']`
    :   Expected revenue based on amount and probability

    `forecast_category: Literal['asc', 'desc']`
    :   Forecast category for this opportunity

    `forecast_category_name: Literal['asc', 'desc']`
    :   Name of the forecast category

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the opportunity record

    `is_closed: Literal['asc', 'desc']`
    :   Whether the opportunity is closed

    `is_deleted: Literal['asc', 'desc']`
    :   Whether the opportunity has been moved to the Recycle Bin

    `is_won: Literal['asc', 'desc']`
    :   Whether the opportunity was won

    `last_activity_date: Literal['asc', 'desc']`
    :   Date of the last activity associated with this opportunity

    `last_modified_by_id: Literal['asc', 'desc']`
    :   ID of the user who last modified this opportunity

    `last_modified_date: Literal['asc', 'desc']`
    :   Date and time when the opportunity was last modified

    `lead_source: Literal['asc', 'desc']`
    :   Source from which this opportunity originated

    `name: Literal['asc', 'desc']`
    :   Name of the opportunity

    `next_step: Literal['asc', 'desc']`
    :   Description of the next step in closing the opportunity

    `owner_id: Literal['asc', 'desc']`
    :   ID of the user who owns this opportunity

    `probability: Literal['asc', 'desc']`
    :   Likelihood of closing the opportunity (percentage)

    `stage_name: Literal['asc', 'desc']`
    :   Current stage of the opportunity in the sales process

    `system_modstamp: Literal['asc', 'desc']`
    :   System timestamp when the record was last modified

    `type_: Literal['asc', 'desc']`
    :   Type of opportunity (e.g., New Business, Existing Business)

`OpportunitiesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   ID of the account associated with this opportunity

    `amount: str`
    :   Estimated total sale amount

    `campaign_id: str`
    :   ID of the campaign that generated this opportunity

    `close_date: str`
    :   Expected close date for the opportunity

    `contact_id: str`
    :   ID of the primary contact for this opportunity

    `created_by_id: str`
    :   ID of the user who created this opportunity

    `created_date: str`
    :   Date and time when the opportunity was created

    `description: str`
    :   Text description of the opportunity

    `expected_revenue: str`
    :   Expected revenue based on amount and probability

    `forecast_category: str`
    :   Forecast category for this opportunity

    `forecast_category_name: str`
    :   Name of the forecast category

    `id: str`
    :   Unique identifier for the opportunity record

    `is_closed: str`
    :   Whether the opportunity is closed

    `is_deleted: str`
    :   Whether the opportunity has been moved to the Recycle Bin

    `is_won: str`
    :   Whether the opportunity was won

    `last_activity_date: str`
    :   Date of the last activity associated with this opportunity

    `last_modified_by_id: str`
    :   ID of the user who last modified this opportunity

    `last_modified_date: str`
    :   Date and time when the opportunity was last modified

    `lead_source: str`
    :   Source from which this opportunity originated

    `name: str`
    :   Name of the opportunity

    `next_step: str`
    :   Description of the next step in closing the opportunity

    `owner_id: str`
    :   ID of the user who owns this opportunity

    `probability: str`
    :   Likelihood of closing the opportunity (percentage)

    `stage_name: str`
    :   Current stage of the opportunity in the sales process

    `system_modstamp: str`
    :   System timestamp when the record was last modified

    `type_: str`
    :   Type of opportunity (e.g., New Business, Existing Business)

`QueryListParams(*args, **kwargs)`
:   Parameters for query.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`ReportsGetParams(*args, **kwargs)`
:   Parameters for reports.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `include_details: bool`
    :   The type of the None singleton.

`ReportsListParams(*args, **kwargs)`
:   Parameters for reports.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`SobjectsListParams(*args, **kwargs)`
:   Parameters for sobjects.list operation

    ### Ancestors (in MRO)

    * builtins.dict

`TasksAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.salesforce.types.TasksEqCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksGtCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksGteCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksLtCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksLteCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksInCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksNotCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksAndCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksOrCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksAnyCondition]`
    :   The type of the None singleton.

`TasksAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.salesforce.types.TasksAnyValueFilter`
    :   The type of the None singleton.

`TasksAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Any`
    :   ID of the account associated with this task

    `activity_date: Any`
    :   Due date for the task

    `call_disposition: Any`
    :   Result of the call, if this task represents a call

    `call_duration_in_seconds: Any`
    :   Duration of the call in seconds

    `call_type: Any`
    :   Type of call (Inbound, Outbound, Internal)

    `completed_date_time: Any`
    :   Date and time when the task was completed

    `created_by_id: Any`
    :   ID of the user who created this task

    `created_date: Any`
    :   Date and time when the task was created

    `description: Any`
    :   Text description or notes about the task

    `id: Any`
    :   Unique identifier for the task record

    `is_closed: Any`
    :   Whether the task has been completed

    `is_deleted: Any`
    :   Whether the task has been moved to the Recycle Bin

    `is_high_priority: Any`
    :   Whether the task is marked as high priority

    `last_modified_by_id: Any`
    :   ID of the user who last modified this task

    `last_modified_date: Any`
    :   Date and time when the task was last modified

    `owner_id: Any`
    :   ID of the user who owns this task

    `priority: Any`
    :   Priority level of the task (High, Normal, Low)

    `status: Any`
    :   Current status of the task

    `subject: Any`
    :   Subject or title of the task

    `system_modstamp: Any`
    :   System timestamp when the record was last modified

    `task_subtype: Any`
    :   Subtype of the task (e.g., Call, Email, Task)

    `type_: Any`
    :   Type of task

    `what_id: Any`
    :   ID of the related object (Account, Opportunity, etc.)

    `who_id: Any`
    :   ID of the related person (Contact or Lead)

`TasksApiSearchParams(*args, **kwargs)`
:   Parameters for tasks.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`TasksContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.salesforce.types.TasksAnyValueFilter`
    :   The type of the None singleton.

`TasksEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.salesforce.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.salesforce.types.TasksStringFilter`
    :   The type of the None singleton.

`TasksGetParams(*args, **kwargs)`
:   Parameters for tasks.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fields: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

`TasksGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.salesforce.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.salesforce.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.salesforce.types.TasksInFilter`
    :   The type of the None singleton.

`TasksInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: list[str]`
    :   ID of the account associated with this task

    `activity_date: list[str]`
    :   Due date for the task

    `call_disposition: list[str]`
    :   Result of the call, if this task represents a call

    `call_duration_in_seconds: list[int]`
    :   Duration of the call in seconds

    `call_type: list[str]`
    :   Type of call (Inbound, Outbound, Internal)

    `completed_date_time: list[str]`
    :   Date and time when the task was completed

    `created_by_id: list[str]`
    :   ID of the user who created this task

    `created_date: list[str]`
    :   Date and time when the task was created

    `description: list[str]`
    :   Text description or notes about the task

    `id: list[str]`
    :   Unique identifier for the task record

    `is_closed: list[bool]`
    :   Whether the task has been completed

    `is_deleted: list[bool]`
    :   Whether the task has been moved to the Recycle Bin

    `is_high_priority: list[bool]`
    :   Whether the task is marked as high priority

    `last_modified_by_id: list[str]`
    :   ID of the user who last modified this task

    `last_modified_date: list[str]`
    :   Date and time when the task was last modified

    `owner_id: list[str]`
    :   ID of the user who owns this task

    `priority: list[str]`
    :   Priority level of the task (High, Normal, Low)

    `status: list[str]`
    :   Current status of the task

    `subject: list[str]`
    :   Subject or title of the task

    `system_modstamp: list[str]`
    :   System timestamp when the record was last modified

    `task_subtype: list[str]`
    :   Subtype of the task (e.g., Call, Email, Task)

    `type_: list[str]`
    :   Type of task

    `what_id: list[str]`
    :   ID of the related object (Account, Opportunity, etc.)

    `who_id: list[str]`
    :   ID of the related person (Contact or Lead)

`TasksKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.salesforce.types.TasksStringFilter`
    :   The type of the None singleton.

`TasksLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.salesforce.types.TasksStringFilter`
    :   The type of the None singleton.

`TasksListParams(*args, **kwargs)`
:   Parameters for tasks.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `q: str`
    :   The type of the None singleton.

`TasksLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.salesforce.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.salesforce.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.salesforce.types.TasksSearchFilter`
    :   The type of the None singleton.

`TasksNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.salesforce.types.TasksEqCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksGtCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksGteCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksLtCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksLteCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksInCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksNotCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksAndCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksOrCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksAnyCondition`
    :   The type of the None singleton.

`TasksOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.salesforce.types.TasksEqCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksGtCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksGteCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksLtCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksLteCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksInCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksNotCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksAndCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksOrCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksAnyCondition]`
    :   The type of the None singleton.

`TasksSearchFilter(*args, **kwargs)`
:   Available fields for filtering tasks search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str | None`
    :   ID of the account associated with this task

    `activity_date: str | None`
    :   Due date for the task

    `call_disposition: str | None`
    :   Result of the call, if this task represents a call

    `call_duration_in_seconds: int | None`
    :   Duration of the call in seconds

    `call_type: str | None`
    :   Type of call (Inbound, Outbound, Internal)

    `completed_date_time: str | None`
    :   Date and time when the task was completed

    `created_by_id: str | None`
    :   ID of the user who created this task

    `created_date: str | None`
    :   Date and time when the task was created

    `description: str | None`
    :   Text description or notes about the task

    `id: str`
    :   Unique identifier for the task record

    `is_closed: bool | None`
    :   Whether the task has been completed

    `is_deleted: bool | None`
    :   Whether the task has been moved to the Recycle Bin

    `is_high_priority: bool | None`
    :   Whether the task is marked as high priority

    `last_modified_by_id: str | None`
    :   ID of the user who last modified this task

    `last_modified_date: str | None`
    :   Date and time when the task was last modified

    `owner_id: str | None`
    :   ID of the user who owns this task

    `priority: str | None`
    :   Priority level of the task (High, Normal, Low)

    `status: str | None`
    :   Current status of the task

    `subject: str | None`
    :   Subject or title of the task

    `system_modstamp: str | None`
    :   System timestamp when the record was last modified

    `task_subtype: str | None`
    :   Subtype of the task (e.g., Call, Email, Task)

    `type_: str | None`
    :   Type of task

    `what_id: str | None`
    :   ID of the related object (Account, Opportunity, etc.)

    `who_id: str | None`
    :   ID of the related person (Contact or Lead)

`TasksSearchQuery(*args, **kwargs)`
:   Search query for tasks entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.salesforce.types.TasksEqCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksNeqCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksGtCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksGteCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksLtCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksLteCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksInCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksLikeCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksFuzzyCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksKeywordCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksContainsCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksNotCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksAndCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksOrCondition | airbyte_agent_sdk.connectors.salesforce.types.TasksAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.salesforce.types.TasksSortFilter]`
    :   The type of the None singleton.

`TasksSortFilter(*args, **kwargs)`
:   Available fields for sorting tasks search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Literal['asc', 'desc']`
    :   ID of the account associated with this task

    `activity_date: Literal['asc', 'desc']`
    :   Due date for the task

    `call_disposition: Literal['asc', 'desc']`
    :   Result of the call, if this task represents a call

    `call_duration_in_seconds: Literal['asc', 'desc']`
    :   Duration of the call in seconds

    `call_type: Literal['asc', 'desc']`
    :   Type of call (Inbound, Outbound, Internal)

    `completed_date_time: Literal['asc', 'desc']`
    :   Date and time when the task was completed

    `created_by_id: Literal['asc', 'desc']`
    :   ID of the user who created this task

    `created_date: Literal['asc', 'desc']`
    :   Date and time when the task was created

    `description: Literal['asc', 'desc']`
    :   Text description or notes about the task

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the task record

    `is_closed: Literal['asc', 'desc']`
    :   Whether the task has been completed

    `is_deleted: Literal['asc', 'desc']`
    :   Whether the task has been moved to the Recycle Bin

    `is_high_priority: Literal['asc', 'desc']`
    :   Whether the task is marked as high priority

    `last_modified_by_id: Literal['asc', 'desc']`
    :   ID of the user who last modified this task

    `last_modified_date: Literal['asc', 'desc']`
    :   Date and time when the task was last modified

    `owner_id: Literal['asc', 'desc']`
    :   ID of the user who owns this task

    `priority: Literal['asc', 'desc']`
    :   Priority level of the task (High, Normal, Low)

    `status: Literal['asc', 'desc']`
    :   Current status of the task

    `subject: Literal['asc', 'desc']`
    :   Subject or title of the task

    `system_modstamp: Literal['asc', 'desc']`
    :   System timestamp when the record was last modified

    `task_subtype: Literal['asc', 'desc']`
    :   Subtype of the task (e.g., Call, Email, Task)

    `type_: Literal['asc', 'desc']`
    :   Type of task

    `what_id: Literal['asc', 'desc']`
    :   ID of the related object (Account, Opportunity, etc.)

    `who_id: Literal['asc', 'desc']`
    :   ID of the related person (Contact or Lead)

`TasksStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   ID of the account associated with this task

    `activity_date: str`
    :   Due date for the task

    `call_disposition: str`
    :   Result of the call, if this task represents a call

    `call_duration_in_seconds: str`
    :   Duration of the call in seconds

    `call_type: str`
    :   Type of call (Inbound, Outbound, Internal)

    `completed_date_time: str`
    :   Date and time when the task was completed

    `created_by_id: str`
    :   ID of the user who created this task

    `created_date: str`
    :   Date and time when the task was created

    `description: str`
    :   Text description or notes about the task

    `id: str`
    :   Unique identifier for the task record

    `is_closed: str`
    :   Whether the task has been completed

    `is_deleted: str`
    :   Whether the task has been moved to the Recycle Bin

    `is_high_priority: str`
    :   Whether the task is marked as high priority

    `last_modified_by_id: str`
    :   ID of the user who last modified this task

    `last_modified_date: str`
    :   Date and time when the task was last modified

    `owner_id: str`
    :   ID of the user who owns this task

    `priority: str`
    :   Priority level of the task (High, Normal, Low)

    `status: str`
    :   Current status of the task

    `subject: str`
    :   Subject or title of the task

    `system_modstamp: str`
    :   System timestamp when the record was last modified

    `task_subtype: str`
    :   Subtype of the task (e.g., Call, Email, Task)

    `type_: str`
    :   Type of task

    `what_id: str`
    :   ID of the related object (Account, Opportunity, etc.)

    `who_id: str`
    :   ID of the related person (Contact or Lead)