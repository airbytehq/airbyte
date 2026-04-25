---
id: airbyte_agent_sdk-connectors-intercom-types
title: airbyte_agent_sdk.connectors.intercom.types
---

Module airbyte_agent_sdk.connectors.intercom.types
==================================================
Type definitions for intercom connector.

Classes
-------

<a id="AdminsGetParams"></a>

`AdminsGetParams(*args, **kwargs)`
:   Parameters for admins.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="AdminsListParams"></a>

`AdminsListParams(*args, **kwargs)`
:   Parameters for admins.list operation

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="CompaniesAndCondition"></a>

`CompaniesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.intercom.types.CompaniesEqCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesNeqCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesGtCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesGteCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesLtCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesLteCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesInCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesLikeCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesFuzzyCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesKeywordCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesContainsCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesNotCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesAndCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesOrCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesAnyCondition]`
    :   The type of the None singleton.

<a id="CompaniesAnyCondition"></a>

`CompaniesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.intercom.types.CompaniesAnyValueFilter`
    :   The type of the None singleton.

<a id="CompaniesAnyValueFilter"></a>

`CompaniesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `app_id: Any`
    :   The ID of the application associated with the company

    `company_id: Any`
    :   The unique identifier of the company

    `created_at: Any`
    :   The date and time when the company was created

    `custom_attributes: Any`
    :   Custom attributes specific to the company

    `id: Any`
    :   The ID of the company

    `industry: Any`
    :   The industry in which the company operates

    `monthly_spend: Any`
    :   The monthly spend of the company

    `name: Any`
    :   The name of the company

    `plan: Any`
    :   Details of the company's subscription plan

    `remote_created_at: Any`
    :   The remote date and time when the company was created

    `segments: Any`
    :   Segments associated with the company

    `session_count: Any`
    :   The number of sessions related to the company

    `size: Any`
    :   The size of the company

    `tags: Any`
    :   Tags associated with the company

    `type_: Any`
    :   The type of the company

    `updated_at: Any`
    :   The date and time when the company was last updated

    `user_count: Any`
    :   The number of users associated with the company

    `website: Any`
    :   The website of the company

<a id="CompaniesContainsCondition"></a>

`CompaniesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.intercom.types.CompaniesAnyValueFilter`
    :   The type of the None singleton.

<a id="CompaniesCreateParams"></a>

`CompaniesCreateParams(*args, **kwargs)`
:   Parameters for companies.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `company_id: str`
    :   The type of the None singleton.

    `custom_attributes: dict[str, typing.Any]`
    :   The type of the None singleton.

    `industry: str`
    :   The type of the None singleton.

    `monthly_spend: float`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `plan: str`
    :   The type of the None singleton.

    `size: int`
    :   The type of the None singleton.

    `website: str`
    :   The type of the None singleton.

<a id="CompaniesEqCondition"></a>

`CompaniesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.intercom.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesFuzzyCondition"></a>

`CompaniesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.intercom.types.CompaniesStringFilter`
    :   The type of the None singleton.

<a id="CompaniesGetParams"></a>

`CompaniesGetParams(*args, **kwargs)`
:   Parameters for companies.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CompaniesGtCondition"></a>

`CompaniesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.intercom.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesGteCondition"></a>

`CompaniesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.intercom.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesInCondition"></a>

`CompaniesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.intercom.types.CompaniesInFilter`
    :   The type of the None singleton.

<a id="CompaniesInFilter"></a>

`CompaniesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `app_id: list[str]`
    :   The ID of the application associated with the company

    `company_id: list[str]`
    :   The unique identifier of the company

    `created_at: list[int]`
    :   The date and time when the company was created

    `custom_attributes: list[dict[str, typing.Any]]`
    :   Custom attributes specific to the company

    `id: list[str]`
    :   The ID of the company

    `industry: list[str]`
    :   The industry in which the company operates

    `monthly_spend: list[float]`
    :   The monthly spend of the company

    `name: list[str]`
    :   The name of the company

    `plan: list[dict[str, typing.Any]]`
    :   Details of the company's subscription plan

    `remote_created_at: list[int]`
    :   The remote date and time when the company was created

    `segments: list[dict[str, typing.Any]]`
    :   Segments associated with the company

    `session_count: list[int]`
    :   The number of sessions related to the company

    `size: list[int]`
    :   The size of the company

    `tags: list[dict[str, typing.Any]]`
    :   Tags associated with the company

    `type_: list[str]`
    :   The type of the company

    `updated_at: list[int]`
    :   The date and time when the company was last updated

    `user_count: list[int]`
    :   The number of users associated with the company

    `website: list[str]`
    :   The website of the company

<a id="CompaniesKeywordCondition"></a>

`CompaniesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.intercom.types.CompaniesStringFilter`
    :   The type of the None singleton.

<a id="CompaniesLikeCondition"></a>

`CompaniesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.intercom.types.CompaniesStringFilter`
    :   The type of the None singleton.

<a id="CompaniesListParams"></a>

`CompaniesListParams(*args, **kwargs)`
:   Parameters for companies.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

    `starting_after: str`
    :   The type of the None singleton.

<a id="CompaniesLtCondition"></a>

`CompaniesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.intercom.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesLteCondition"></a>

`CompaniesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.intercom.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesNeqCondition"></a>

`CompaniesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.intercom.types.CompaniesSearchFilter`
    :   The type of the None singleton.

<a id="CompaniesNotCondition"></a>

`CompaniesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.intercom.types.CompaniesEqCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesNeqCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesGtCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesGteCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesLtCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesLteCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesInCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesLikeCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesFuzzyCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesKeywordCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesContainsCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesNotCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesAndCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesOrCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesAnyCondition`
    :   The type of the None singleton.

<a id="CompaniesOrCondition"></a>

`CompaniesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.intercom.types.CompaniesEqCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesNeqCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesGtCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesGteCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesLtCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesLteCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesInCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesLikeCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesFuzzyCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesKeywordCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesContainsCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesNotCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesAndCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesOrCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesAnyCondition]`
    :   The type of the None singleton.

<a id="CompaniesSearchFilter"></a>

`CompaniesSearchFilter(*args, **kwargs)`
:   Available fields for filtering companies search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `app_id: str | None`
    :   The ID of the application associated with the company

    `company_id: str | None`
    :   The unique identifier of the company

    `created_at: int | None`
    :   The date and time when the company was created

    `custom_attributes: dict[str, typing.Any] | None`
    :   Custom attributes specific to the company

    `id: str | None`
    :   The ID of the company

    `industry: str | None`
    :   The industry in which the company operates

    `monthly_spend: float | None`
    :   The monthly spend of the company

    `name: str | None`
    :   The name of the company

    `plan: dict[str, typing.Any] | None`
    :   Details of the company's subscription plan

    `remote_created_at: int | None`
    :   The remote date and time when the company was created

    `segments: dict[str, typing.Any] | None`
    :   Segments associated with the company

    `session_count: int | None`
    :   The number of sessions related to the company

    `size: int | None`
    :   The size of the company

    `tags: dict[str, typing.Any] | None`
    :   Tags associated with the company

    `type_: str | None`
    :   The type of the company

    `updated_at: int | None`
    :   The date and time when the company was last updated

    `user_count: int | None`
    :   The number of users associated with the company

    `website: str | None`
    :   The website of the company

<a id="CompaniesSearchQuery"></a>

`CompaniesSearchQuery(*args, **kwargs)`
:   Search query for companies entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.intercom.types.CompaniesEqCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesNeqCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesGtCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesGteCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesLtCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesLteCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesInCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesLikeCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesFuzzyCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesKeywordCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesContainsCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesNotCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesAndCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesOrCondition | airbyte_agent_sdk.connectors.intercom.types.CompaniesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.intercom.types.CompaniesSortFilter]`
    :   The type of the None singleton.

