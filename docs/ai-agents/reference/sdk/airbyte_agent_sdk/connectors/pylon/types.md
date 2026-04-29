---
id: airbyte_agent_sdk-connectors-pylon-types
title: airbyte_agent_sdk.connectors.pylon.types
---

Module airbyte_agent_sdk.connectors.pylon.types
===============================================
Type definitions for pylon connector.

Classes
-------

<a id="AccountsAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.pylon.types.AccountsEqCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsGtCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsGteCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsLtCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsLteCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsInCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsNotCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsAndCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsOrCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsAnyCondition]`
    :   The type of the None singleton.

<a id="AccountsAnyCondition"></a>

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

    `any: airbyte_agent_sdk.connectors.pylon.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountsAnyValueFilter"></a>

`AccountsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   Timestamp when the account was created, in ISO 8601 format

    `domain: Any`
    :   Primary domain associated with the account

    `id: Any`
    :   Unique identifier for the account

    `is_disabled: Any`
    :   Whether the account has been disabled

    `latest_customer_activity_time: Any`
    :   Timestamp of the most recent activity from this account, in ISO 8601 format

    `name: Any`
    :   Name of the account (customer organization)

    `primary_domain: Any`
    :   Canonical primary domain for the account

    `type_: Any`
    :   Classification of the account (e.g. customer, prospect)

<a id="AccountsContainsCondition"></a>

`AccountsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pylon.types.AccountsAnyValueFilter`
    :   The type of the None singleton.

<a id="AccountsCreateParams"></a>

`AccountsCreateParams(*args, **kwargs)`
:   Parameters for accounts.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `domains: list[str]`
    :   The type of the None singleton.

    `logo_url: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `owner_id: str`
    :   The type of the None singleton.

    `primary_domain: str`
    :   The type of the None singleton.

    `tags: list[str]`
    :   The type of the None singleton.

<a id="AccountsEqCondition"></a>

`AccountsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pylon.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsFuzzyCondition"></a>

`AccountsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pylon.types.AccountsStringFilter`
    :   The type of the None singleton.

<a id="AccountsGetParams"></a>

`AccountsGetParams(*args, **kwargs)`
:   Parameters for accounts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="AccountsGtCondition"></a>

`AccountsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pylon.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsGteCondition"></a>

`AccountsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pylon.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsInCondition"></a>

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

    `in: airbyte_agent_sdk.connectors.pylon.types.AccountsInFilter`
    :   The type of the None singleton.

<a id="AccountsInFilter"></a>

`AccountsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   Timestamp when the account was created, in ISO 8601 format

    `domain: list[str]`
    :   Primary domain associated with the account

    `id: list[str]`
    :   Unique identifier for the account

    `is_disabled: list[bool]`
    :   Whether the account has been disabled

    `latest_customer_activity_time: list[str]`
    :   Timestamp of the most recent activity from this account, in ISO 8601 format

    `name: list[str]`
    :   Name of the account (customer organization)

    `primary_domain: list[str]`
    :   Canonical primary domain for the account

    `type_: list[str]`
    :   Classification of the account (e.g. customer, prospect)

<a id="AccountsKeywordCondition"></a>

`AccountsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pylon.types.AccountsStringFilter`
    :   The type of the None singleton.

<a id="AccountsLikeCondition"></a>

`AccountsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pylon.types.AccountsStringFilter`
    :   The type of the None singleton.

<a id="AccountsListParams"></a>

`AccountsListParams(*args, **kwargs)`
:   Parameters for accounts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

<a id="AccountsLtCondition"></a>

`AccountsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pylon.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsLteCondition"></a>

`AccountsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pylon.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsNeqCondition"></a>

`AccountsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pylon.types.AccountsSearchFilter`
    :   The type of the None singleton.

<a id="AccountsNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.pylon.types.AccountsEqCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsGtCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsGteCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsLtCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsLteCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsInCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsNotCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsAndCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsOrCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsAnyCondition`
    :   The type of the None singleton.

<a id="AccountsOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.pylon.types.AccountsEqCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsGtCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsGteCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsLtCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsLteCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsInCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsNotCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsAndCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsOrCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsAnyCondition]`
    :   The type of the None singleton.

<a id="AccountsSearchFilter"></a>

`AccountsSearchFilter(*args, **kwargs)`
:   Available fields for filtering accounts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the account was created, in ISO 8601 format

    `domain: str | None`
    :   Primary domain associated with the account

    `id: str`
    :   Unique identifier for the account

    `is_disabled: bool | None`
    :   Whether the account has been disabled

    `latest_customer_activity_time: str | None`
    :   Timestamp of the most recent activity from this account, in ISO 8601 format

    `name: str | None`
    :   Name of the account (customer organization)

    `primary_domain: str | None`
    :   Canonical primary domain for the account

    `type_: str | None`
    :   Classification of the account (e.g. customer, prospect)

<a id="AccountsSearchQuery"></a>

`AccountsSearchQuery(*args, **kwargs)`
:   Search query for accounts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pylon.types.AccountsEqCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsGtCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsGteCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsLtCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsLteCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsInCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsNotCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsAndCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsOrCondition | airbyte_agent_sdk.connectors.pylon.types.AccountsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pylon.types.AccountsSortFilter]`
    :   The type of the None singleton.

<a id="AccountsSortFilter"></a>

`AccountsSortFilter(*args, **kwargs)`
:   Available fields for sorting accounts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the account was created, in ISO 8601 format

    `domain: Literal['asc', 'desc']`
    :   Primary domain associated with the account

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the account

    `is_disabled: Literal['asc', 'desc']`
    :   Whether the account has been disabled

    `latest_customer_activity_time: Literal['asc', 'desc']`
    :   Timestamp of the most recent activity from this account, in ISO 8601 format

    `name: Literal['asc', 'desc']`
    :   Name of the account (customer organization)

    `primary_domain: Literal['asc', 'desc']`
    :   Canonical primary domain for the account

    `type_: Literal['asc', 'desc']`
    :   Classification of the account (e.g. customer, prospect)

<a id="AccountsStringFilter"></a>

`AccountsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   Timestamp when the account was created, in ISO 8601 format

    `domain: str`
    :   Primary domain associated with the account

    `id: str`
    :   Unique identifier for the account

    `is_disabled: str`
    :   Whether the account has been disabled

    `latest_customer_activity_time: str`
    :   Timestamp of the most recent activity from this account, in ISO 8601 format

    `name: str`
    :   Name of the account (customer organization)

    `primary_domain: str`
    :   Canonical primary domain for the account

    `type_: str`
    :   Classification of the account (e.g. customer, prospect)

<a id="AccountsUpdateParams"></a>

`AccountsUpdateParams(*args, **kwargs)`
:   Parameters for accounts.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `domains: list[str]`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `is_disabled: bool`
    :   The type of the None singleton.

    `logo_url: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `owner_id: str`
    :   The type of the None singleton.

    `primary_domain: str`
    :   The type of the None singleton.

    `tags: list[str]`
    :   The type of the None singleton.

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

<a id="ArticlesCreateParams"></a>

`ArticlesCreateParams(*args, **kwargs)`
:   Parameters for articles.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_user_id: str`
    :   The type of the None singleton.

    `body_html: str`
    :   The type of the None singleton.

    `is_published: bool`
    :   The type of the None singleton.

    `kb_id: str`
    :   The type of the None singleton.

    `slug: str`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="ArticlesUpdateParams"></a>