<a id="CompaniesSortFilter"></a>

`CompaniesSortFilter(*args, **kwargs)`
:   Available fields for sorting companies search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `app_id: Literal['asc', 'desc']`
    :   The ID of the application associated with the company

    `company_id: Literal['asc', 'desc']`
    :   The unique identifier of the company

    `created_at: Literal['asc', 'desc']`
    :   The date and time when the company was created

    `custom_attributes: Literal['asc', 'desc']`
    :   Custom attributes specific to the company

    `id: Literal['asc', 'desc']`
    :   The ID of the company

    `industry: Literal['asc', 'desc']`
    :   The industry in which the company operates

    `monthly_spend: Literal['asc', 'desc']`
    :   The monthly spend of the company

    `name: Literal['asc', 'desc']`
    :   The name of the company

    `plan: Literal['asc', 'desc']`
    :   Details of the company's subscription plan

    `remote_created_at: Literal['asc', 'desc']`
    :   The remote date and time when the company was created

    `segments: Literal['asc', 'desc']`
    :   Segments associated with the company

    `session_count: Literal['asc', 'desc']`
    :   The number of sessions related to the company

    `size: Literal['asc', 'desc']`
    :   The size of the company

    `tags: Literal['asc', 'desc']`
    :   Tags associated with the company

    `type_: Literal['asc', 'desc']`
    :   The type of the company

    `updated_at: Literal['asc', 'desc']`
    :   The date and time when the company was last updated

    `user_count: Literal['asc', 'desc']`
    :   The number of users associated with the company

    `website: Literal['asc', 'desc']`
    :   The website of the company

<a id="CompaniesStringFilter"></a>

`CompaniesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `app_id: str`
    :   The ID of the application associated with the company

    `company_id: str`
    :   The unique identifier of the company

    `created_at: str`
    :   The date and time when the company was created

    `custom_attributes: str`
    :   Custom attributes specific to the company

    `id: str`
    :   The ID of the company

    `industry: str`
    :   The industry in which the company operates

    `monthly_spend: str`
    :   The monthly spend of the company

    `name: str`
    :   The name of the company

    `plan: str`
    :   Details of the company's subscription plan

    `remote_created_at: str`
    :   The remote date and time when the company was created

    `segments: str`
    :   Segments associated with the company

    `session_count: str`
    :   The number of sessions related to the company

    `size: str`
    :   The size of the company

    `tags: str`
    :   Tags associated with the company

    `type_: str`
    :   The type of the company

    `updated_at: str`
    :   The date and time when the company was last updated

    `user_count: str`
    :   The number of users associated with the company

    `website: str`
    :   The website of the company

<a id="CompaniesUpdateParams"></a>

`CompaniesUpdateParams(*args, **kwargs)`
:   Parameters for companies.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `custom_attributes: dict[str, typing.Any]`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `industry: str`
    :   The type of the None singleton.

    `monthly_spend: float`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `plan: str`
    :   The type of the None singleton.

    `size: int`
    :   The type of the None singleton.

    `website: str`
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

    `and: list[airbyte_agent_sdk.connectors.intercom.types.ContactsEqCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsGtCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsGteCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsLtCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsLteCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsInCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsNotCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsAndCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsOrCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.intercom.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

<a id="ContactsAnyValueFilter"></a>

`ContactsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `android_app_name: Any`
    :   The name of the Android app associated with the contact.

    `android_app_version: Any`
    :   The version of the Android app associated with the contact.

    `android_device: Any`
    :   The device used by the contact for Android.

    `android_last_seen_at: Any`
    :   The date and time when the contact was last seen on Android.

    `android_os_version: Any`
    :   The operating system version of the Android device.

    `android_sdk_version: Any`
    :   The SDK version of the Android device.

    `avatar: Any`
    :   URL pointing to the contact's avatar image.

    `browser: Any`
    :   The browser used by the contact.

    `browser_language: Any`
    :   The language preference set in the contact's browser.

    `browser_version: Any`
    :   The version of the browser used by the contact.

    `companies: Any`
    :   Companies associated with the contact.

    `created_at: Any`
    :   The date and time when the contact was created.

    `custom_attributes: Any`
    :   Custom attributes defined for the contact.

    `email: Any`
    :   The email address of the contact.

    `external_id: Any`
    :   External identifier for the contact.

    `has_hard_bounced: Any`
    :   Flag indicating if the contact has hard bounced.

    `id: Any`
    :   The unique identifier of the contact.

    `ios_app_name: Any`
    :   The name of the iOS app associated with the contact.

    `ios_app_version: Any`
    :   The version of the iOS app associated with the contact.

    `ios_device: Any`
    :   The device used by the contact for iOS.

    `ios_last_seen_at: Any`
    :   The date and time when the contact was last seen on iOS.

    `ios_os_version: Any`
    :   The operating system version of the iOS device.

    `ios_sdk_version: Any`
    :   The SDK version of the iOS device.

    `language_override: Any`
    :   Language override set for the contact.

    `last_contacted_at: Any`
    :   The date and time when the contact was last contacted.

    `last_email_clicked_at: Any`
    :   The date and time when the contact last clicked an email.

    `last_email_opened_at: Any`
    :   The date and time when the contact last opened an email.

    `last_replied_at: Any`
    :   The date and time when the contact last replied.

    `last_seen_at: Any`
    :   The date and time when the contact was last seen overall.

    `location: Any`
    :   Location details of the contact.

    `marked_email_as_spam: Any`
    :   Flag indicating if the contact's email was marked as spam.

    `name: Any`
    :   The name of the contact.

    `notes: Any`
    :   Notes associated with the contact.

    `opted_in_subscription_types: Any`
    :   Subscription types the contact opted into.

    `opted_out_subscription_types: Any`
    :   Subscription types the contact opted out from.

    `os: Any`
    :   Operating system of the contact's device.

    `owner_id: Any`
    :   The unique identifier of the contact's owner.

    `phone: Any`
    :   The phone number of the contact.

    `referrer: Any`
    :   Referrer information related to the contact.

    `role: Any`
    :   Role or position of the contact.

    `signed_up_at: Any`
    :   The date and time when the contact signed up.

    `sms_consent: Any`
    :   Consent status for SMS communication.

    `social_profiles: Any`
    :   Social profiles associated with the contact.

    `tags: Any`
    :   Tags associated with the contact.

    `type_: Any`
    :   Type of contact.

    `unsubscribed_from_emails: Any`
    :   Flag indicating if the contact unsubscribed from emails.

    `unsubscribed_from_sms: Any`
    :   Flag indicating if the contact unsubscribed from SMS.

    `updated_at: Any`
    :   The date and time when the contact was last updated.

    `utm_campaign: Any`
    :   Campaign data from UTM parameters.

    `utm_content: Any`
    :   Content data from UTM parameters.

    `utm_medium: Any`
    :   Medium data from UTM parameters.

    `utm_source: Any`
    :   Source data from UTM parameters.

    `utm_term: Any`
    :   Term data from UTM parameters.

    `workspace_id: Any`
    :   The unique identifier of the workspace associated with the contact.

<a id="ContactsContainsCondition"></a>

`ContactsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.intercom.types.ContactsAnyValueFilter`
    :   The type of the None singleton.

<a id="ContactsCreateParams"></a>

`ContactsCreateParams(*args, **kwargs)`
:   Parameters for contacts.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar: str`
    :   The type of the None singleton.

    `custom_attributes: dict[str, typing.Any]`
    :   The type of the None singleton.

    `email: str`
    :   The type of the None singleton.

    `external_id: str`
    :   The type of the None singleton.

    `last_seen_at: int`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `owner_id: int`
    :   The type of the None singleton.

    `phone: str`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

    `signed_up_at: int`
    :   The type of the None singleton.

    `unsubscribed_from_emails: bool`
    :   The type of the None singleton.

<a id="ContactsEqCondition"></a>

`ContactsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.intercom.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsFuzzyCondition"></a>

`ContactsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.intercom.types.ContactsStringFilter`
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

    `gt: airbyte_agent_sdk.connectors.intercom.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsGteCondition"></a>

`ContactsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.intercom.types.ContactsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.intercom.types.ContactsInFilter`
    :   The type of the None singleton.

<a id="ContactsInFilter"></a>

`ContactsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `android_app_name: list[str]`
    :   The name of the Android app associated with the contact.

    `android_app_version: list[str]`
    :   The version of the Android app associated with the contact.

    `android_device: list[str]`
    :   The device used by the contact for Android.

    `android_last_seen_at: list[str]`
    :   The date and time when the contact was last seen on Android.

    `android_os_version: list[str]`
    :   The operating system version of the Android device.

    `android_sdk_version: list[str]`
    :   The SDK version of the Android device.

    `avatar: list[str]`
    :   URL pointing to the contact's avatar image.

    `browser: list[str]`
    :   The browser used by the contact.

    `browser_language: list[str]`
    :   The language preference set in the contact's browser.

    `browser_version: list[str]`
    :   The version of the browser used by the contact.

    `companies: list[dict[str, typing.Any]]`
    :   Companies associated with the contact.

    `created_at: list[int]`
    :   The date and time when the contact was created.

    `custom_attributes: list[dict[str, typing.Any]]`
    :   Custom attributes defined for the contact.

    `email: list[str]`
    :   The email address of the contact.

    `external_id: list[str]`
    :   External identifier for the contact.

    `has_hard_bounced: list[bool]`
    :   Flag indicating if the contact has hard bounced.

    `id: list[str]`
    :   The unique identifier of the contact.

    `ios_app_name: list[str]`
    :   The name of the iOS app associated with the contact.

    `ios_app_version: list[str]`
    :   The version of the iOS app associated with the contact.

    `ios_device: list[str]`
    :   The device used by the contact for iOS.

    `ios_last_seen_at: list[int]`
    :   The date and time when the contact was last seen on iOS.

    `ios_os_version: list[str]`
    :   The operating system version of the iOS device.

    `ios_sdk_version: list[str]`
    :   The SDK version of the iOS device.

    `language_override: list[str]`
    :   Language override set for the contact.

    `last_contacted_at: list[int]`
    :   The date and time when the contact was last contacted.

    `last_email_clicked_at: list[int]`
    :   The date and time when the contact last clicked an email.

    `last_email_opened_at: list[int]`
    :   The date and time when the contact last opened an email.

    `last_replied_at: list[int]`
    :   The date and time when the contact last replied.

    `last_seen_at: list[int]`
    :   The date and time when the contact was last seen overall.

    `location: list[dict[str, typing.Any]]`
    :   Location details of the contact.

    `marked_email_as_spam: list[bool]`
    :   Flag indicating if the contact's email was marked as spam.

    `name: list[str]`
    :   The name of the contact.

    `notes: list[dict[str, typing.Any]]`
    :   Notes associated with the contact.

    `opted_in_subscription_types: list[dict[str, typing.Any]]`
    :   Subscription types the contact opted into.

    `opted_out_subscription_types: list[dict[str, typing.Any]]`
    :   Subscription types the contact opted out from.

    `os: list[str]`
    :   Operating system of the contact's device.

    `owner_id: list[int]`
    :   The unique identifier of the contact's owner.

    `phone: list[str]`
    :   The phone number of the contact.

    `referrer: list[str]`
    :   Referrer information related to the contact.

    `role: list[str]`
    :   Role or position of the contact.

    `signed_up_at: list[int]`
    :   The date and time when the contact signed up.

    `sms_consent: list[bool]`
    :   Consent status for SMS communication.

    `social_profiles: list[dict[str, typing.Any]]`
    :   Social profiles associated with the contact.

    `tags: list[dict[str, typing.Any]]`
    :   Tags associated with the contact.

    `type_: list[str]`
    :   Type of contact.

    `unsubscribed_from_emails: list[bool]`
    :   Flag indicating if the contact unsubscribed from emails.

    `unsubscribed_from_sms: list[bool]`
    :   Flag indicating if the contact unsubscribed from SMS.

    `updated_at: list[int]`
    :   The date and time when the contact was last updated.

    `utm_campaign: list[str]`
    :   Campaign data from UTM parameters.

    `utm_content: list[str]`
    :   Content data from UTM parameters.

    `utm_medium: list[str]`
    :   Medium data from UTM parameters.

    `utm_source: list[str]`
    :   Source data from UTM parameters.

    `utm_term: list[str]`
    :   Term data from UTM parameters.

    `workspace_id: list[str]`
    :   The unique identifier of the workspace associated with the contact.

<a id="ContactsKeywordCondition"></a>

`ContactsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.intercom.types.ContactsStringFilter`
    :   The type of the None singleton.

<a id="ContactsLikeCondition"></a>

`ContactsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.intercom.types.ContactsStringFilter`
    :   The type of the None singleton.

<a id="ContactsListParams"></a>

`ContactsListParams(*args, **kwargs)`
:   Parameters for contacts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

    `starting_after: str`
    :   The type of the None singleton.

<a id="ContactsLtCondition"></a>

`ContactsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.intercom.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsLteCondition"></a>

`ContactsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.intercom.types.ContactsSearchFilter`
    :   The type of the None singleton.

<a id="ContactsNeqCondition"></a>

`ContactsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.intercom.types.ContactsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.intercom.types.ContactsEqCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsGtCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsGteCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsLtCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsLteCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsInCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsNotCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsAndCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsOrCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.intercom.types.ContactsEqCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsGtCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsGteCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsLtCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsLteCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsInCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsNotCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsAndCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsOrCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsAnyCondition]`
    :   The type of the None singleton.

<a id="ContactsSearchFilter"></a>

`ContactsSearchFilter(*args, **kwargs)`
:   Available fields for filtering contacts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `android_app_name: str | None`
    :   The name of the Android app associated with the contact.

    `android_app_version: str | None`
    :   The version of the Android app associated with the contact.

    `android_device: str | None`
    :   The device used by the contact for Android.

    `android_last_seen_at: str | None`
    :   The date and time when the contact was last seen on Android.

    `android_os_version: str | None`
    :   The operating system version of the Android device.

    `android_sdk_version: str | None`
    :   The SDK version of the Android device.

    `avatar: str | None`
    :   URL pointing to the contact's avatar image.

    `browser: str | None`
    :   The browser used by the contact.

    `browser_language: str | None`
    :   The language preference set in the contact's browser.

    `browser_version: str | None`
    :   The version of the browser used by the contact.

    `companies: dict[str, typing.Any] | None`
    :   Companies associated with the contact.

    `created_at: int | None`
    :   The date and time when the contact was created.

    `custom_attributes: dict[str, typing.Any] | None`
    :   Custom attributes defined for the contact.

    `email: str | None`
    :   The email address of the contact.

    `external_id: str | None`
    :   External identifier for the contact.

    `has_hard_bounced: bool | None`
    :   Flag indicating if the contact has hard bounced.

    `id: str | None`
    :   The unique identifier of the contact.

    `ios_app_name: str | None`
    :   The name of the iOS app associated with the contact.

    `ios_app_version: str | None`
    :   The version of the iOS app associated with the contact.

    `ios_device: str | None`
    :   The device used by the contact for iOS.

    `ios_last_seen_at: int | None`
    :   The date and time when the contact was last seen on iOS.

    `ios_os_version: str | None`
    :   The operating system version of the iOS device.

    `ios_sdk_version: str | None`
    :   The SDK version of the iOS device.

    `language_override: str | None`
    :   Language override set for the contact.

    `last_contacted_at: int | None`
    :   The date and time when the contact was last contacted.

    `last_email_clicked_at: int | None`
    :   The date and time when the contact last clicked an email.

    `last_email_opened_at: int | None`
    :   The date and time when the contact last opened an email.

    `last_replied_at: int | None`
    :   The date and time when the contact last replied.

    `last_seen_at: int | None`
    :   The date and time when the contact was last seen overall.

    `location: dict[str, typing.Any] | None`
    :   Location details of the contact.

    `marked_email_as_spam: bool | None`
    :   Flag indicating if the contact's email was marked as spam.

    `name: str | None`
    :   The name of the contact.

    `notes: dict[str, typing.Any] | None`
    :   Notes associated with the contact.

    `opted_in_subscription_types: dict[str, typing.Any] | None`
    :   Subscription types the contact opted into.

    `opted_out_subscription_types: dict[str, typing.Any] | None`
    :   Subscription types the contact opted out from.

    `os: str | None`
    :   Operating system of the contact's device.

    `owner_id: int | None`
    :   The unique identifier of the contact's owner.

    `phone: str | None`
    :   The phone number of the contact.

    `referrer: str | None`
    :   Referrer information related to the contact.

    `role: str | None`
    :   Role or position of the contact.

    `signed_up_at: int | None`
    :   The date and time when the contact signed up.

    `sms_consent: bool | None`
    :   Consent status for SMS communication.

    `social_profiles: dict[str, typing.Any] | None`
    :   Social profiles associated with the contact.

    `tags: dict[str, typing.Any] | None`
    :   Tags associated with the contact.

    `type_: str | None`
    :   Type of contact.

    `unsubscribed_from_emails: bool | None`
    :   Flag indicating if the contact unsubscribed from emails.

    `unsubscribed_from_sms: bool | None`
    :   Flag indicating if the contact unsubscribed from SMS.

    `updated_at: int | None`
    :   The date and time when the contact was last updated.

    `utm_campaign: str | None`
    :   Campaign data from UTM parameters.

    `utm_content: str | None`
    :   Content data from UTM parameters.

    `utm_medium: str | None`
    :   Medium data from UTM parameters.

    `utm_source: str | None`
    :   Source data from UTM parameters.

    `utm_term: str | None`
    :   Term data from UTM parameters.

    `workspace_id: str | None`
    :   The unique identifier of the workspace associated with the contact.

<a id="ContactsSearchQuery"></a>

`ContactsSearchQuery(*args, **kwargs)`
:   Search query for contacts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.intercom.types.ContactsEqCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsNeqCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsGtCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsGteCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsLtCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsLteCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsInCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsLikeCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsFuzzyCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsKeywordCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsContainsCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsNotCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsAndCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsOrCondition | airbyte_agent_sdk.connectors.intercom.types.ContactsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.intercom.types.ContactsSortFilter]`
    :   The type of the None singleton.

<a id="ContactsSortFilter"></a>

`ContactsSortFilter(*args, **kwargs)`
:   Available fields for sorting contacts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `android_app_name: Literal['asc', 'desc']`
    :   The name of the Android app associated with the contact.

    `android_app_version: Literal['asc', 'desc']`
    :   The version of the Android app associated with the contact.

    `android_device: Literal['asc', 'desc']`
    :   The device used by the contact for Android.

    `android_last_seen_at: Literal['asc', 'desc']`
    :   The date and time when the contact was last seen on Android.

    `android_os_version: Literal['asc', 'desc']`
    :   The operating system version of the Android device.

    `android_sdk_version: Literal['asc', 'desc']`
    :   The SDK version of the Android device.

    `avatar: Literal['asc', 'desc']`
    :   URL pointing to the contact's avatar image.

    `browser: Literal['asc', 'desc']`
    :   The browser used by the contact.

    `browser_language: Literal['asc', 'desc']`
    :   The language preference set in the contact's browser.

    `browser_version: Literal['asc', 'desc']`
    :   The version of the browser used by the contact.

    `companies: Literal['asc', 'desc']`
    :   Companies associated with the contact.

    `created_at: Literal['asc', 'desc']`
    :   The date and time when the contact was created.

    `custom_attributes: Literal['asc', 'desc']`
    :   Custom attributes defined for the contact.

    `email: Literal['asc', 'desc']`
    :   The email address of the contact.

    `external_id: Literal['asc', 'desc']`
    :   External identifier for the contact.

    `has_hard_bounced: Literal['asc', 'desc']`
    :   Flag indicating if the contact has hard bounced.

    `id: Literal['asc', 'desc']`
    :   The unique identifier of the contact.

    `ios_app_name: Literal['asc', 'desc']`
    :   The name of the iOS app associated with the contact.

    `ios_app_version: Literal['asc', 'desc']`
    :   The version of the iOS app associated with the contact.

    `ios_device: Literal['asc', 'desc']`
    :   The device used by the contact for iOS.

    `ios_last_seen_at: Literal['asc', 'desc']`
    :   The date and time when the contact was last seen on iOS.

    `ios_os_version: Literal['asc', 'desc']`
    :   The operating system version of the iOS device.

    `ios_sdk_version: Literal['asc', 'desc']`
    :   The SDK version of the iOS device.

    `language_override: Literal['asc', 'desc']`
    :   Language override set for the contact.

    `last_contacted_at: Literal['asc', 'desc']`
    :   The date and time when the contact was last contacted.

    `last_email_clicked_at: Literal['asc', 'desc']`
    :   The date and time when the contact last clicked an email.

    `last_email_opened_at: Literal['asc', 'desc']`
    :   The date and time when the contact last opened an email.

    `last_replied_at: Literal['asc', 'desc']`
    :   The date and time when the contact last replied.

    `last_seen_at: Literal['asc', 'desc']`
    :   The date and time when the contact was last seen overall.

    `location: Literal['asc', 'desc']`
    :   Location details of the contact.

    `marked_email_as_spam: Literal['asc', 'desc']`
    :   Flag indicating if the contact's email was marked as spam.

    `name: Literal['asc', 'desc']`
    :   The name of the contact.

    `notes: Literal['asc', 'desc']`
    :   Notes associated with the contact.

    `opted_in_subscription_types: Literal['asc', 'desc']`
    :   Subscription types the contact opted into.

    `opted_out_subscription_types: Literal['asc', 'desc']`
    :   Subscription types the contact opted out from.

    `os: Literal['asc', 'desc']`
    :   Operating system of the contact's device.

    `owner_id: Literal['asc', 'desc']`
    :   The unique identifier of the contact's owner.

    `phone: Literal['asc', 'desc']`
    :   The phone number of the contact.

    `referrer: Literal['asc', 'desc']`
    :   Referrer information related to the contact.

    `role: Literal['asc', 'desc']`
    :   Role or position of the contact.

    `signed_up_at: Literal['asc', 'desc']`
    :   The date and time when the contact signed up.

    `sms_consent: Literal['asc', 'desc']`
    :   Consent status for SMS communication.

    `social_profiles: Literal['asc', 'desc']`
    :   Social profiles associated with the contact.

    `tags: Literal['asc', 'desc']`
    :   Tags associated with the contact.

    `type_: Literal['asc', 'desc']`
    :   Type of contact.

    `unsubscribed_from_emails: Literal['asc', 'desc']`
    :   Flag indicating if the contact unsubscribed from emails.

    `unsubscribed_from_sms: Literal['asc', 'desc']`
    :   Flag indicating if the contact unsubscribed from SMS.

    `updated_at: Literal['asc', 'desc']`
    :   The date and time when the contact was last updated.

    `utm_campaign: Literal['asc', 'desc']`
    :   Campaign data from UTM parameters.

    `utm_content: Literal['asc', 'desc']`
    :   Content data from UTM parameters.

    `utm_medium: Literal['asc', 'desc']`
    :   Medium data from UTM parameters.

    `utm_source: Literal['asc', 'desc']`
    :   Source data from UTM parameters.

    `utm_term: Literal['asc', 'desc']`
    :   Term data from UTM parameters.

    `workspace_id: Literal['asc', 'desc']`
    :   The unique identifier of the workspace associated with the contact.

<a id="ContactsStringFilter"></a>

`ContactsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `android_app_name: str`
    :   The name of the Android app associated with the contact.

    `android_app_version: str`
    :   The version of the Android app associated with the contact.

    `android_device: str`
    :   The device used by the contact for Android.

    `android_last_seen_at: str`
    :   The date and time when the contact was last seen on Android.

    `android_os_version: str`
    :   The operating system version of the Android device.

    `android_sdk_version: str`
    :   The SDK version of the Android device.

    `avatar: str`
    :   URL pointing to the contact's avatar image.

    `browser: str`
    :   The browser used by the contact.

    `browser_language: str`
    :   The language preference set in the contact's browser.

    `browser_version: str`
    :   The version of the browser used by the contact.

    `companies: str`
    :   Companies associated with the contact.

    `created_at: str`
    :   The date and time when the contact was created.

    `custom_attributes: str`
    :   Custom attributes defined for the contact.

    `email: str`
    :   The email address of the contact.

    `external_id: str`
    :   External identifier for the contact.

    `has_hard_bounced: str`
    :   Flag indicating if the contact has hard bounced.

    `id: str`
    :   The unique identifier of the contact.

    `ios_app_name: str`
    :   The name of the iOS app associated with the contact.

    `ios_app_version: str`
    :   The version of the iOS app associated with the contact.

    `ios_device: str`
    :   The device used by the contact for iOS.

    `ios_last_seen_at: str`
    :   The date and time when the contact was last seen on iOS.

    `ios_os_version: str`
    :   The operating system version of the iOS device.

    `ios_sdk_version: str`
    :   The SDK version of the iOS device.

    `language_override: str`
    :   Language override set for the contact.

    `last_contacted_at: str`
    :   The date and time when the contact was last contacted.

    `last_email_clicked_at: str`
    :   The date and time when the contact last clicked an email.

    `last_email_opened_at: str`
    :   The date and time when the contact last opened an email.

    `last_replied_at: str`
    :   The date and time when the contact last replied.

    `last_seen_at: str`
    :   The date and time when the contact was last seen overall.

    `location: str`
    :   Location details of the contact.

    `marked_email_as_spam: str`
    :   Flag indicating if the contact's email was marked as spam.

    `name: str`
    :   The name of the contact.

    `notes: str`
    :   Notes associated with the contact.

    `opted_in_subscription_types: str`
    :   Subscription types the contact opted into.

    `opted_out_subscription_types: str`
    :   Subscription types the contact opted out from.

    `os: str`
    :   Operating system of the contact's device.

    `owner_id: str`
    :   The unique identifier of the contact's owner.

    `phone: str`
    :   The phone number of the contact.

    `referrer: str`
    :   Referrer information related to the contact.

    `role: str`
    :   Role or position of the contact.

    `signed_up_at: str`
    :   The date and time when the contact signed up.

    `sms_consent: str`
    :   Consent status for SMS communication.

    `social_profiles: str`
    :   Social profiles associated with the contact.

    `tags: str`
    :   Tags associated with the contact.

    `type_: str`
    :   Type of contact.

    `unsubscribed_from_emails: str`
    :   Flag indicating if the contact unsubscribed from emails.

    `unsubscribed_from_sms: str`
    :   Flag indicating if the contact unsubscribed from SMS.

    `updated_at: str`
    :   The date and time when the contact was last updated.

    `utm_campaign: str`
    :   Campaign data from UTM parameters.

    `utm_content: str`
    :   Content data from UTM parameters.

    `utm_medium: str`
    :   Medium data from UTM parameters.

    `utm_source: str`
    :   Source data from UTM parameters.

    `utm_term: str`
    :   Term data from UTM parameters.

    `workspace_id: str`
    :   The unique identifier of the workspace associated with the contact.