`ArticlesUpdateParams(*args, **kwargs)`
:   Parameters for articles.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `article_id: str`
    :   The type of the None singleton.

    `body_html: str`
    :   The type of the None singleton.

    `kb_id: str`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="CollectionsCreateParams"></a>

`CollectionsCreateParams(*args, **kwargs)`
:   Parameters for collections.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description: str`
    :   The type of the None singleton.

    `kb_id: str`
    :   The type of the None singleton.

    `slug: str`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="ContactsAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.pylon.types.ContactsEqCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsGtCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsGteCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsLtCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsLteCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsInCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsNotCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsAndCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsOrCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsAnyCondition]`
    :   The type of the None singleton.

<a id="ContactsAnyCondition"></a>

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

    `any: airbyte_agent_sdk.connectors.pylon.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

<a id="ContactsAnyValueFilter"></a>

`ContactsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email: Any`
    :   Primary email address of the contact

    `id: Any`
    :   Unique identifier for the contact

    `name: Any`
    :   Full name of the contact

    `portal_role: Any`
    :   Role the contact has in the customer portal

    `primary_phone_number: Any`
    :   Primary phone number of the contact

<a id="ContactsContainsCondition"></a>

`ContactsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pylon.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

<a id="ContactsCreateParams"></a>

`ContactsCreateParams(*args, **kwargs)`
:   Parameters for contacts.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `avatar_url: str`
    :   The type of the None singleton.

    `email: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="ContactsEqCondition"></a>

`ContactsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pylon.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsFuzzyCondition"></a>

`ContactsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pylon.types.ContactsStringFilter`
    :   The type of the None singleton.

<a id="ContactsGetParams"></a>

`ContactsGetParams(*args, **kwargs)`
:   Parameters for contacts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ContactsGtCondition"></a>

`ContactsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pylon.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsGteCondition"></a>

`ContactsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pylon.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsInCondition"></a>

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

    `in: airbyte_agent_sdk.connectors.pylon.types.ContactsInFilter`
    :   The type of the None singleton.

<a id="ContactsInFilter"></a>

`ContactsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email: list[str]`
    :   Primary email address of the contact

    `id: list[str]`
    :   Unique identifier for the contact

    `name: list[str]`
    :   Full name of the contact

    `portal_role: list[str]`
    :   Role the contact has in the customer portal

    `primary_phone_number: list[str]`
    :   Primary phone number of the contact

<a id="ContactsKeywordCondition"></a>

`ContactsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pylon.types.ContactsStringFilter`
    :   The type of the None singleton.

<a id="ContactsLikeCondition"></a>

`ContactsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pylon.types.ContactsStringFilter`
    :   The type of the None singleton.

<a id="ContactsListParams"></a>

`ContactsListParams(*args, **kwargs)`
:   Parameters for contacts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

<a id="ContactsLtCondition"></a>

`ContactsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pylon.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsLteCondition"></a>

`ContactsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pylon.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsNeqCondition"></a>

`ContactsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pylon.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.pylon.types.ContactsEqCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsGtCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsGteCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsLtCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsLteCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsInCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsNotCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsAndCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsOrCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsAnyCondition`
    :   The type of the None singleton.

<a id="ContactsOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.pylon.types.ContactsEqCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsGtCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsGteCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsLtCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsLteCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsInCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsNotCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsAndCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsOrCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsAnyCondition]`
    :   The type of the None singleton.

<a id="ContactsSearchFilter"></a>

`ContactsSearchFilter(*args, **kwargs)`
:   Available fields for filtering contacts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email: str | None`
    :   Primary email address of the contact

    `id: str`
    :   Unique identifier for the contact

    `name: str | None`
    :   Full name of the contact

    `portal_role: str | None`
    :   Role the contact has in the customer portal

    `primary_phone_number: str | None`
    :   Primary phone number of the contact

<a id="ContactsSearchQuery"></a>

`ContactsSearchQuery(*args, **kwargs)`
:   Search query for contacts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pylon.types.ContactsEqCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsGtCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsGteCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsLtCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsLteCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsInCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsNotCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsAndCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsOrCondition | airbyte_agent_sdk.connectors.pylon.types.ContactsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pylon.types.ContactsSortFilter]`
    :   The type of the None singleton.

<a id="ContactsSortFilter"></a>

`ContactsSortFilter(*args, **kwargs)`
:   Available fields for sorting contacts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email: Literal['asc', 'desc']`
    :   Primary email address of the contact

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the contact

    `name: Literal['asc', 'desc']`
    :   Full name of the contact

    `portal_role: Literal['asc', 'desc']`
    :   Role the contact has in the customer portal

    `primary_phone_number: Literal['asc', 'desc']`
    :   Primary phone number of the contact

<a id="ContactsStringFilter"></a>

`ContactsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email: str`
    :   Primary email address of the contact

    `id: str`
    :   Unique identifier for the contact

    `name: str`
    :   Full name of the contact

    `portal_role: str`
    :   Role the contact has in the customer portal

    `primary_phone_number: str`
    :   Primary phone number of the contact

<a id="ContactsUpdateParams"></a>

`ContactsUpdateParams(*args, **kwargs)`
:   Parameters for contacts.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `email: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="CustomFieldsAndCondition"></a>

`CustomFieldsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.pylon.types.CustomFieldsEqCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsGtCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsGteCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsLtCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsLteCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsInCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsNotCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsAndCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsOrCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsAnyCondition]`
    :   The type of the None singleton.

<a id="CustomFieldsAnyCondition"></a>

`CustomFieldsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.pylon.types.CustomFieldsAnyValueFilter`
    :   The type of the None singleton.

<a id="CustomFieldsAnyValueFilter"></a>

`CustomFieldsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   Timestamp when the custom field was created, in ISO 8601 format

    `id: Any`
    :   Unique identifier for the custom field

    `is_read_only: Any`
    :   Whether the custom field is read-only

    `label: Any`
    :   Display label of the custom field

    `object_type: Any`
    :   Type of object this custom field applies to (e.g. issue, account)

    `slug: Any`
    :   URL-safe identifier for the custom field

    `type_: Any`
    :   Data type of the custom field (e.g. text, select)

<a id="CustomFieldsContainsCondition"></a>

`CustomFieldsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pylon.types.CustomFieldsAnyValueFilter`
    :   The type of the None singleton.

<a id="CustomFieldsEqCondition"></a>

`CustomFieldsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pylon.types.CustomFieldsSearchFilter`
    :   The type of the None singleton.

<a id="CustomFieldsFuzzyCondition"></a>

`CustomFieldsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pylon.types.CustomFieldsStringFilter`
    :   The type of the None singleton.

<a id="CustomFieldsGetParams"></a>

`CustomFieldsGetParams(*args, **kwargs)`
:   Parameters for custom_fields.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CustomFieldsGtCondition"></a>

`CustomFieldsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pylon.types.CustomFieldsSearchFilter`
    :   The type of the None singleton.

<a id="CustomFieldsGteCondition"></a>

`CustomFieldsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pylon.types.CustomFieldsSearchFilter`
    :   The type of the None singleton.

<a id="CustomFieldsInCondition"></a>

`CustomFieldsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.pylon.types.CustomFieldsInFilter`
    :   The type of the None singleton.

<a id="CustomFieldsInFilter"></a>

`CustomFieldsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   Timestamp when the custom field was created, in ISO 8601 format

    `id: list[str]`
    :   Unique identifier for the custom field

    `is_read_only: list[bool]`
    :   Whether the custom field is read-only

    `label: list[str]`
    :   Display label of the custom field

    `object_type: list[str]`
    :   Type of object this custom field applies to (e.g. issue, account)

    `slug: list[str]`
    :   URL-safe identifier for the custom field

    `type_: list[str]`
    :   Data type of the custom field (e.g. text, select)