<a id="ContactsUpdateParams"></a>

`ContactsUpdateParams(*args, **kwargs)`
:   Parameters for contacts.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `avatar: str`
    :   The type of the None singleton.

    `custom_attributes: dict[str, typing.Any]`
    :   The type of the None singleton.

    `email: str`
    :   The type of the None singleton.

    `external_id: str`
    :   The type of the None singleton.

    `id: str`
    :   The type of the None singleton.

    `last_seen_at: int`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `owner_id: int`
    :   The type of the None singleton.

    `phone: str`
    :   The type of the None singleton.

    `role: str`
    :   The type of the None singleton.

    `signed_up_at: int`
    :   The type of the None singleton.

    `unsubscribed_from_emails: bool`
    :   The type of the None singleton.

<a id="ConversationsAndCondition"></a>

`ConversationsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.intercom.types.ConversationsEqCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsNeqCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsGtCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsGteCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsLtCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsLteCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsInCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsLikeCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsFuzzyCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsKeywordCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsContainsCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsNotCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsAndCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsOrCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsAnyCondition]`
    :   The type of the None singleton.

<a id="ConversationsAnyCondition"></a>

`ConversationsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.intercom.types.ConversationsAnyValueFilter`
    :   The type of the None singleton.

<a id="ConversationsAnyValueFilter"></a>

`ConversationsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `admin_assignee_id: Any`
    :   The ID of the administrator assigned to the conversation

    `ai_agent: Any`
    :   Data related to AI Agent involvement in the conversation

    `ai_agent_participated: Any`
    :   Indicates whether AI Agent participated in the conversation

    `assignee: Any`
    :   The assigned user responsible for the conversation.

    `contacts: Any`
    :   List of contacts involved in the conversation.

    `conversation_message: Any`
    :   The main message content of the conversation.

    `conversation_rating: Any`
    :   Ratings given to the conversation by the customer and teammate.

    `created_at: Any`
    :   The timestamp when the conversation was created

    `custom_attributes: Any`
    :   Custom attributes associated with the conversation

    `customer_first_reply: Any`
    :   Timestamp indicating when the customer first replied.

    `customers: Any`
    :   List of customers involved in the conversation

    `first_contact_reply: Any`
    :   Timestamp indicating when the first contact replied.

    `id: Any`
    :   The unique ID of the conversation

    `linked_objects: Any`
    :   Linked objects associated with the conversation

    `open: Any`
    :   Indicates if the conversation is open or closed

    `priority: Any`
    :   The priority level of the conversation

    `read: Any`
    :   Indicates if the conversation has been read

    `redacted: Any`
    :   Indicates if the conversation is redacted

    `sent_at: Any`
    :   The timestamp when the conversation was sent

    `sla_applied: Any`
    :   Service Level Agreement details applied to the conversation.

    `snoozed_until: Any`
    :   Timestamp until the conversation is snoozed

    `source: Any`
    :   Source details of the conversation.

    `state: Any`
    :   The state of the conversation (e.g., new, in progress)

    `statistics: Any`
    :   Statistics related to the conversation.

    `tags: Any`
    :   Tags applied to the conversation.

    `team_assignee_id: Any`
    :   The ID of the team assigned to the conversation

    `teammates: Any`
    :   List of teammates involved in the conversation.

    `title: Any`
    :   The title of the conversation

    `topics: Any`
    :   Topics associated with the conversation.

    `type_: Any`
    :   The type of the conversation

    `updated_at: Any`
    :   The timestamp when the conversation was last updated

    `user: Any`
    :   The user related to the conversation.

    `waiting_since: Any`
    :   Timestamp since waiting for a response

<a id="ConversationsContainsCondition"></a>

`ConversationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.intercom.types.ConversationsAnyValueFilter`
    :   The type of the None singleton.

<a id="ConversationsEqCondition"></a>

`ConversationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.intercom.types.ConversationsSearchFilter`
    :   The type of the None singleton.

<a id="ConversationsFuzzyCondition"></a>

`ConversationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.intercom.types.ConversationsStringFilter`
    :   The type of the None singleton.

<a id="ConversationsGetParams"></a>

`ConversationsGetParams(*args, **kwargs)`
:   Parameters for conversations.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ConversationsGtCondition"></a>

`ConversationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.intercom.types.ConversationsSearchFilter`
    :   The type of the None singleton.

<a id="ConversationsGteCondition"></a>

`ConversationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.intercom.types.ConversationsSearchFilter`
    :   The type of the None singleton.

<a id="ConversationsInCondition"></a>

`ConversationsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.intercom.types.ConversationsInFilter`
    :   The type of the None singleton.

<a id="ConversationsInFilter"></a>

`ConversationsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `admin_assignee_id: list[int]`
    :   The ID of the administrator assigned to the conversation

    `ai_agent: list[dict[str, typing.Any]]`
    :   Data related to AI Agent involvement in the conversation

    `ai_agent_participated: list[bool]`
    :   Indicates whether AI Agent participated in the conversation

    `assignee: list[dict[str, typing.Any]]`
    :   The assigned user responsible for the conversation.

    `contacts: list[dict[str, typing.Any]]`
    :   List of contacts involved in the conversation.

    `conversation_message: list[dict[str, typing.Any]]`
    :   The main message content of the conversation.

    `conversation_rating: list[dict[str, typing.Any]]`
    :   Ratings given to the conversation by the customer and teammate.

    `created_at: list[int]`
    :   The timestamp when the conversation was created

    `custom_attributes: list[dict[str, typing.Any]]`
    :   Custom attributes associated with the conversation

    `customer_first_reply: list[dict[str, typing.Any]]`
    :   Timestamp indicating when the customer first replied.

    `customers: list[list[typing.Any]]`
    :   List of customers involved in the conversation

    `first_contact_reply: list[dict[str, typing.Any]]`
    :   Timestamp indicating when the first contact replied.

    `id: list[str]`
    :   The unique ID of the conversation

    `linked_objects: list[dict[str, typing.Any]]`
    :   Linked objects associated with the conversation

    `open: list[bool]`
    :   Indicates if the conversation is open or closed

    `priority: list[str]`
    :   The priority level of the conversation

    `read: list[bool]`
    :   Indicates if the conversation has been read

    `redacted: list[bool]`
    :   Indicates if the conversation is redacted

    `sent_at: list[int]`
    :   The timestamp when the conversation was sent

    `sla_applied: list[dict[str, typing.Any]]`
    :   Service Level Agreement details applied to the conversation.

    `snoozed_until: list[int]`
    :   Timestamp until the conversation is snoozed

    `source: list[dict[str, typing.Any]]`
    :   Source details of the conversation.

    `state: list[str]`
    :   The state of the conversation (e.g., new, in progress)

    `statistics: list[dict[str, typing.Any]]`
    :   Statistics related to the conversation.

    `tags: list[dict[str, typing.Any]]`
    :   Tags applied to the conversation.

    `team_assignee_id: list[int]`
    :   The ID of the team assigned to the conversation

    `teammates: list[dict[str, typing.Any]]`
    :   List of teammates involved in the conversation.

    `title: list[str]`
    :   The title of the conversation

    `topics: list[dict[str, typing.Any]]`
    :   Topics associated with the conversation.

    `type_: list[str]`
    :   The type of the conversation

    `updated_at: list[int]`
    :   The timestamp when the conversation was last updated

    `user: list[dict[str, typing.Any]]`
    :   The user related to the conversation.

    `waiting_since: list[int]`
    :   Timestamp since waiting for a response