<a id="CustomFieldsKeywordCondition"></a>

`CustomFieldsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pylon.types.CustomFieldsStringFilter`
    :   The type of the None singleton.

<a id="CustomFieldsLikeCondition"></a>

`CustomFieldsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pylon.types.CustomFieldsStringFilter`
    :   The type of the None singleton.

<a id="CustomFieldsListParams"></a>

`CustomFieldsListParams(*args, **kwargs)`
:   Parameters for custom_fields.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `object_type: str`
    :   The type of the None singleton.

<a id="CustomFieldsLtCondition"></a>

`CustomFieldsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pylon.types.CustomFieldsSearchFilter`
    :   The type of the None singleton.

<a id="CustomFieldsLteCondition"></a>

`CustomFieldsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pylon.types.CustomFieldsSearchFilter`
    :   The type of the None singleton.

<a id="CustomFieldsNeqCondition"></a>

`CustomFieldsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pylon.types.CustomFieldsSearchFilter`
    :   The type of the None singleton.

<a id="CustomFieldsNotCondition"></a>

`CustomFieldsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.pylon.types.CustomFieldsEqCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsGtCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsGteCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsLtCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsLteCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsInCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsNotCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsAndCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsOrCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsAnyCondition`
    :   The type of the None singleton.

<a id="CustomFieldsOrCondition"></a>

`CustomFieldsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.pylon.types.CustomFieldsEqCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsGtCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsGteCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsLtCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsLteCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsInCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsNotCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsAndCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsOrCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsAnyCondition]`
    :   The type of the None singleton.

<a id="CustomFieldsSearchFilter"></a>

`CustomFieldsSearchFilter(*args, **kwargs)`
:   Available fields for filtering custom_fields search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the custom field was created, in ISO 8601 format

    `id: str`
    :   Unique identifier for the custom field

    `is_read_only: bool | None`
    :   Whether the custom field is read-only

    `label: str | None`
    :   Display label of the custom field

    `object_type: str | None`
    :   Type of object this custom field applies to (e.g. issue, account)

    `slug: str | None`
    :   URL-safe identifier for the custom field

    `type_: str | None`
    :   Data type of the custom field (e.g. text, select)

<a id="CustomFieldsSearchQuery"></a>

`CustomFieldsSearchQuery(*args, **kwargs)`
:   Search query for custom_fields entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pylon.types.CustomFieldsEqCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsGtCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsGteCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsLtCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsLteCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsInCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsNotCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsAndCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsOrCondition | airbyte_agent_sdk.connectors.pylon.types.CustomFieldsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pylon.types.CustomFieldsSortFilter]`
    :   The type of the None singleton.

<a id="CustomFieldsSortFilter"></a>

`CustomFieldsSortFilter(*args, **kwargs)`
:   Available fields for sorting custom_fields search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the custom field was created, in ISO 8601 format

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the custom field

    `is_read_only: Literal['asc', 'desc']`
    :   Whether the custom field is read-only

    `label: Literal['asc', 'desc']`
    :   Display label of the custom field

    `object_type: Literal['asc', 'desc']`
    :   Type of object this custom field applies to (e.g. issue, account)

    `slug: Literal['asc', 'desc']`
    :   URL-safe identifier for the custom field

    `type_: Literal['asc', 'desc']`
    :   Data type of the custom field (e.g. text, select)

<a id="CustomFieldsStringFilter"></a>

`CustomFieldsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   Timestamp when the custom field was created, in ISO 8601 format

    `id: str`
    :   Unique identifier for the custom field

    `is_read_only: str`
    :   Whether the custom field is read-only

    `label: str`
    :   Display label of the custom field

    `object_type: str`
    :   Type of object this custom field applies to (e.g. issue, account)

    `slug: str`
    :   URL-safe identifier for the custom field

    `type_: str`
    :   Data type of the custom field (e.g. text, select)

<a id="IssueAssignmentsUpdateParams"></a>

`IssueAssignmentsUpdateParams(*args, **kwargs)`
:   Parameters for issue_assignments.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee_id: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `team_id: str`
    :   The type of the None singleton.

<a id="IssueNotesCreateParams"></a>

`IssueNotesCreateParams(*args, **kwargs)`
:   Parameters for issue_notes.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `body_html: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `message_id: str`
    :   The type of the None singleton.

    `thread_id: str`
    :   The type of the None singleton.

<a id="IssueRepliesCreateParams"></a>

`IssueRepliesCreateParams(*args, **kwargs)`
:   Parameters for issue_replies.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `attachment_urls: list[str]`
    :   The type of the None singleton.

    `body_html: str`
    :   The type of the None singleton.

    `contact_id: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `message_id: str`
    :   The type of the None singleton.

    `user_id: str`
    :   The type of the None singleton.

<a id="IssueStatusesUpdateParams"></a>

`IssueStatusesUpdateParams(*args, **kwargs)`
:   Parameters for issue_statuses.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `state: str`
    :   The type of the None singleton.

<a id="IssueThreadsCreateParams"></a>

`IssueThreadsCreateParams(*args, **kwargs)`
:   Parameters for issue_threads.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `name: str`
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

    `and: list[airbyte_agent_sdk.connectors.pylon.types.IssuesEqCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesGtCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesGteCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesLtCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesLteCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesInCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesNotCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesAndCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesOrCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.pylon.types.IssuesAnyValueFilter`
    :   The type of the None singleton.

<a id="IssuesAnyValueFilter"></a>

`IssuesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   Timestamp when the issue was created, in ISO 8601 format

    `customer_portal_visible: Any`
    :   Whether the issue is visible in the customer portal

    `id: Any`
    :   Unique identifier for the issue

    `latest_message_time: Any`
    :   Timestamp of the most recent message on the issue, in ISO 8601 format

    `number: Any`
    :   Human-readable issue number within the workspace

    `resolution_time: Any`
    :   Timestamp when the issue was resolved, in ISO 8601 format

    `snoozed_until_time: Any`
    :   Timestamp the issue is snoozed until, in ISO 8601 format

    `source: Any`
    :   Channel the issue originated from (e.g. email, slack)

    `state: Any`
    :   Current state of the issue (e.g. new, in_progress, closed)

    `title: Any`
    :   Title of the issue

    `type_: Any`
    :   Type classification of the issue

<a id="IssuesContainsCondition"></a>

`IssuesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pylon.types.IssuesAnyValueFilter`
    :   The type of the None singleton.

<a id="IssuesCreateParams"></a>

`IssuesCreateParams(*args, **kwargs)`
:   Parameters for issues.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `assignee_id: str`
    :   The type of the None singleton.

    `body_html: str`
    :   The type of the None singleton.

    `priority: str`
    :   The type of the None singleton.

    `requester_email: str`
    :   The type of the None singleton.

    `requester_name: str`
    :   The type of the None singleton.

    `tags: list[str]`
    :   The type of the None singleton.

    `team_id: str`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="IssuesDeleteParams"></a>

`IssuesDeleteParams(*args, **kwargs)`
:   Parameters for issues.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="IssuesEqCondition"></a>

`IssuesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pylon.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesFuzzyCondition"></a>

`IssuesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pylon.types.IssuesStringFilter`
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

    `gt: airbyte_agent_sdk.connectors.pylon.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesGteCondition"></a>

`IssuesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pylon.types.IssuesSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.pylon.types.IssuesInFilter`
    :   The type of the None singleton.

<a id="IssuesInFilter"></a>

`IssuesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   Timestamp when the issue was created, in ISO 8601 format

    `customer_portal_visible: list[bool]`
    :   Whether the issue is visible in the customer portal

    `id: list[str]`
    :   Unique identifier for the issue

    `latest_message_time: list[str]`
    :   Timestamp of the most recent message on the issue, in ISO 8601 format

    `number: list[int]`
    :   Human-readable issue number within the workspace

    `resolution_time: list[str]`
    :   Timestamp when the issue was resolved, in ISO 8601 format

    `snoozed_until_time: list[str]`
    :   Timestamp the issue is snoozed until, in ISO 8601 format

    `source: list[str]`
    :   Channel the issue originated from (e.g. email, slack)

    `state: list[str]`
    :   Current state of the issue (e.g. new, in_progress, closed)

    `title: list[str]`
    :   Title of the issue

    `type_: list[str]`
    :   Type classification of the issue

<a id="IssuesKeywordCondition"></a>

`IssuesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pylon.types.IssuesStringFilter`
    :   The type of the None singleton.

<a id="IssuesLikeCondition"></a>

`IssuesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pylon.types.IssuesStringFilter`
    :   The type of the None singleton.

<a id="IssuesListParams"></a>

`IssuesListParams(*args, **kwargs)`
:   Parameters for issues.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `end_time: str`
    :   The type of the None singleton.

    `start_time: str`
    :   The type of the None singleton.

<a id="IssuesLtCondition"></a>

`IssuesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pylon.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesLteCondition"></a>

`IssuesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pylon.types.IssuesSearchFilter`
    :   The type of the None singleton.

<a id="IssuesNeqCondition"></a>

`IssuesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pylon.types.IssuesSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.pylon.types.IssuesEqCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesGtCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesGteCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesLtCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesLteCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesInCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesNotCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesAndCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesOrCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.pylon.types.IssuesEqCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesGtCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesGteCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesLtCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesLteCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesInCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesNotCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesAndCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesOrCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesAnyCondition]`
    :   The type of the None singleton.

<a id="IssuesSearchFilter"></a>

`IssuesSearchFilter(*args, **kwargs)`
:   Available fields for filtering issues search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the issue was created, in ISO 8601 format

    `customer_portal_visible: bool | None`
    :   Whether the issue is visible in the customer portal

    `id: str`
    :   Unique identifier for the issue

    `latest_message_time: str | None`
    :   Timestamp of the most recent message on the issue, in ISO 8601 format

    `number: int | None`
    :   Human-readable issue number within the workspace

    `resolution_time: str | None`
    :   Timestamp when the issue was resolved, in ISO 8601 format

    `snoozed_until_time: str | None`
    :   Timestamp the issue is snoozed until, in ISO 8601 format

    `source: str | None`
    :   Channel the issue originated from (e.g. email, slack)

    `state: str | None`
    :   Current state of the issue (e.g. new, in_progress, closed)

    `title: str | None`
    :   Title of the issue

    `type_: str | None`
    :   Type classification of the issue

<a id="IssuesSearchQuery"></a>

`IssuesSearchQuery(*args, **kwargs)`
:   Search query for issues entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pylon.types.IssuesEqCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesNeqCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesGtCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesGteCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesLtCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesLteCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesInCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesLikeCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesContainsCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesNotCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesAndCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesOrCondition | airbyte_agent_sdk.connectors.pylon.types.IssuesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pylon.types.IssuesSortFilter]`
    :   The type of the None singleton.

<a id="IssuesSortFilter"></a>

`IssuesSortFilter(*args, **kwargs)`
:   Available fields for sorting issues search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   Timestamp when the issue was created, in ISO 8601 format

    `customer_portal_visible: Literal['asc', 'desc']`
    :   Whether the issue is visible in the customer portal

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the issue

    `latest_message_time: Literal['asc', 'desc']`
    :   Timestamp of the most recent message on the issue, in ISO 8601 format

    `number: Literal['asc', 'desc']`
    :   Human-readable issue number within the workspace

    `resolution_time: Literal['asc', 'desc']`
    :   Timestamp when the issue was resolved, in ISO 8601 format

    `snoozed_until_time: Literal['asc', 'desc']`
    :   Timestamp the issue is snoozed until, in ISO 8601 format

    `source: Literal['asc', 'desc']`
    :   Channel the issue originated from (e.g. email, slack)

    `state: Literal['asc', 'desc']`
    :   Current state of the issue (e.g. new, in_progress, closed)

    `title: Literal['asc', 'desc']`
    :   Title of the issue

    `type_: Literal['asc', 'desc']`
    :   Type classification of the issue

<a id="IssuesStringFilter"></a>

`IssuesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   Timestamp when the issue was created, in ISO 8601 format

    `customer_portal_visible: str`
    :   Whether the issue is visible in the customer portal

    `id: str`
    :   Unique identifier for the issue

    `latest_message_time: str`
    :   Timestamp of the most recent message on the issue, in ISO 8601 format

    `number: str`
    :   Human-readable issue number within the workspace

    `resolution_time: str`
    :   Timestamp when the issue was resolved, in ISO 8601 format

    `snoozed_until_time: str`
    :   Timestamp the issue is snoozed until, in ISO 8601 format

    `source: str`
    :   Channel the issue originated from (e.g. email, slack)

    `state: str`
    :   Current state of the issue (e.g. new, in_progress, closed)

    `title: str`
    :   Title of the issue

    `type_: str`
    :   Type classification of the issue

<a id="IssuesUpdateParams"></a>

`IssuesUpdateParams(*args, **kwargs)`
:   Parameters for issues.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `assignee_id: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `state: str`
    :   The type of the None singleton.

    `tags: list[str]`
    :   The type of the None singleton.

    `team_id: str`
    :   The type of the None singleton.

<a id="MeGetParams"></a>

`MeGetParams(*args, **kwargs)`
:   Parameters for me.get operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="MessagesAndCondition"></a>

`MessagesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.pylon.types.MessagesEqCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesNeqCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesGtCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesGteCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesLtCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesLteCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesInCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesLikeCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesContainsCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesNotCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesAndCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesOrCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesAnyCondition]`
    :   The type of the None singleton.

<a id="MessagesAnyCondition"></a>

`MessagesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.pylon.types.MessagesAnyValueFilter`
    :   The type of the None singleton.

<a id="MessagesAnyValueFilter"></a>

`MessagesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Unique identifier for the message

    `is_private: Any`
    :   Whether the message is an internal note (not visible to the customer)

    `source: Any`
    :   Channel the message was sent through (e.g. email, slack)

    `thread_id: Any`
    :   Identifier of the thread this message belongs to

    `timestamp: Any`
    :   Timestamp the message was posted, in ISO 8601 format

<a id="MessagesContainsCondition"></a>

`MessagesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pylon.types.MessagesAnyValueFilter`
    :   The type of the None singleton.

<a id="MessagesEqCondition"></a>

`MessagesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pylon.types.MessagesSearchFilter`
    :   The type of the None singleton.

<a id="MessagesFuzzyCondition"></a>

`MessagesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pylon.types.MessagesStringFilter`
    :   The type of the None singleton.

<a id="MessagesGtCondition"></a>

`MessagesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pylon.types.MessagesSearchFilter`
    :   The type of the None singleton.

<a id="MessagesGteCondition"></a>

`MessagesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pylon.types.MessagesSearchFilter`
    :   The type of the None singleton.

<a id="MessagesInCondition"></a>

`MessagesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.pylon.types.MessagesInFilter`
    :   The type of the None singleton.

<a id="MessagesInFilter"></a>

`MessagesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[str]`
    :   Unique identifier for the message

    `is_private: list[bool]`
    :   Whether the message is an internal note (not visible to the customer)

    `source: list[str]`
    :   Channel the message was sent through (e.g. email, slack)

    `thread_id: list[str]`
    :   Identifier of the thread this message belongs to

    `timestamp: list[str]`
    :   Timestamp the message was posted, in ISO 8601 format

<a id="MessagesKeywordCondition"></a>

`MessagesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pylon.types.MessagesStringFilter`
    :   The type of the None singleton.

<a id="MessagesLikeCondition"></a>

`MessagesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pylon.types.MessagesStringFilter`
    :   The type of the None singleton.

<a id="MessagesListParams"></a>

`MessagesListParams(*args, **kwargs)`
:   Parameters for messages.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

<a id="MessagesLtCondition"></a>

`MessagesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pylon.types.MessagesSearchFilter`
    :   The type of the None singleton.

<a id="MessagesLteCondition"></a>

`MessagesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pylon.types.MessagesSearchFilter`
    :   The type of the None singleton.

<a id="MessagesNeqCondition"></a>

`MessagesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pylon.types.MessagesSearchFilter`
    :   The type of the None singleton.

<a id="MessagesNotCondition"></a>

`MessagesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.pylon.types.MessagesEqCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesNeqCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesGtCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesGteCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesLtCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesLteCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesInCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesLikeCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesContainsCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesNotCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesAndCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesOrCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesAnyCondition`
    :   The type of the None singleton.

<a id="MessagesOrCondition"></a>

`MessagesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.pylon.types.MessagesEqCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesNeqCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesGtCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesGteCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesLtCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesLteCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesInCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesLikeCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesContainsCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesNotCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesAndCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesOrCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesAnyCondition]`
    :   The type of the None singleton.

<a id="MessagesSearchFilter"></a>

`MessagesSearchFilter(*args, **kwargs)`
:   Available fields for filtering messages search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the message

    `is_private: bool | None`
    :   Whether the message is an internal note (not visible to the customer)

    `source: str | None`
    :   Channel the message was sent through (e.g. email, slack)

    `thread_id: str | None`
    :   Identifier of the thread this message belongs to

    `timestamp: str | None`
    :   Timestamp the message was posted, in ISO 8601 format

<a id="MessagesSearchQuery"></a>

`MessagesSearchQuery(*args, **kwargs)`
:   Search query for messages entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pylon.types.MessagesEqCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesNeqCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesGtCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesGteCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesLtCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesLteCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesInCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesLikeCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesContainsCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesNotCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesAndCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesOrCondition | airbyte_agent_sdk.connectors.pylon.types.MessagesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pylon.types.MessagesSortFilter]`
    :   The type of the None singleton.

<a id="MessagesSortFilter"></a>

`MessagesSortFilter(*args, **kwargs)`
:   Available fields for sorting messages search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the message

    `is_private: Literal['asc', 'desc']`
    :   Whether the message is an internal note (not visible to the customer)

    `source: Literal['asc', 'desc']`
    :   Channel the message was sent through (e.g. email, slack)

    `thread_id: Literal['asc', 'desc']`
    :   Identifier of the thread this message belongs to

    `timestamp: Literal['asc', 'desc']`
    :   Timestamp the message was posted, in ISO 8601 format

<a id="MessagesStringFilter"></a>

`MessagesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the message

    `is_private: str`
    :   Whether the message is an internal note (not visible to the customer)

    `source: str`
    :   Channel the message was sent through (e.g. email, slack)

    `thread_id: str`
    :   Identifier of the thread this message belongs to

    `timestamp: str`
    :   Timestamp the message was posted, in ISO 8601 format

<a id="MilestonesCreateParams"></a>

`MilestonesCreateParams(*args, **kwargs)`
:   Parameters for milestones.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `due_date: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

<a id="MilestonesUpdateParams"></a>

`MilestonesUpdateParams(*args, **kwargs)`
:   Parameters for milestones.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `due_date: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="ProjectsCreateParams"></a>

`ProjectsCreateParams(*args, **kwargs)`
:   Parameters for projects.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `description_html: str`
    :   The type of the None singleton.

    `end_date: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `start_date: str`
    :   The type of the None singleton.

<a id="ProjectsUpdateParams"></a>

`ProjectsUpdateParams(*args, **kwargs)`
:   Parameters for projects.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `description_html: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `is_archived: bool`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.pylon.types.TagsEqCondition | airbyte_agent_sdk.connectors.pylon.types.TagsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.TagsGtCondition | airbyte_agent_sdk.connectors.pylon.types.TagsGteCondition | airbyte_agent_sdk.connectors.pylon.types.TagsLtCondition | airbyte_agent_sdk.connectors.pylon.types.TagsLteCondition | airbyte_agent_sdk.connectors.pylon.types.TagsInCondition | airbyte_agent_sdk.connectors.pylon.types.TagsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.TagsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.TagsNotCondition | airbyte_agent_sdk.connectors.pylon.types.TagsAndCondition | airbyte_agent_sdk.connectors.pylon.types.TagsOrCondition | airbyte_agent_sdk.connectors.pylon.types.TagsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.pylon.types.TagsAnyValueFilter`
    :   The type of the None singleton.

<a id="TagsAnyValueFilter"></a>

`TagsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Unique identifier for the tag

    `object_type: Any`
    :   Type of object this tag applies to (e.g. issue, account)

    `value: Any`
    :   Display value of the tag

<a id="TagsContainsCondition"></a>

`TagsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pylon.types.TagsAnyValueFilter`
    :   The type of the None singleton.

<a id="TagsCreateParams"></a>

`TagsCreateParams(*args, **kwargs)`
:   Parameters for tags.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hex_color: str`
    :   The type of the None singleton.

    `object_type: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

<a id="TagsEqCondition"></a>

`TagsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pylon.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsFuzzyCondition"></a>

`TagsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pylon.types.TagsStringFilter`
    :   The type of the None singleton.

<a id="TagsGetParams"></a>

`TagsGetParams(*args, **kwargs)`
:   Parameters for tags.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="TagsGtCondition"></a>

`TagsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pylon.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsGteCondition"></a>

`TagsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pylon.types.TagsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.pylon.types.TagsInFilter`
    :   The type of the None singleton.

<a id="TagsInFilter"></a>

`TagsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[str]`
    :   Unique identifier for the tag

    `object_type: list[str]`
    :   Type of object this tag applies to (e.g. issue, account)

    `value: list[str]`
    :   Display value of the tag

<a id="TagsKeywordCondition"></a>

`TagsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pylon.types.TagsStringFilter`
    :   The type of the None singleton.

<a id="TagsLikeCondition"></a>

`TagsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pylon.types.TagsStringFilter`
    :   The type of the None singleton.

<a id="TagsListParams"></a>

`TagsListParams(*args, **kwargs)`
:   Parameters for tags.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

<a id="TagsLtCondition"></a>

`TagsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pylon.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsLteCondition"></a>

`TagsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pylon.types.TagsSearchFilter`
    :   The type of the None singleton.

<a id="TagsNeqCondition"></a>

`TagsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pylon.types.TagsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.pylon.types.TagsEqCondition | airbyte_agent_sdk.connectors.pylon.types.TagsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.TagsGtCondition | airbyte_agent_sdk.connectors.pylon.types.TagsGteCondition | airbyte_agent_sdk.connectors.pylon.types.TagsLtCondition | airbyte_agent_sdk.connectors.pylon.types.TagsLteCondition | airbyte_agent_sdk.connectors.pylon.types.TagsInCondition | airbyte_agent_sdk.connectors.pylon.types.TagsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.TagsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.TagsNotCondition | airbyte_agent_sdk.connectors.pylon.types.TagsAndCondition | airbyte_agent_sdk.connectors.pylon.types.TagsOrCondition | airbyte_agent_sdk.connectors.pylon.types.TagsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.pylon.types.TagsEqCondition | airbyte_agent_sdk.connectors.pylon.types.TagsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.TagsGtCondition | airbyte_agent_sdk.connectors.pylon.types.TagsGteCondition | airbyte_agent_sdk.connectors.pylon.types.TagsLtCondition | airbyte_agent_sdk.connectors.pylon.types.TagsLteCondition | airbyte_agent_sdk.connectors.pylon.types.TagsInCondition | airbyte_agent_sdk.connectors.pylon.types.TagsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.TagsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.TagsNotCondition | airbyte_agent_sdk.connectors.pylon.types.TagsAndCondition | airbyte_agent_sdk.connectors.pylon.types.TagsOrCondition | airbyte_agent_sdk.connectors.pylon.types.TagsAnyCondition]`
    :   The type of the None singleton.

<a id="TagsSearchFilter"></a>

`TagsSearchFilter(*args, **kwargs)`
:   Available fields for filtering tags search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the tag

    `object_type: str | None`
    :   Type of object this tag applies to (e.g. issue, account)

    `value: str | None`
    :   Display value of the tag

<a id="TagsSearchQuery"></a>

`TagsSearchQuery(*args, **kwargs)`
:   Search query for tags entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pylon.types.TagsEqCondition | airbyte_agent_sdk.connectors.pylon.types.TagsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.TagsGtCondition | airbyte_agent_sdk.connectors.pylon.types.TagsGteCondition | airbyte_agent_sdk.connectors.pylon.types.TagsLtCondition | airbyte_agent_sdk.connectors.pylon.types.TagsLteCondition | airbyte_agent_sdk.connectors.pylon.types.TagsInCondition | airbyte_agent_sdk.connectors.pylon.types.TagsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.TagsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.TagsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.TagsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.TagsNotCondition | airbyte_agent_sdk.connectors.pylon.types.TagsAndCondition | airbyte_agent_sdk.connectors.pylon.types.TagsOrCondition | airbyte_agent_sdk.connectors.pylon.types.TagsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pylon.types.TagsSortFilter]`
    :   The type of the None singleton.

<a id="TagsSortFilter"></a>

`TagsSortFilter(*args, **kwargs)`
:   Available fields for sorting tags search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the tag

    `object_type: Literal['asc', 'desc']`
    :   Type of object this tag applies to (e.g. issue, account)

    `value: Literal['asc', 'desc']`
    :   Display value of the tag

<a id="TagsStringFilter"></a>

`TagsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the tag

    `object_type: str`
    :   Type of object this tag applies to (e.g. issue, account)

    `value: str`
    :   Display value of the tag

<a id="TagsUpdateParams"></a>

`TagsUpdateParams(*args, **kwargs)`
:   Parameters for tags.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `hex_color: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

<a id="TasksCreateParams"></a>

`TasksCreateParams(*args, **kwargs)`
:   Parameters for tasks.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee_id: str`
    :   The type of the None singleton.

    `body_html: str`
    :   The type of the None singleton.

    `due_date: str`
    :   The type of the None singleton.

    `milestone_id: str`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="TasksUpdateParams"></a>

`TasksUpdateParams(*args, **kwargs)`
:   Parameters for tasks.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `assignee_id: str`
    :   The type of the None singleton.

    `body_html: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `title: str`
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

    `and: list[airbyte_agent_sdk.connectors.pylon.types.TeamsEqCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsGtCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsGteCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsLtCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsLteCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsInCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsNotCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsAndCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsOrCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.pylon.types.TeamsAnyValueFilter`
    :   The type of the None singleton.

<a id="TeamsAnyValueFilter"></a>

`TeamsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Unique identifier for the team

    `name: Any`
    :   Name of the team

<a id="TeamsContainsCondition"></a>

`TeamsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pylon.types.TeamsAnyValueFilter`
    :   The type of the None singleton.

<a id="TeamsCreateParams"></a>

`TeamsCreateParams(*args, **kwargs)`
:   Parameters for teams.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="TeamsEqCondition"></a>

`TeamsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pylon.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsFuzzyCondition"></a>

`TeamsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pylon.types.TeamsStringFilter`
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

    `gt: airbyte_agent_sdk.connectors.pylon.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsGteCondition"></a>

`TeamsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pylon.types.TeamsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.pylon.types.TeamsInFilter`
    :   The type of the None singleton.

<a id="TeamsInFilter"></a>

`TeamsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[str]`
    :   Unique identifier for the team

    `name: list[str]`
    :   Name of the team

<a id="TeamsKeywordCondition"></a>

`TeamsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pylon.types.TeamsStringFilter`
    :   The type of the None singleton.

<a id="TeamsLikeCondition"></a>

`TeamsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pylon.types.TeamsStringFilter`
    :   The type of the None singleton.

<a id="TeamsListParams"></a>

`TeamsListParams(*args, **kwargs)`
:   Parameters for teams.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

<a id="TeamsLtCondition"></a>

`TeamsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pylon.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsLteCondition"></a>

`TeamsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pylon.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsNeqCondition"></a>

`TeamsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pylon.types.TeamsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.pylon.types.TeamsEqCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsGtCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsGteCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsLtCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsLteCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsInCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsNotCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsAndCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsOrCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.pylon.types.TeamsEqCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsGtCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsGteCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsLtCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsLteCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsInCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsNotCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsAndCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsOrCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsAnyCondition]`
    :   The type of the None singleton.

<a id="TeamsSearchFilter"></a>

`TeamsSearchFilter(*args, **kwargs)`
:   Available fields for filtering teams search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the team

    `name: str | None`
    :   Name of the team

<a id="TeamsSearchQuery"></a>

`TeamsSearchQuery(*args, **kwargs)`
:   Search query for teams entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pylon.types.TeamsEqCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsGtCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsGteCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsLtCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsLteCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsInCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsNotCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsAndCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsOrCondition | airbyte_agent_sdk.connectors.pylon.types.TeamsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pylon.types.TeamsSortFilter]`
    :   The type of the None singleton.

<a id="TeamsSortFilter"></a>

`TeamsSortFilter(*args, **kwargs)`
:   Available fields for sorting teams search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the team

    `name: Literal['asc', 'desc']`
    :   Name of the team

<a id="TeamsStringFilter"></a>

`TeamsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the team

    `name: str`
    :   Name of the team

<a id="TeamsUpdateParams"></a>