<a id="ConversationsKeywordCondition"></a>

`ConversationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.intercom.types.ConversationsStringFilter`
    :   The type of the None singleton.

<a id="ConversationsLikeCondition"></a>

`ConversationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.intercom.types.ConversationsStringFilter`
    :   The type of the None singleton.

<a id="ConversationsListParams"></a>

`ConversationsListParams(*args, **kwargs)`
:   Parameters for conversations.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `per_page: int`
    :   The type of the None singleton.

    `starting_after: str`
    :   The type of the None singleton.

<a id="ConversationsLtCondition"></a>

`ConversationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.intercom.types.ConversationsSearchFilter`
    :   The type of the None singleton.

<a id="ConversationsLteCondition"></a>

`ConversationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.intercom.types.ConversationsSearchFilter`
    :   The type of the None singleton.

<a id="ConversationsNeqCondition"></a>

`ConversationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.intercom.types.ConversationsSearchFilter`
    :   The type of the None singleton.

<a id="ConversationsNotCondition"></a>

`ConversationsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.intercom.types.ConversationsEqCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsNeqCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsGtCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsGteCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsLtCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsLteCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsInCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsLikeCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsFuzzyCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsKeywordCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsContainsCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsNotCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsAndCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsOrCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsAnyCondition`
    :   The type of the None singleton.