`TeamsUpdateParams(*args, **kwargs)`
:   Parameters for teams.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

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

    `and: list[airbyte_agent_sdk.connectors.pylon.types.TicketFormsEqCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsGtCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsGteCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsLtCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsLteCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsInCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsNotCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsAndCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsOrCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.pylon.types.TicketFormsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketFormsAnyValueFilter"></a>

`TicketFormsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Unique identifier for the ticket form

    `is_public: Any`
    :   Whether the ticket form is publicly accessible

    `name: Any`
    :   Display name of the ticket form

    `slug: Any`
    :   URL-safe identifier for the ticket form

<a id="TicketFormsContainsCondition"></a>

`TicketFormsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pylon.types.TicketFormsAnyValueFilter`
    :   The type of the None singleton.

<a id="TicketFormsEqCondition"></a>

`TicketFormsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pylon.types.TicketFormsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFormsFuzzyCondition"></a>

`TicketFormsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pylon.types.TicketFormsStringFilter`
    :   The type of the None singleton.

<a id="TicketFormsGtCondition"></a>

`TicketFormsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pylon.types.TicketFormsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFormsGteCondition"></a>

`TicketFormsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pylon.types.TicketFormsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.pylon.types.TicketFormsInFilter`
    :   The type of the None singleton.

<a id="TicketFormsInFilter"></a>

`TicketFormsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[str]`
    :   Unique identifier for the ticket form

    `is_public: list[bool]`
    :   Whether the ticket form is publicly accessible

    `name: list[str]`
    :   Display name of the ticket form

    `slug: list[str]`
    :   URL-safe identifier for the ticket form

<a id="TicketFormsKeywordCondition"></a>

`TicketFormsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pylon.types.TicketFormsStringFilter`
    :   The type of the None singleton.

<a id="TicketFormsLikeCondition"></a>

`TicketFormsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pylon.types.TicketFormsStringFilter`
    :   The type of the None singleton.

<a id="TicketFormsListParams"></a>

`TicketFormsListParams(*args, **kwargs)`
:   Parameters for ticket_forms.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

<a id="TicketFormsLtCondition"></a>

`TicketFormsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pylon.types.TicketFormsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFormsLteCondition"></a>

`TicketFormsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pylon.types.TicketFormsSearchFilter`
    :   The type of the None singleton.

<a id="TicketFormsNeqCondition"></a>

`TicketFormsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pylon.types.TicketFormsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.pylon.types.TicketFormsEqCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsGtCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsGteCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsLtCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsLteCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsInCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsNotCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsAndCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsOrCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.pylon.types.TicketFormsEqCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsGtCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsGteCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsLtCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsLteCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsInCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsNotCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsAndCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsOrCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsAnyCondition]`
    :   The type of the None singleton.

<a id="TicketFormsSearchFilter"></a>

`TicketFormsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ticket_forms search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the ticket form

    `is_public: bool | None`
    :   Whether the ticket form is publicly accessible

    `name: str | None`
    :   Display name of the ticket form

    `slug: str | None`
    :   URL-safe identifier for the ticket form

<a id="TicketFormsSearchQuery"></a>

`TicketFormsSearchQuery(*args, **kwargs)`
:   Search query for ticket_forms entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pylon.types.TicketFormsEqCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsNeqCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsGtCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsGteCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsLtCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsLteCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsInCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsLikeCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsContainsCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsNotCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsAndCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsOrCondition | airbyte_agent_sdk.connectors.pylon.types.TicketFormsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pylon.types.TicketFormsSortFilter]`
    :   The type of the None singleton.

<a id="TicketFormsSortFilter"></a>

`TicketFormsSortFilter(*args, **kwargs)`
:   Available fields for sorting ticket_forms search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the ticket form

    `is_public: Literal['asc', 'desc']`
    :   Whether the ticket form is publicly accessible

    `name: Literal['asc', 'desc']`
    :   Display name of the ticket form

    `slug: Literal['asc', 'desc']`
    :   URL-safe identifier for the ticket form

<a id="TicketFormsStringFilter"></a>

`TicketFormsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the ticket form

    `is_public: str`
    :   Whether the ticket form is publicly accessible

    `name: str`
    :   Display name of the ticket form

    `slug: str`
    :   URL-safe identifier for the ticket form

<a id="UserRolesAndCondition"></a>

`UserRolesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.pylon.types.UserRolesEqCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesNeqCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesGtCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesGteCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesLtCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesLteCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesInCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesLikeCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesContainsCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesNotCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesAndCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesOrCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesAnyCondition]`
    :   The type of the None singleton.

<a id="UserRolesAnyCondition"></a>

`UserRolesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.pylon.types.UserRolesAnyValueFilter`
    :   The type of the None singleton.

<a id="UserRolesAnyValueFilter"></a>

`UserRolesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Unique identifier for the user role

    `name: Any`
    :   Display name of the user role

    `slug: Any`
    :   URL-safe identifier for the user role

<a id="UserRolesContainsCondition"></a>

`UserRolesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pylon.types.UserRolesAnyValueFilter`
    :   The type of the None singleton.

<a id="UserRolesEqCondition"></a>

`UserRolesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pylon.types.UserRolesSearchFilter`
    :   The type of the None singleton.

<a id="UserRolesFuzzyCondition"></a>

`UserRolesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pylon.types.UserRolesStringFilter`
    :   The type of the None singleton.

<a id="UserRolesGtCondition"></a>

`UserRolesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.pylon.types.UserRolesSearchFilter`
    :   The type of the None singleton.

<a id="UserRolesGteCondition"></a>

`UserRolesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pylon.types.UserRolesSearchFilter`
    :   The type of the None singleton.

<a id="UserRolesInCondition"></a>

`UserRolesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.pylon.types.UserRolesInFilter`
    :   The type of the None singleton.

<a id="UserRolesInFilter"></a>

`UserRolesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[str]`
    :   Unique identifier for the user role

    `name: list[str]`
    :   Display name of the user role

    `slug: list[str]`
    :   URL-safe identifier for the user role

<a id="UserRolesKeywordCondition"></a>

`UserRolesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pylon.types.UserRolesStringFilter`
    :   The type of the None singleton.

<a id="UserRolesLikeCondition"></a>

`UserRolesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pylon.types.UserRolesStringFilter`
    :   The type of the None singleton.

<a id="UserRolesListParams"></a>

`UserRolesListParams(*args, **kwargs)`
:   Parameters for user_roles.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

<a id="UserRolesLtCondition"></a>

`UserRolesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pylon.types.UserRolesSearchFilter`
    :   The type of the None singleton.

<a id="UserRolesLteCondition"></a>

`UserRolesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pylon.types.UserRolesSearchFilter`
    :   The type of the None singleton.

<a id="UserRolesNeqCondition"></a>

`UserRolesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pylon.types.UserRolesSearchFilter`
    :   The type of the None singleton.

<a id="UserRolesNotCondition"></a>

`UserRolesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.pylon.types.UserRolesEqCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesNeqCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesGtCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesGteCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesLtCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesLteCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesInCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesLikeCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesContainsCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesNotCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesAndCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesOrCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesAnyCondition`
    :   The type of the None singleton.

<a id="UserRolesOrCondition"></a>

`UserRolesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.pylon.types.UserRolesEqCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesNeqCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesGtCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesGteCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesLtCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesLteCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesInCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesLikeCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesContainsCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesNotCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesAndCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesOrCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesAnyCondition]`
    :   The type of the None singleton.

<a id="UserRolesSearchFilter"></a>

`UserRolesSearchFilter(*args, **kwargs)`
:   Available fields for filtering user_roles search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the user role

    `name: str | None`
    :   Display name of the user role

    `slug: str | None`
    :   URL-safe identifier for the user role

<a id="UserRolesSearchQuery"></a>

`UserRolesSearchQuery(*args, **kwargs)`
:   Search query for user_roles entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pylon.types.UserRolesEqCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesNeqCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesGtCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesGteCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesLtCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesLteCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesInCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesLikeCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesContainsCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesNotCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesAndCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesOrCondition | airbyte_agent_sdk.connectors.pylon.types.UserRolesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pylon.types.UserRolesSortFilter]`
    :   The type of the None singleton.

<a id="UserRolesSortFilter"></a>

`UserRolesSortFilter(*args, **kwargs)`
:   Available fields for sorting user_roles search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the user role

    `name: Literal['asc', 'desc']`
    :   Display name of the user role

    `slug: Literal['asc', 'desc']`
    :   URL-safe identifier for the user role

<a id="UserRolesStringFilter"></a>

`UserRolesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the user role

    `name: str`
    :   Display name of the user role

    `slug: str`
    :   URL-safe identifier for the user role

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

    `and: list[airbyte_agent_sdk.connectors.pylon.types.UsersEqCondition | airbyte_agent_sdk.connectors.pylon.types.UsersNeqCondition | airbyte_agent_sdk.connectors.pylon.types.UsersGtCondition | airbyte_agent_sdk.connectors.pylon.types.UsersGteCondition | airbyte_agent_sdk.connectors.pylon.types.UsersLtCondition | airbyte_agent_sdk.connectors.pylon.types.UsersLteCondition | airbyte_agent_sdk.connectors.pylon.types.UsersInCondition | airbyte_agent_sdk.connectors.pylon.types.UsersLikeCondition | airbyte_agent_sdk.connectors.pylon.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.UsersContainsCondition | airbyte_agent_sdk.connectors.pylon.types.UsersNotCondition | airbyte_agent_sdk.connectors.pylon.types.UsersAndCondition | airbyte_agent_sdk.connectors.pylon.types.UsersOrCondition | airbyte_agent_sdk.connectors.pylon.types.UsersAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.pylon.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersAnyValueFilter"></a>

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email: Any`
    :   Primary email address of the user

    `id: Any`
    :   Unique identifier for the user

    `name: Any`
    :   Full name of the user

    `role_id: Any`
    :   Identifier of the user's role

    `status: Any`
    :   Current status of the user (e.g. active, disabled)

<a id="UsersContainsCondition"></a>

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.pylon.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersEqCondition"></a>

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.pylon.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersFuzzyCondition"></a>

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.pylon.types.UsersStringFilter`
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

    `gt: airbyte_agent_sdk.connectors.pylon.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersGteCondition"></a>

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.pylon.types.UsersSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.pylon.types.UsersInFilter`
    :   The type of the None singleton.

<a id="UsersInFilter"></a>

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email: list[str]`
    :   Primary email address of the user

    `id: list[str]`
    :   Unique identifier for the user

    `name: list[str]`
    :   Full name of the user

    `role_id: list[str]`
    :   Identifier of the user's role

    `status: list[str]`
    :   Current status of the user (e.g. active, disabled)

<a id="UsersKeywordCondition"></a>

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.pylon.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersLikeCondition"></a>

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.pylon.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersListParams"></a>

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

<a id="UsersLtCondition"></a>

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.pylon.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersLteCondition"></a>

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.pylon.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNeqCondition"></a>

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.pylon.types.UsersSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.pylon.types.UsersEqCondition | airbyte_agent_sdk.connectors.pylon.types.UsersNeqCondition | airbyte_agent_sdk.connectors.pylon.types.UsersGtCondition | airbyte_agent_sdk.connectors.pylon.types.UsersGteCondition | airbyte_agent_sdk.connectors.pylon.types.UsersLtCondition | airbyte_agent_sdk.connectors.pylon.types.UsersLteCondition | airbyte_agent_sdk.connectors.pylon.types.UsersInCondition | airbyte_agent_sdk.connectors.pylon.types.UsersLikeCondition | airbyte_agent_sdk.connectors.pylon.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.UsersContainsCondition | airbyte_agent_sdk.connectors.pylon.types.UsersNotCondition | airbyte_agent_sdk.connectors.pylon.types.UsersAndCondition | airbyte_agent_sdk.connectors.pylon.types.UsersOrCondition | airbyte_agent_sdk.connectors.pylon.types.UsersAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.pylon.types.UsersEqCondition | airbyte_agent_sdk.connectors.pylon.types.UsersNeqCondition | airbyte_agent_sdk.connectors.pylon.types.UsersGtCondition | airbyte_agent_sdk.connectors.pylon.types.UsersGteCondition | airbyte_agent_sdk.connectors.pylon.types.UsersLtCondition | airbyte_agent_sdk.connectors.pylon.types.UsersLteCondition | airbyte_agent_sdk.connectors.pylon.types.UsersInCondition | airbyte_agent_sdk.connectors.pylon.types.UsersLikeCondition | airbyte_agent_sdk.connectors.pylon.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.UsersContainsCondition | airbyte_agent_sdk.connectors.pylon.types.UsersNotCondition | airbyte_agent_sdk.connectors.pylon.types.UsersAndCondition | airbyte_agent_sdk.connectors.pylon.types.UsersOrCondition | airbyte_agent_sdk.connectors.pylon.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersSearchFilter"></a>

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email: str | None`
    :   Primary email address of the user

    `id: str`
    :   Unique identifier for the user

    `name: str | None`
    :   Full name of the user

    `role_id: str | None`
    :   Identifier of the user's role

    `status: str | None`
    :   Current status of the user (e.g. active, disabled)

<a id="UsersSearchQuery"></a>

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.pylon.types.UsersEqCondition | airbyte_agent_sdk.connectors.pylon.types.UsersNeqCondition | airbyte_agent_sdk.connectors.pylon.types.UsersGtCondition | airbyte_agent_sdk.connectors.pylon.types.UsersGteCondition | airbyte_agent_sdk.connectors.pylon.types.UsersLtCondition | airbyte_agent_sdk.connectors.pylon.types.UsersLteCondition | airbyte_agent_sdk.connectors.pylon.types.UsersInCondition | airbyte_agent_sdk.connectors.pylon.types.UsersLikeCondition | airbyte_agent_sdk.connectors.pylon.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.pylon.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.pylon.types.UsersContainsCondition | airbyte_agent_sdk.connectors.pylon.types.UsersNotCondition | airbyte_agent_sdk.connectors.pylon.types.UsersAndCondition | airbyte_agent_sdk.connectors.pylon.types.UsersOrCondition | airbyte_agent_sdk.connectors.pylon.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.pylon.types.UsersSortFilter]`
    :   The type of the None singleton.

<a id="UsersSortFilter"></a>

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email: Literal['asc', 'desc']`
    :   Primary email address of the user

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the user

    `name: Literal['asc', 'desc']`
    :   Full name of the user

    `role_id: Literal['asc', 'desc']`
    :   Identifier of the user's role

    `status: Literal['asc', 'desc']`
    :   Current status of the user (e.g. active, disabled)

<a id="UsersStringFilter"></a>

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `email: str`
    :   Primary email address of the user

    `id: str`
    :   Unique identifier for the user

    `name: str`
    :   Full name of the user

    `role_id: str`
    :   Identifier of the user's role

    `status: str`
    :   Current status of the user (e.g. active, disabled)