<a id="ConversationsOrCondition"></a>

`ConversationsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.intercom.types.ConversationsEqCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsNeqCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsGtCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsGteCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsLtCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsLteCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsInCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsLikeCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsFuzzyCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsKeywordCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsContainsCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsNotCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsAndCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsOrCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsAnyCondition]`
    :   The type of the None singleton.

<a id="ConversationsSearchFilter"></a>

`ConversationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering conversations search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `admin_assignee_id: int | None`
    :   The ID of the administrator assigned to the conversation

    `ai_agent: dict[str, typing.Any] | None`
    :   Data related to AI Agent involvement in the conversation

    `ai_agent_participated: bool | None`
    :   Indicates whether AI Agent participated in the conversation

    `assignee: dict[str, typing.Any] | None`
    :   The assigned user responsible for the conversation.

    `contacts: dict[str, typing.Any] | None`
    :   List of contacts involved in the conversation.

    `conversation_message: dict[str, typing.Any] | None`
    :   The main message content of the conversation.

    `conversation_rating: dict[str, typing.Any] | None`
    :   Ratings given to the conversation by the customer and teammate.

    `created_at: int | None`
    :   The timestamp when the conversation was created

    `custom_attributes: dict[str, typing.Any] | None`
    :   Custom attributes associated with the conversation

    `customer_first_reply: dict[str, typing.Any] | None`
    :   Timestamp indicating when the customer first replied.

    `customers: list[typing.Any] | None`
    :   List of customers involved in the conversation

    `first_contact_reply: dict[str, typing.Any] | None`
    :   Timestamp indicating when the first contact replied.

    `id: str | None`
    :   The unique ID of the conversation

    `linked_objects: dict[str, typing.Any] | None`
    :   Linked objects associated with the conversation

    `open: bool | None`
    :   Indicates if the conversation is open or closed

    `priority: str | None`
    :   The priority level of the conversation

    `read: bool | None`
    :   Indicates if the conversation has been read

    `redacted: bool | None`
    :   Indicates if the conversation is redacted

    `sent_at: int | None`
    :   The timestamp when the conversation was sent

    `sla_applied: dict[str, typing.Any] | None`
    :   Service Level Agreement details applied to the conversation.

    `snoozed_until: int | None`
    :   Timestamp until the conversation is snoozed

    `source: dict[str, typing.Any] | None`
    :   Source details of the conversation.

    `state: str | None`
    :   The state of the conversation (e.g., new, in progress)

    `statistics: dict[str, typing.Any] | None`
    :   Statistics related to the conversation.

    `tags: dict[str, typing.Any] | None`
    :   Tags applied to the conversation.

    `team_assignee_id: int | None`
    :   The ID of the team assigned to the conversation

    `teammates: dict[str, typing.Any] | None`
    :   List of teammates involved in the conversation.

    `title: str | None`
    :   The title of the conversation

    `topics: dict[str, typing.Any] | None`
    :   Topics associated with the conversation.

    `type_: str | None`
    :   The type of the conversation

    `updated_at: int | None`
    :   The timestamp when the conversation was last updated

    `user: dict[str, typing.Any] | None`
    :   The user related to the conversation.

    `waiting_since: int | None`
    :   Timestamp since waiting for a response

<a id="ConversationsSearchQuery"></a>

`ConversationsSearchQuery(*args, **kwargs)`
:   Search query for conversations entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.intercom.types.ConversationsEqCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsNeqCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsGtCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsGteCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsLtCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsLteCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsInCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsLikeCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsFuzzyCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsKeywordCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsContainsCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsNotCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsAndCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsOrCondition | airbyte_agent_sdk.connectors.intercom.types.ConversationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.intercom.types.ConversationsSortFilter]`
    :   The type of the None singleton.

<a id="ConversationsSortFilter"></a>

`ConversationsSortFilter(*args, **kwargs)`
:   Available fields for sorting conversations search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `admin_assignee_id: Literal['asc', 'desc']`
    :   The ID of the administrator assigned to the conversation

    `ai_agent: Literal['asc', 'desc']`
    :   Data related to AI Agent involvement in the conversation

    `ai_agent_participated: Literal['asc', 'desc']`
    :   Indicates whether AI Agent participated in the conversation

    `assignee: Literal['asc', 'desc']`
    :   The assigned user responsible for the conversation.

    `contacts: Literal['asc', 'desc']`
    :   List of contacts involved in the conversation.

    `conversation_message: Literal['asc', 'desc']`
    :   The main message content of the conversation.

    `conversation_rating: Literal['asc', 'desc']`
    :   Ratings given to the conversation by the customer and teammate.

    `created_at: Literal['asc', 'desc']`
    :   The timestamp when the conversation was created

    `custom_attributes: Literal['asc', 'desc']`
    :   Custom attributes associated with the conversation

    `customer_first_reply: Literal['asc', 'desc']`
    :   Timestamp indicating when the customer first replied.

    `customers: Literal['asc', 'desc']`
    :   List of customers involved in the conversation

    `first_contact_reply: Literal['asc', 'desc']`
    :   Timestamp indicating when the first contact replied.

    `id: Literal['asc', 'desc']`
    :   The unique ID of the conversation

    `linked_objects: Literal['asc', 'desc']`
    :   Linked objects associated with the conversation

    `open: Literal['asc', 'desc']`
    :   Indicates if the conversation is open or closed

    `priority: Literal['asc', 'desc']`
    :   The priority level of the conversation

    `read: Literal['asc', 'desc']`
    :   Indicates if the conversation has been read

    `redacted: Literal['asc', 'desc']`
    :   Indicates if the conversation is redacted

    `sent_at: Literal['asc', 'desc']`
    :   The timestamp when the conversation was sent

    `sla_applied: Literal['asc', 'desc']`
    :   Service Level Agreement details applied to the conversation.

    `snoozed_until: Literal['asc', 'desc']`
    :   Timestamp until the conversation is snoozed

    `source: Literal['asc', 'desc']`
    :   Source details of the conversation.

    `state: Literal['asc', 'desc']`
    :   The state of the conversation (e.g., new, in progress)

    `statistics: Literal['asc', 'desc']`
    :   Statistics related to the conversation.

    `tags: Literal['asc', 'desc']`
    :   Tags applied to the conversation.

    `team_assignee_id: Literal['asc', 'desc']`
    :   The ID of the team assigned to the conversation

    `teammates: Literal['asc', 'desc']`
    :   List of teammates involved in the conversation.

    `title: Literal['asc', 'desc']`
    :   The title of the conversation

    `topics: Literal['asc', 'desc']`
    :   Topics associated with the conversation.

    `type_: Literal['asc', 'desc']`
    :   The type of the conversation

    `updated_at: Literal['asc', 'desc']`
    :   The timestamp when the conversation was last updated

    `user: Literal['asc', 'desc']`
    :   The user related to the conversation.

    `waiting_since: Literal['asc', 'desc']`
    :   Timestamp since waiting for a response

<a id="ConversationsStringFilter"></a>

`ConversationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `admin_assignee_id: str`
    :   The ID of the administrator assigned to the conversation

    `ai_agent: str`
    :   Data related to AI Agent involvement in the conversation

    `ai_agent_participated: str`
    :   Indicates whether AI Agent participated in the conversation

    `assignee: str`
    :   The assigned user responsible for the conversation.

    `contacts: str`
    :   List of contacts involved in the conversation.

    `conversation_message: str`
    :   The main message content of the conversation.

    `conversation_rating: str`
    :   Ratings given to the conversation by the customer and teammate.

    `created_at: str`
    :   The timestamp when the conversation was created

    `custom_attributes: str`
    :   Custom attributes associated with the conversation

    `customer_first_reply: str`
    :   Timestamp indicating when the customer first replied.

    `customers: str`
    :   List of customers involved in the conversation

    `first_contact_reply: str`
    :   Timestamp indicating when the first contact replied.

    `id: str`
    :   The unique ID of the conversation

    `linked_objects: str`
    :   Linked objects associated with the conversation

    `open: str`
    :   Indicates if the conversation is open or closed

    `priority: str`
    :   The priority level of the conversation

    `read: str`
    :   Indicates if the conversation has been read

    `redacted: str`
    :   Indicates if the conversation is redacted

    `sent_at: str`
    :   The timestamp when the conversation was sent

    `sla_applied: str`
    :   Service Level Agreement details applied to the conversation.

    `snoozed_until: str`
    :   Timestamp until the conversation is snoozed

    `source: str`
    :   Source details of the conversation.

    `state: str`
    :   The state of the conversation (e.g., new, in progress)

    `statistics: str`
    :   Statistics related to the conversation.

    `tags: str`
    :   Tags applied to the conversation.

    `team_assignee_id: str`
    :   The ID of the team assigned to the conversation

    `teammates: str`
    :   List of teammates involved in the conversation.

    `title: str`
    :   The title of the conversation

    `topics: str`
    :   Topics associated with the conversation.

    `type_: str`
    :   The type of the conversation

    `updated_at: str`
    :   The timestamp when the conversation was last updated

    `user: str`
    :   The user related to the conversation.

    `waiting_since: str`
    :   Timestamp since waiting for a response

<a id="InternalArticlesCreateParams"></a>

`InternalArticlesCreateParams(*args, **kwargs)`
:   Parameters for internal_articles.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `author_id: int`
    :   The type of the None singleton.

    `body: str`
    :   The type of the None singleton.

    `owner_id: int`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="NotesCreateParams"></a>

`NotesCreateParams(*args, **kwargs)`
:   Parameters for notes.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `admin_id: str`
    :   The type of the None singleton.

    `body: str`
    :   The type of the None singleton.

    `contact_id: str`
    :   The type of the None singleton.

<a id="SegmentsGetParams"></a>

`SegmentsGetParams(*args, **kwargs)`
:   Parameters for segments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="SegmentsListParams"></a>

`SegmentsListParams(*args, **kwargs)`
:   Parameters for segments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `include_count: bool`
    :   The type of the None singleton.

<a id="TagsCreateParams"></a>

`TagsCreateParams(*args, **kwargs)`
:   Parameters for tags.create operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `name: str`
    :   The type of the None singleton.

<a id="TagsGetParams"></a>

`TagsGetParams(*args, **kwargs)`
:   Parameters for tags.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="TagsListParams"></a>

`TagsListParams(*args, **kwargs)`
:   Parameters for tags.list operation

    ### Ancestors (in MRO)

    * builtins.dict

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

    `and: list[airbyte_agent_sdk.connectors.intercom.types.TeamsEqCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsGtCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsGteCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsLtCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsLteCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsInCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsNotCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsAndCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsOrCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.intercom.types.TeamsAnyValueFilter`
    :   The type of the None singleton.

<a id="TeamsAnyValueFilter"></a>

`TeamsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `admin_ids: Any`
    :   Array of user IDs representing the admins of the team.

    `id: Any`
    :   Unique identifier for the team.

    `name: Any`
    :   Name of the team.

    `type_: Any`
    :   Type of team (e.g., 'internal', 'external').

<a id="TeamsContainsCondition"></a>

`TeamsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.intercom.types.TeamsAnyValueFilter`
    :   The type of the None singleton.

<a id="TeamsEqCondition"></a>

`TeamsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.intercom.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsFuzzyCondition"></a>

`TeamsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.intercom.types.TeamsStringFilter`
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

    `gt: airbyte_agent_sdk.connectors.intercom.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsGteCondition"></a>

`TeamsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.intercom.types.TeamsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.intercom.types.TeamsInFilter`
    :   The type of the None singleton.

<a id="TeamsInFilter"></a>

`TeamsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `admin_ids: list[list[typing.Any]]`
    :   Array of user IDs representing the admins of the team.

    `id: list[str]`
    :   Unique identifier for the team.

    `name: list[str]`
    :   Name of the team.

    `type_: list[str]`
    :   Type of team (e.g., 'internal', 'external').

<a id="TeamsKeywordCondition"></a>

`TeamsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.intercom.types.TeamsStringFilter`
    :   The type of the None singleton.

<a id="TeamsLikeCondition"></a>

`TeamsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.intercom.types.TeamsStringFilter`
    :   The type of the None singleton.

<a id="TeamsListParams"></a>

`TeamsListParams(*args, **kwargs)`
:   Parameters for teams.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="TeamsLtCondition"></a>

`TeamsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.intercom.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsLteCondition"></a>

`TeamsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.intercom.types.TeamsSearchFilter`
    :   The type of the None singleton.

<a id="TeamsNeqCondition"></a>

`TeamsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.intercom.types.TeamsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.intercom.types.TeamsEqCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsGtCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsGteCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsLtCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsLteCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsInCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsNotCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsAndCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsOrCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.intercom.types.TeamsEqCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsGtCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsGteCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsLtCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsLteCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsInCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsNotCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsAndCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsOrCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsAnyCondition]`
    :   The type of the None singleton.

<a id="TeamsSearchFilter"></a>

`TeamsSearchFilter(*args, **kwargs)`
:   Available fields for filtering teams search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `admin_ids: list[typing.Any] | None`
    :   Array of user IDs representing the admins of the team.

    `id: str | None`
    :   Unique identifier for the team.

    `name: str | None`
    :   Name of the team.

    `type_: str | None`
    :   Type of team (e.g., 'internal', 'external').

<a id="TeamsSearchQuery"></a>

`TeamsSearchQuery(*args, **kwargs)`
:   Search query for teams entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.intercom.types.TeamsEqCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsNeqCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsGtCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsGteCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsLtCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsLteCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsInCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsLikeCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsFuzzyCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsKeywordCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsContainsCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsNotCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsAndCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsOrCondition | airbyte_agent_sdk.connectors.intercom.types.TeamsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.intercom.types.TeamsSortFilter]`
    :   The type of the None singleton.

<a id="TeamsSortFilter"></a>

`TeamsSortFilter(*args, **kwargs)`
:   Available fields for sorting teams search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `admin_ids: Literal['asc', 'desc']`
    :   Array of user IDs representing the admins of the team.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the team.

    `name: Literal['asc', 'desc']`
    :   Name of the team.

    `type_: Literal['asc', 'desc']`
    :   Type of team (e.g., 'internal', 'external').

<a id="TeamsStringFilter"></a>

`TeamsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `admin_ids: str`
    :   Array of user IDs representing the admins of the team.

    `id: str`
    :   Unique identifier for the team.

    `name: str`
    :   Name of the team.

    `type_: str`
    :   Type of team (e.g., 'internal', 'external').