---
id: airbyte_agent_sdk-connectors-snapchat_marketing-types
title: airbyte_agent_sdk.connectors.snapchat_marketing.types
---

Module airbyte_agent_sdk.connectors.snapchat_marketing.types
============================================================
Type definitions for snapchat-marketing connector.

Classes
-------

<a id="AdaccountsAndCondition"></a>

`AdaccountsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsAnyCondition]`
    :   The type of the None singleton.

<a id="AdaccountsAnyCondition"></a>

`AdaccountsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdaccountsAnyValueFilter"></a>

`AdaccountsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_organization_id: Any`
    :   Advertiser organization ID

    `agency_representing_client: Any`
    :   Whether the account is managed by an agency

    `billing_center_id: Any`
    :   Billing center ID

    `billing_type: Any`
    :   Billing type

    `client_paying_invoices: Any`
    :   Whether the client pays invoices directly

    `created_at: Any`
    :   Creation timestamp

    `currency: Any`
    :   Account currency code

    `funding_source_ids: Any`
    :   Associated funding source IDs

    `id: Any`
    :   Unique ad account identifier

    `name: Any`
    :   Ad account name

    `organization_id: Any`
    :   Parent organization ID

    `regulations: Any`
    :   Regulatory settings

    `status: Any`
    :   Ad account status

    `timezone: Any`
    :   Account timezone

    `type_: Any`
    :   Ad account type

    `updated_at: Any`
    :   Last update timestamp

<a id="AdaccountsContainsCondition"></a>

`AdaccountsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdaccountsEqCondition"></a>

`AdaccountsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsSearchFilter`
    :   The type of the None singleton.

<a id="AdaccountsFuzzyCondition"></a>

`AdaccountsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsStringFilter`
    :   The type of the None singleton.

<a id="AdaccountsGetParams"></a>

`AdaccountsGetParams(*args, **kwargs)`
:   Parameters for adaccounts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="AdaccountsGtCondition"></a>

`AdaccountsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsSearchFilter`
    :   The type of the None singleton.

<a id="AdaccountsGteCondition"></a>

`AdaccountsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsSearchFilter`
    :   The type of the None singleton.

<a id="AdaccountsInCondition"></a>

`AdaccountsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsInFilter`
    :   The type of the None singleton.

<a id="AdaccountsInFilter"></a>

`AdaccountsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_organization_id: list[str]`
    :   Advertiser organization ID

    `agency_representing_client: list[bool]`
    :   Whether the account is managed by an agency

    `billing_center_id: list[str]`
    :   Billing center ID

    `billing_type: list[str]`
    :   Billing type

    `client_paying_invoices: list[bool]`
    :   Whether the client pays invoices directly

    `created_at: list[str]`
    :   Creation timestamp

    `currency: list[str]`
    :   Account currency code

    `funding_source_ids: list[list[typing.Any]]`
    :   Associated funding source IDs

    `id: list[str]`
    :   Unique ad account identifier

    `name: list[str]`
    :   Ad account name

    `organization_id: list[str]`
    :   Parent organization ID

    `regulations: list[dict[str, typing.Any]]`
    :   Regulatory settings

    `status: list[str]`
    :   Ad account status

    `timezone: list[str]`
    :   Account timezone

    `type_: list[str]`
    :   Ad account type

    `updated_at: list[str]`
    :   Last update timestamp

<a id="AdaccountsKeywordCondition"></a>

`AdaccountsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsStringFilter`
    :   The type of the None singleton.

<a id="AdaccountsLikeCondition"></a>

`AdaccountsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsStringFilter`
    :   The type of the None singleton.

<a id="AdaccountsListParams"></a>

`AdaccountsListParams(*args, **kwargs)`
:   Parameters for adaccounts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `organization_id: str`
    :   The type of the None singleton.

<a id="AdaccountsLtCondition"></a>

`AdaccountsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsSearchFilter`
    :   The type of the None singleton.

<a id="AdaccountsLteCondition"></a>

`AdaccountsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsSearchFilter`
    :   The type of the None singleton.

<a id="AdaccountsNeqCondition"></a>

`AdaccountsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsSearchFilter`
    :   The type of the None singleton.

<a id="AdaccountsNotCondition"></a>

`AdaccountsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsAnyCondition`
    :   The type of the None singleton.

<a id="AdaccountsOrCondition"></a>

`AdaccountsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsAnyCondition]`
    :   The type of the None singleton.

<a id="AdaccountsSearchFilter"></a>

`AdaccountsSearchFilter(*args, **kwargs)`
:   Available fields for filtering adaccounts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_organization_id: str | None`
    :   Advertiser organization ID

    `agency_representing_client: bool | None`
    :   Whether the account is managed by an agency

    `billing_center_id: str | None`
    :   Billing center ID

    `billing_type: str | None`
    :   Billing type

    `client_paying_invoices: bool | None`
    :   Whether the client pays invoices directly

    `created_at: str | None`
    :   Creation timestamp

    `currency: str | None`
    :   Account currency code

    `funding_source_ids: list[typing.Any] | None`
    :   Associated funding source IDs

    `id: str | None`
    :   Unique ad account identifier

    `name: str | None`
    :   Ad account name

    `organization_id: str | None`
    :   Parent organization ID

    `regulations: dict[str, typing.Any] | None`
    :   Regulatory settings

    `status: str | None`
    :   Ad account status

    `timezone: str | None`
    :   Account timezone

    `type_: str | None`
    :   Ad account type

    `updated_at: str | None`
    :   Last update timestamp

<a id="AdaccountsSearchQuery"></a>

`AdaccountsSearchQuery(*args, **kwargs)`
:   Search query for adaccounts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.AdaccountsSortFilter]`
    :   The type of the None singleton.

<a id="AdaccountsSortFilter"></a>

`AdaccountsSortFilter(*args, **kwargs)`
:   Available fields for sorting adaccounts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_organization_id: Literal['asc', 'desc']`
    :   Advertiser organization ID

    `agency_representing_client: Literal['asc', 'desc']`
    :   Whether the account is managed by an agency

    `billing_center_id: Literal['asc', 'desc']`
    :   Billing center ID

    `billing_type: Literal['asc', 'desc']`
    :   Billing type

    `client_paying_invoices: Literal['asc', 'desc']`
    :   Whether the client pays invoices directly

    `created_at: Literal['asc', 'desc']`
    :   Creation timestamp

    `currency: Literal['asc', 'desc']`
    :   Account currency code

    `funding_source_ids: Literal['asc', 'desc']`
    :   Associated funding source IDs

    `id: Literal['asc', 'desc']`
    :   Unique ad account identifier

    `name: Literal['asc', 'desc']`
    :   Ad account name

    `organization_id: Literal['asc', 'desc']`
    :   Parent organization ID

    `regulations: Literal['asc', 'desc']`
    :   Regulatory settings

    `status: Literal['asc', 'desc']`
    :   Ad account status

    `timezone: Literal['asc', 'desc']`
    :   Account timezone

    `type_: Literal['asc', 'desc']`
    :   Ad account type

    `updated_at: Literal['asc', 'desc']`
    :   Last update timestamp

<a id="AdaccountsStringFilter"></a>

`AdaccountsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `advertiser_organization_id: str`
    :   Advertiser organization ID

    `agency_representing_client: str`
    :   Whether the account is managed by an agency

    `billing_center_id: str`
    :   Billing center ID

    `billing_type: str`
    :   Billing type

    `client_paying_invoices: str`
    :   Whether the client pays invoices directly

    `created_at: str`
    :   Creation timestamp

    `currency: str`
    :   Account currency code

    `funding_source_ids: str`
    :   Associated funding source IDs

    `id: str`
    :   Unique ad account identifier

    `name: str`
    :   Ad account name

    `organization_id: str`
    :   Parent organization ID

    `regulations: str`
    :   Regulatory settings

    `status: str`
    :   Ad account status

    `timezone: str`
    :   Account timezone

    `type_: str`
    :   Ad account type

    `updated_at: str`
    :   Last update timestamp

<a id="AdsAndCondition"></a>

`AdsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsAnyCondition]`
    :   The type of the None singleton.

<a id="AdsAnyCondition"></a>

`AdsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdsAnyValueFilter"></a>

`AdsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_squad_id: Any`
    :   Parent ad squad ID

    `created_at: Any`
    :   Creation timestamp

    `creative_id: Any`
    :   Associated creative ID

    `delivery_status: Any`
    :   Delivery status messages

    `id: Any`
    :   Unique ad identifier

    `name: Any`
    :   Ad name

    `render_type: Any`
    :   Render type

    `review_status: Any`
    :   Review status

    `review_status_reasons: Any`
    :   Reasons for review status

    `status: Any`
    :   Ad status

    `type_: Any`
    :   Ad type

    `updated_at: Any`
    :   Last update timestamp

<a id="AdsContainsCondition"></a>

`AdsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdsEqCondition"></a>

`AdsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

<a id="AdsFuzzyCondition"></a>

`AdsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsStringFilter`
    :   The type of the None singleton.

<a id="AdsGetParams"></a>

`AdsGetParams(*args, **kwargs)`
:   Parameters for ads.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="AdsGtCondition"></a>

`AdsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

<a id="AdsGteCondition"></a>

`AdsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

<a id="AdsInCondition"></a>

`AdsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsInFilter`
    :   The type of the None singleton.

<a id="AdsInFilter"></a>

`AdsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_squad_id: list[str]`
    :   Parent ad squad ID

    `created_at: list[str]`
    :   Creation timestamp

    `creative_id: list[str]`
    :   Associated creative ID

    `delivery_status: list[list[typing.Any]]`
    :   Delivery status messages

    `id: list[str]`
    :   Unique ad identifier

    `name: list[str]`
    :   Ad name

    `render_type: list[str]`
    :   Render type

    `review_status: list[str]`
    :   Review status

    `review_status_reasons: list[list[typing.Any]]`
    :   Reasons for review status

    `status: list[str]`
    :   Ad status

    `type_: list[str]`
    :   Ad type

    `updated_at: list[str]`
    :   Last update timestamp

<a id="AdsKeywordCondition"></a>

`AdsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsStringFilter`
    :   The type of the None singleton.

<a id="AdsLikeCondition"></a>

`AdsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsStringFilter`
    :   The type of the None singleton.

<a id="AdsListParams"></a>

`AdsListParams(*args, **kwargs)`
:   Parameters for ads.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

<a id="AdsLtCondition"></a>

`AdsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

<a id="AdsLteCondition"></a>

`AdsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

<a id="AdsNeqCondition"></a>

`AdsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsSearchFilter`
    :   The type of the None singleton.

<a id="AdsNotCondition"></a>

`AdsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsAnyCondition`
    :   The type of the None singleton.

<a id="AdsOrCondition"></a>

`AdsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsAnyCondition]`
    :   The type of the None singleton.

<a id="AdsSearchFilter"></a>

`AdsSearchFilter(*args, **kwargs)`
:   Available fields for filtering ads search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_squad_id: str | None`
    :   Parent ad squad ID

    `created_at: str | None`
    :   Creation timestamp

    `creative_id: str | None`
    :   Associated creative ID

    `delivery_status: list[typing.Any] | None`
    :   Delivery status messages

    `id: str | None`
    :   Unique ad identifier

    `name: str | None`
    :   Ad name

    `render_type: str | None`
    :   Render type

    `review_status: str | None`
    :   Review status

    `review_status_reasons: list[typing.Any] | None`
    :   Reasons for review status

    `status: str | None`
    :   Ad status

    `type_: str | None`
    :   Ad type

    `updated_at: str | None`
    :   Last update timestamp

<a id="AdsSearchQuery"></a>

`AdsSearchQuery(*args, **kwargs)`
:   Search query for ads entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsSortFilter]`
    :   The type of the None singleton.

<a id="AdsSortFilter"></a>

`AdsSortFilter(*args, **kwargs)`
:   Available fields for sorting ads search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_squad_id: Literal['asc', 'desc']`
    :   Parent ad squad ID

    `created_at: Literal['asc', 'desc']`
    :   Creation timestamp

    `creative_id: Literal['asc', 'desc']`
    :   Associated creative ID

    `delivery_status: Literal['asc', 'desc']`
    :   Delivery status messages

    `id: Literal['asc', 'desc']`
    :   Unique ad identifier

    `name: Literal['asc', 'desc']`
    :   Ad name

    `render_type: Literal['asc', 'desc']`
    :   Render type

    `review_status: Literal['asc', 'desc']`
    :   Review status

    `review_status_reasons: Literal['asc', 'desc']`
    :   Reasons for review status

    `status: Literal['asc', 'desc']`
    :   Ad status

    `type_: Literal['asc', 'desc']`
    :   Ad type

    `updated_at: Literal['asc', 'desc']`
    :   Last update timestamp

<a id="AdsStringFilter"></a>

`AdsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_squad_id: str`
    :   Parent ad squad ID

    `created_at: str`
    :   Creation timestamp

    `creative_id: str`
    :   Associated creative ID

    `delivery_status: str`
    :   Delivery status messages

    `id: str`
    :   Unique ad identifier

    `name: str`
    :   Ad name

    `render_type: str`
    :   Render type

    `review_status: str`
    :   Review status

    `review_status_reasons: str`
    :   Reasons for review status

    `status: str`
    :   Ad status

    `type_: str`
    :   Ad type

    `updated_at: str`
    :   Last update timestamp

<a id="AdsquadsAndCondition"></a>

`AdsquadsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsAnyCondition]`
    :   The type of the None singleton.

<a id="AdsquadsAnyCondition"></a>

`AdsquadsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdsquadsAnyValueFilter"></a>

`AdsquadsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auto_bid: Any`
    :   Whether auto bidding is enabled

    `bid_strategy: Any`
    :   Bid strategy

    `billing_event: Any`
    :   Billing event type

    `campaign_id: Any`
    :   Parent campaign ID

    `child_ad_type: Any`
    :   Child ad type

    `created_at: Any`
    :   Creation timestamp

    `creation_state: Any`
    :   Creation state

    `daily_budget_micro: Any`
    :   Daily budget in micro-currency

    `delivery_constraint: Any`
    :   Delivery constraint

    `delivery_properties_version: Any`
    :   Delivery properties version

    `delivery_status: Any`
    :   Delivery status messages

    `end_time: Any`
    :   Ad squad end time

    `event_sources: Any`
    :   Event sources configuration

    `forced_view_setting: Any`
    :   Forced view setting

    `id: Any`
    :   Unique ad squad identifier

    `lifetime_budget_micro: Any`
    :   Lifetime budget in micro-currency

    `name: Any`
    :   Ad squad name

    `optimization_goal: Any`
    :   Optimization goal

    `pacing_type: Any`
    :   Pacing type

    `placement: Any`
    :   Placement type

    `skadnetwork_properties: Any`
    :   SKAdNetwork properties

    `start_time: Any`
    :   Ad squad start time

    `status: Any`
    :   Ad squad status

    `target_bid: Any`
    :   Whether target bid is enabled

    `targeting: Any`
    :   Targeting specification

    `targeting_reach_status: Any`
    :   Targeting reach status

    `type_: Any`
    :   Ad squad type

    `updated_at: Any`
    :   Last update timestamp

<a id="AdsquadsContainsCondition"></a>

`AdsquadsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsAnyValueFilter`
    :   The type of the None singleton.

<a id="AdsquadsEqCondition"></a>

`AdsquadsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsSearchFilter`
    :   The type of the None singleton.

<a id="AdsquadsFuzzyCondition"></a>

`AdsquadsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsStringFilter`
    :   The type of the None singleton.

<a id="AdsquadsGetParams"></a>

`AdsquadsGetParams(*args, **kwargs)`
:   Parameters for adsquads.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="AdsquadsGtCondition"></a>

`AdsquadsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsSearchFilter`
    :   The type of the None singleton.

<a id="AdsquadsGteCondition"></a>

`AdsquadsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsSearchFilter`
    :   The type of the None singleton.

<a id="AdsquadsInCondition"></a>

`AdsquadsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsInFilter`
    :   The type of the None singleton.

<a id="AdsquadsInFilter"></a>

`AdsquadsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auto_bid: list[bool]`
    :   Whether auto bidding is enabled

    `bid_strategy: list[str]`
    :   Bid strategy

    `billing_event: list[str]`
    :   Billing event type

    `campaign_id: list[str]`
    :   Parent campaign ID

    `child_ad_type: list[str]`
    :   Child ad type

    `created_at: list[str]`
    :   Creation timestamp

    `creation_state: list[str]`
    :   Creation state

    `daily_budget_micro: list[int]`
    :   Daily budget in micro-currency

    `delivery_constraint: list[str]`
    :   Delivery constraint

    `delivery_properties_version: list[int]`
    :   Delivery properties version

    `delivery_status: list[list[typing.Any]]`
    :   Delivery status messages

    `end_time: list[str]`
    :   Ad squad end time

    `event_sources: list[dict[str, typing.Any]]`
    :   Event sources configuration

    `forced_view_setting: list[str]`
    :   Forced view setting

    `id: list[str]`
    :   Unique ad squad identifier

    `lifetime_budget_micro: list[int]`
    :   Lifetime budget in micro-currency

    `name: list[str]`
    :   Ad squad name

    `optimization_goal: list[str]`
    :   Optimization goal

    `pacing_type: list[str]`
    :   Pacing type

    `placement: list[str]`
    :   Placement type

    `skadnetwork_properties: list[dict[str, typing.Any]]`
    :   SKAdNetwork properties

    `start_time: list[str]`
    :   Ad squad start time

    `status: list[str]`
    :   Ad squad status

    `target_bid: list[bool]`
    :   Whether target bid is enabled

    `targeting: list[dict[str, typing.Any]]`
    :   Targeting specification

    `targeting_reach_status: list[str]`
    :   Targeting reach status

    `type_: list[str]`
    :   Ad squad type

    `updated_at: list[str]`
    :   Last update timestamp

<a id="AdsquadsKeywordCondition"></a>

`AdsquadsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsStringFilter`
    :   The type of the None singleton.

<a id="AdsquadsLikeCondition"></a>

`AdsquadsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsStringFilter`
    :   The type of the None singleton.

<a id="AdsquadsListParams"></a>

`AdsquadsListParams(*args, **kwargs)`
:   Parameters for adsquads.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

<a id="AdsquadsLtCondition"></a>

`AdsquadsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsSearchFilter`
    :   The type of the None singleton.

<a id="AdsquadsLteCondition"></a>

`AdsquadsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsSearchFilter`
    :   The type of the None singleton.

<a id="AdsquadsNeqCondition"></a>

`AdsquadsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsSearchFilter`
    :   The type of the None singleton.

<a id="AdsquadsNotCondition"></a>

`AdsquadsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsAnyCondition`
    :   The type of the None singleton.

<a id="AdsquadsOrCondition"></a>

`AdsquadsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsAnyCondition]`
    :   The type of the None singleton.

<a id="AdsquadsSearchFilter"></a>

`AdsquadsSearchFilter(*args, **kwargs)`
:   Available fields for filtering adsquads search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auto_bid: bool | None`
    :   Whether auto bidding is enabled

    `bid_strategy: str | None`
    :   Bid strategy

    `billing_event: str | None`
    :   Billing event type

    `campaign_id: str | None`
    :   Parent campaign ID

    `child_ad_type: str | None`
    :   Child ad type

    `created_at: str | None`
    :   Creation timestamp

    `creation_state: str | None`
    :   Creation state

    `daily_budget_micro: int | None`
    :   Daily budget in micro-currency

    `delivery_constraint: str | None`
    :   Delivery constraint

    `delivery_properties_version: int | None`
    :   Delivery properties version

    `delivery_status: list[typing.Any] | None`
    :   Delivery status messages

    `end_time: str | None`
    :   Ad squad end time

    `event_sources: dict[str, typing.Any] | None`
    :   Event sources configuration

    `forced_view_setting: str | None`
    :   Forced view setting

    `id: str | None`
    :   Unique ad squad identifier

    `lifetime_budget_micro: int | None`
    :   Lifetime budget in micro-currency

    `name: str | None`
    :   Ad squad name

    `optimization_goal: str | None`
    :   Optimization goal

    `pacing_type: str | None`
    :   Pacing type

    `placement: str | None`
    :   Placement type

    `skadnetwork_properties: dict[str, typing.Any] | None`
    :   SKAdNetwork properties

    `start_time: str | None`
    :   Ad squad start time

    `status: str | None`
    :   Ad squad status

    `target_bid: bool | None`
    :   Whether target bid is enabled

    `targeting: dict[str, typing.Any] | None`
    :   Targeting specification

    `targeting_reach_status: str | None`
    :   Targeting reach status

    `type_: str | None`
    :   Ad squad type

    `updated_at: str | None`
    :   Last update timestamp

<a id="AdsquadsSearchQuery"></a>

`AdsquadsSearchQuery(*args, **kwargs)`
:   Search query for adsquads entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.AdsquadsSortFilter]`
    :   The type of the None singleton.

<a id="AdsquadsSortFilter"></a>

`AdsquadsSortFilter(*args, **kwargs)`
:   Available fields for sorting adsquads search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auto_bid: Literal['asc', 'desc']`
    :   Whether auto bidding is enabled

    `bid_strategy: Literal['asc', 'desc']`
    :   Bid strategy

    `billing_event: Literal['asc', 'desc']`
    :   Billing event type

    `campaign_id: Literal['asc', 'desc']`
    :   Parent campaign ID

    `child_ad_type: Literal['asc', 'desc']`
    :   Child ad type

    `created_at: Literal['asc', 'desc']`
    :   Creation timestamp

    `creation_state: Literal['asc', 'desc']`
    :   Creation state

    `daily_budget_micro: Literal['asc', 'desc']`
    :   Daily budget in micro-currency

    `delivery_constraint: Literal['asc', 'desc']`
    :   Delivery constraint

    `delivery_properties_version: Literal['asc', 'desc']`
    :   Delivery properties version

    `delivery_status: Literal['asc', 'desc']`
    :   Delivery status messages

    `end_time: Literal['asc', 'desc']`
    :   Ad squad end time

    `event_sources: Literal['asc', 'desc']`
    :   Event sources configuration

    `forced_view_setting: Literal['asc', 'desc']`
    :   Forced view setting

    `id: Literal['asc', 'desc']`
    :   Unique ad squad identifier

    `lifetime_budget_micro: Literal['asc', 'desc']`
    :   Lifetime budget in micro-currency

    `name: Literal['asc', 'desc']`
    :   Ad squad name

    `optimization_goal: Literal['asc', 'desc']`
    :   Optimization goal

    `pacing_type: Literal['asc', 'desc']`
    :   Pacing type

    `placement: Literal['asc', 'desc']`
    :   Placement type

    `skadnetwork_properties: Literal['asc', 'desc']`
    :   SKAdNetwork properties

    `start_time: Literal['asc', 'desc']`
    :   Ad squad start time

    `status: Literal['asc', 'desc']`
    :   Ad squad status

    `target_bid: Literal['asc', 'desc']`
    :   Whether target bid is enabled

    `targeting: Literal['asc', 'desc']`
    :   Targeting specification

    `targeting_reach_status: Literal['asc', 'desc']`
    :   Targeting reach status

    `type_: Literal['asc', 'desc']`
    :   Ad squad type

    `updated_at: Literal['asc', 'desc']`
    :   Last update timestamp

<a id="AdsquadsStringFilter"></a>

`AdsquadsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auto_bid: str`
    :   Whether auto bidding is enabled

    `bid_strategy: str`
    :   Bid strategy

    `billing_event: str`
    :   Billing event type

    `campaign_id: str`
    :   Parent campaign ID

    `child_ad_type: str`
    :   Child ad type

    `created_at: str`
    :   Creation timestamp

    `creation_state: str`
    :   Creation state

    `daily_budget_micro: str`
    :   Daily budget in micro-currency

    `delivery_constraint: str`
    :   Delivery constraint

    `delivery_properties_version: str`
    :   Delivery properties version

    `delivery_status: str`
    :   Delivery status messages

    `end_time: str`
    :   Ad squad end time

    `event_sources: str`
    :   Event sources configuration

    `forced_view_setting: str`
    :   Forced view setting

    `id: str`
    :   Unique ad squad identifier

    `lifetime_budget_micro: str`
    :   Lifetime budget in micro-currency

    `name: str`
    :   Ad squad name

    `optimization_goal: str`
    :   Optimization goal

    `pacing_type: str`
    :   Pacing type

    `placement: str`
    :   Placement type

    `skadnetwork_properties: str`
    :   SKAdNetwork properties

    `start_time: str`
    :   Ad squad start time

    `status: str`
    :   Ad squad status

    `target_bid: str`
    :   Whether target bid is enabled

    `targeting: str`
    :   Targeting specification

    `targeting_reach_status: str`
    :   Targeting reach status

    `type_: str`
    :   Ad squad type

    `updated_at: str`
    :   Last update timestamp

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

<a id="CampaignsAndCondition"></a>

`CampaignsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignsAnyCondition"></a>

`CampaignsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsAnyValueFilter"></a>

`CampaignsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Any`
    :   Parent ad account ID

    `buy_model: Any`
    :   Buy model type

    `created_at: Any`
    :   Creation timestamp

    `creation_state: Any`
    :   Creation state

    `delivery_status: Any`
    :   Delivery status messages

    `id: Any`
    :   Unique campaign identifier

    `name: Any`
    :   Campaign name

    `objective: Any`
    :   Campaign objective

    `start_time: Any`
    :   Campaign start time

    `status: Any`
    :   Campaign status

    `updated_at: Any`
    :   Last update timestamp

<a id="CampaignsContainsCondition"></a>

`CampaignsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsEqCondition"></a>

`CampaignsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsFuzzyCondition"></a>

`CampaignsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsGetParams"></a>

`CampaignsGetParams(*args, **kwargs)`
:   Parameters for campaigns.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CampaignsGtCondition"></a>

`CampaignsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsGteCondition"></a>

`CampaignsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsInCondition"></a>

`CampaignsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsInFilter`
    :   The type of the None singleton.

<a id="CampaignsInFilter"></a>

`CampaignsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: list[str]`
    :   Parent ad account ID

    `buy_model: list[str]`
    :   Buy model type

    `created_at: list[str]`
    :   Creation timestamp

    `creation_state: list[str]`
    :   Creation state

    `delivery_status: list[list[typing.Any]]`
    :   Delivery status messages

    `id: list[str]`
    :   Unique campaign identifier

    `name: list[str]`
    :   Campaign name

    `objective: list[str]`
    :   Campaign objective

    `start_time: list[str]`
    :   Campaign start time

    `status: list[str]`
    :   Campaign status

    `updated_at: list[str]`
    :   Last update timestamp

<a id="CampaignsKeywordCondition"></a>

`CampaignsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsLikeCondition"></a>

`CampaignsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsListParams"></a>

`CampaignsListParams(*args, **kwargs)`
:   Parameters for campaigns.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

<a id="CampaignsLtCondition"></a>

`CampaignsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsLteCondition"></a>

`CampaignsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsNeqCondition"></a>

`CampaignsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsNotCondition"></a>

`CampaignsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsAnyCondition`
    :   The type of the None singleton.

<a id="CampaignsOrCondition"></a>

`CampaignsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignsSearchFilter"></a>

`CampaignsSearchFilter(*args, **kwargs)`
:   Available fields for filtering campaigns search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str | None`
    :   Parent ad account ID

    `buy_model: str | None`
    :   Buy model type

    `created_at: str | None`
    :   Creation timestamp

    `creation_state: str | None`
    :   Creation state

    `delivery_status: list[typing.Any] | None`
    :   Delivery status messages

    `id: str | None`
    :   Unique campaign identifier

    `name: str | None`
    :   Campaign name

    `objective: str | None`
    :   Campaign objective

    `start_time: str | None`
    :   Campaign start time

    `status: str | None`
    :   Campaign status

    `updated_at: str | None`
    :   Last update timestamp

<a id="CampaignsSearchQuery"></a>

`CampaignsSearchQuery(*args, **kwargs)`
:   Search query for campaigns entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.CampaignsSortFilter]`
    :   The type of the None singleton.

<a id="CampaignsSortFilter"></a>

`CampaignsSortFilter(*args, **kwargs)`
:   Available fields for sorting campaigns search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Literal['asc', 'desc']`
    :   Parent ad account ID

    `buy_model: Literal['asc', 'desc']`
    :   Buy model type

    `created_at: Literal['asc', 'desc']`
    :   Creation timestamp

    `creation_state: Literal['asc', 'desc']`
    :   Creation state

    `delivery_status: Literal['asc', 'desc']`
    :   Delivery status messages

    `id: Literal['asc', 'desc']`
    :   Unique campaign identifier

    `name: Literal['asc', 'desc']`
    :   Campaign name

    `objective: Literal['asc', 'desc']`
    :   Campaign objective

    `start_time: Literal['asc', 'desc']`
    :   Campaign start time

    `status: Literal['asc', 'desc']`
    :   Campaign status

    `updated_at: Literal['asc', 'desc']`
    :   Last update timestamp

<a id="CampaignsStringFilter"></a>

`CampaignsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   Parent ad account ID

    `buy_model: str`
    :   Buy model type

    `created_at: str`
    :   Creation timestamp

    `creation_state: str`
    :   Creation state

    `delivery_status: str`
    :   Delivery status messages

    `id: str`
    :   Unique campaign identifier

    `name: str`
    :   Campaign name

    `objective: str`
    :   Campaign objective

    `start_time: str`
    :   Campaign start time

    `status: str`
    :   Campaign status

    `updated_at: str`
    :   Last update timestamp

<a id="CreativesAndCondition"></a>

`CreativesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesAnyCondition]`
    :   The type of the None singleton.

<a id="CreativesAnyCondition"></a>

`CreativesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesAnyValueFilter`
    :   The type of the None singleton.

<a id="CreativesAnyValueFilter"></a>

`CreativesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Any`
    :   Parent ad account ID

    `ad_product: Any`
    :   Ad product type

    `ad_to_place_properties: Any`
    :   Ad-to-place properties

    `brand_name: Any`
    :   Brand name displayed in the creative

    `call_to_action: Any`
    :   Call to action text

    `created_at: Any`
    :   Creation timestamp

    `forced_view_eligibility: Any`
    :   Forced view eligibility status

    `headline: Any`
    :   Creative headline

    `id: Any`
    :   Unique creative identifier

    `name: Any`
    :   Creative name

    `packaging_status: Any`
    :   Packaging status

    `render_type: Any`
    :   Render type

    `review_status: Any`
    :   Review status

    `review_status_details: Any`
    :   Details about the review status

    `shareable: Any`
    :   Whether the creative is shareable

    `top_snap_crop_position: Any`
    :   Top snap crop position

    `top_snap_media_id: Any`
    :   Top snap media ID

    `type_: Any`
    :   Creative type

    `updated_at: Any`
    :   Last update timestamp

    `web_view_properties: Any`
    :   Web view properties

<a id="CreativesContainsCondition"></a>

`CreativesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesAnyValueFilter`
    :   The type of the None singleton.

<a id="CreativesEqCondition"></a>

`CreativesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesSearchFilter`
    :   The type of the None singleton.

<a id="CreativesFuzzyCondition"></a>

`CreativesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesStringFilter`
    :   The type of the None singleton.

<a id="CreativesGetParams"></a>

`CreativesGetParams(*args, **kwargs)`
:   Parameters for creatives.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CreativesGtCondition"></a>

`CreativesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesSearchFilter`
    :   The type of the None singleton.

<a id="CreativesGteCondition"></a>

`CreativesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesSearchFilter`
    :   The type of the None singleton.

<a id="CreativesInCondition"></a>

`CreativesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesInFilter`
    :   The type of the None singleton.

<a id="CreativesInFilter"></a>

`CreativesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: list[str]`
    :   Parent ad account ID

    `ad_product: list[str]`
    :   Ad product type

    `ad_to_place_properties: list[dict[str, typing.Any]]`
    :   Ad-to-place properties

    `brand_name: list[str]`
    :   Brand name displayed in the creative

    `call_to_action: list[str]`
    :   Call to action text

    `created_at: list[str]`
    :   Creation timestamp

    `forced_view_eligibility: list[str]`
    :   Forced view eligibility status

    `headline: list[str]`
    :   Creative headline

    `id: list[str]`
    :   Unique creative identifier

    `name: list[str]`
    :   Creative name

    `packaging_status: list[str]`
    :   Packaging status

    `render_type: list[str]`
    :   Render type

    `review_status: list[str]`
    :   Review status

    `review_status_details: list[str]`
    :   Details about the review status

    `shareable: list[bool]`
    :   Whether the creative is shareable

    `top_snap_crop_position: list[str]`
    :   Top snap crop position

    `top_snap_media_id: list[str]`
    :   Top snap media ID

    `type_: list[str]`
    :   Creative type

    `updated_at: list[str]`
    :   Last update timestamp

    `web_view_properties: list[dict[str, typing.Any]]`
    :   Web view properties

<a id="CreativesKeywordCondition"></a>

`CreativesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesStringFilter`
    :   The type of the None singleton.

<a id="CreativesLikeCondition"></a>

`CreativesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesStringFilter`
    :   The type of the None singleton.

<a id="CreativesListParams"></a>

`CreativesListParams(*args, **kwargs)`
:   Parameters for creatives.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

<a id="CreativesLtCondition"></a>

`CreativesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesSearchFilter`
    :   The type of the None singleton.

<a id="CreativesLteCondition"></a>

`CreativesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesSearchFilter`
    :   The type of the None singleton.

<a id="CreativesNeqCondition"></a>

`CreativesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesSearchFilter`
    :   The type of the None singleton.

<a id="CreativesNotCondition"></a>

`CreativesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesAnyCondition`
    :   The type of the None singleton.

<a id="CreativesOrCondition"></a>

`CreativesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesAnyCondition]`
    :   The type of the None singleton.

<a id="CreativesSearchFilter"></a>

`CreativesSearchFilter(*args, **kwargs)`
:   Available fields for filtering creatives search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str | None`
    :   Parent ad account ID

    `ad_product: str | None`
    :   Ad product type

    `ad_to_place_properties: dict[str, typing.Any] | None`
    :   Ad-to-place properties

    `brand_name: str | None`
    :   Brand name displayed in the creative

    `call_to_action: str | None`
    :   Call to action text

    `created_at: str | None`
    :   Creation timestamp

    `forced_view_eligibility: str | None`
    :   Forced view eligibility status

    `headline: str | None`
    :   Creative headline

    `id: str | None`
    :   Unique creative identifier

    `name: str | None`
    :   Creative name

    `packaging_status: str | None`
    :   Packaging status

    `render_type: str | None`
    :   Render type

    `review_status: str | None`
    :   Review status

    `review_status_details: str | None`
    :   Details about the review status

    `shareable: bool | None`
    :   Whether the creative is shareable

    `top_snap_crop_position: str | None`
    :   Top snap crop position

    `top_snap_media_id: str | None`
    :   Top snap media ID

    `type_: str | None`
    :   Creative type

    `updated_at: str | None`
    :   Last update timestamp

    `web_view_properties: dict[str, typing.Any] | None`
    :   Web view properties

<a id="CreativesSearchQuery"></a>

`CreativesSearchQuery(*args, **kwargs)`
:   Search query for creatives entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.CreativesSortFilter]`
    :   The type of the None singleton.

<a id="CreativesSortFilter"></a>

`CreativesSortFilter(*args, **kwargs)`
:   Available fields for sorting creatives search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Literal['asc', 'desc']`
    :   Parent ad account ID

    `ad_product: Literal['asc', 'desc']`
    :   Ad product type

    `ad_to_place_properties: Literal['asc', 'desc']`
    :   Ad-to-place properties

    `brand_name: Literal['asc', 'desc']`
    :   Brand name displayed in the creative

    `call_to_action: Literal['asc', 'desc']`
    :   Call to action text

    `created_at: Literal['asc', 'desc']`
    :   Creation timestamp

    `forced_view_eligibility: Literal['asc', 'desc']`
    :   Forced view eligibility status

    `headline: Literal['asc', 'desc']`
    :   Creative headline

    `id: Literal['asc', 'desc']`
    :   Unique creative identifier

    `name: Literal['asc', 'desc']`
    :   Creative name

    `packaging_status: Literal['asc', 'desc']`
    :   Packaging status

    `render_type: Literal['asc', 'desc']`
    :   Render type

    `review_status: Literal['asc', 'desc']`
    :   Review status

    `review_status_details: Literal['asc', 'desc']`
    :   Details about the review status

    `shareable: Literal['asc', 'desc']`
    :   Whether the creative is shareable

    `top_snap_crop_position: Literal['asc', 'desc']`
    :   Top snap crop position

    `top_snap_media_id: Literal['asc', 'desc']`
    :   Top snap media ID

    `type_: Literal['asc', 'desc']`
    :   Creative type

    `updated_at: Literal['asc', 'desc']`
    :   Last update timestamp

    `web_view_properties: Literal['asc', 'desc']`
    :   Web view properties

<a id="CreativesStringFilter"></a>

`CreativesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   Parent ad account ID

    `ad_product: str`
    :   Ad product type

    `ad_to_place_properties: str`
    :   Ad-to-place properties

    `brand_name: str`
    :   Brand name displayed in the creative

    `call_to_action: str`
    :   Call to action text

    `created_at: str`
    :   Creation timestamp

    `forced_view_eligibility: str`
    :   Forced view eligibility status

    `headline: str`
    :   Creative headline

    `id: str`
    :   Unique creative identifier

    `name: str`
    :   Creative name

    `packaging_status: str`
    :   Packaging status

    `render_type: str`
    :   Render type

    `review_status: str`
    :   Review status

    `review_status_details: str`
    :   Details about the review status

    `shareable: str`
    :   Whether the creative is shareable

    `top_snap_crop_position: str`
    :   Top snap crop position

    `top_snap_media_id: str`
    :   Top snap media ID

    `type_: str`
    :   Creative type

    `updated_at: str`
    :   Last update timestamp

    `web_view_properties: str`
    :   Web view properties

<a id="MediaAndCondition"></a>

`MediaAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaAnyCondition]`
    :   The type of the None singleton.

<a id="MediaAnyCondition"></a>

`MediaAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaAnyValueFilter`
    :   The type of the None singleton.

<a id="MediaAnyValueFilter"></a>

`MediaAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Any`
    :   Parent ad account ID

    `created_at: Any`
    :   Creation timestamp

    `download_link: Any`
    :   Download URL for the media

    `duration_in_seconds: Any`
    :   Duration in seconds for video media

    `file_name: Any`
    :   Original file name

    `file_size_in_bytes: Any`
    :   File size in bytes

    `hash: Any`
    :   Media file hash

    `id: Any`
    :   Unique media identifier

    `image_metadata: Any`
    :   Image-specific metadata

    `is_demo_media: Any`
    :   Whether this is demo media

    `media_status: Any`
    :   Media processing status

    `media_usages: Any`
    :   Where the media is used

    `name: Any`
    :   Media name

    `type_: Any`
    :   Media type

    `updated_at: Any`
    :   Last update timestamp

    `video_metadata: Any`
    :   Video-specific metadata

    `visibility: Any`
    :   Media visibility setting

<a id="MediaContainsCondition"></a>

`MediaContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaAnyValueFilter`
    :   The type of the None singleton.

<a id="MediaEqCondition"></a>

`MediaEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaSearchFilter`
    :   The type of the None singleton.

<a id="MediaFuzzyCondition"></a>

`MediaFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaStringFilter`
    :   The type of the None singleton.

<a id="MediaGetParams"></a>

`MediaGetParams(*args, **kwargs)`
:   Parameters for media.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="MediaGtCondition"></a>

`MediaGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaSearchFilter`
    :   The type of the None singleton.

<a id="MediaGteCondition"></a>

`MediaGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaSearchFilter`
    :   The type of the None singleton.

<a id="MediaInCondition"></a>

`MediaInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaInFilter`
    :   The type of the None singleton.

<a id="MediaInFilter"></a>

`MediaInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: list[str]`
    :   Parent ad account ID

    `created_at: list[str]`
    :   Creation timestamp

    `download_link: list[str]`
    :   Download URL for the media

    `duration_in_seconds: list[float]`
    :   Duration in seconds for video media

    `file_name: list[str]`
    :   Original file name

    `file_size_in_bytes: list[int]`
    :   File size in bytes

    `hash: list[str]`
    :   Media file hash

    `id: list[str]`
    :   Unique media identifier

    `image_metadata: list[dict[str, typing.Any]]`
    :   Image-specific metadata

    `is_demo_media: list[bool]`
    :   Whether this is demo media

    `media_status: list[str]`
    :   Media processing status

    `media_usages: list[list[typing.Any]]`
    :   Where the media is used

    `name: list[str]`
    :   Media name

    `type_: list[str]`
    :   Media type

    `updated_at: list[str]`
    :   Last update timestamp

    `video_metadata: list[dict[str, typing.Any]]`
    :   Video-specific metadata

    `visibility: list[str]`
    :   Media visibility setting

<a id="MediaKeywordCondition"></a>

`MediaKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaStringFilter`
    :   The type of the None singleton.

<a id="MediaLikeCondition"></a>

`MediaLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaStringFilter`
    :   The type of the None singleton.

<a id="MediaListParams"></a>

`MediaListParams(*args, **kwargs)`
:   Parameters for media.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

<a id="MediaLtCondition"></a>

`MediaLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaSearchFilter`
    :   The type of the None singleton.

<a id="MediaLteCondition"></a>

`MediaLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaSearchFilter`
    :   The type of the None singleton.

<a id="MediaNeqCondition"></a>

`MediaNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaSearchFilter`
    :   The type of the None singleton.

<a id="MediaNotCondition"></a>

`MediaNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaAnyCondition`
    :   The type of the None singleton.

<a id="MediaOrCondition"></a>

`MediaOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaAnyCondition]`
    :   The type of the None singleton.

<a id="MediaSearchFilter"></a>

`MediaSearchFilter(*args, **kwargs)`
:   Available fields for filtering media search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str | None`
    :   Parent ad account ID

    `created_at: str | None`
    :   Creation timestamp

    `download_link: str | None`
    :   Download URL for the media

    `duration_in_seconds: float | None`
    :   Duration in seconds for video media

    `file_name: str | None`
    :   Original file name

    `file_size_in_bytes: int | None`
    :   File size in bytes

    `hash: str | None`
    :   Media file hash

    `id: str | None`
    :   Unique media identifier

    `image_metadata: dict[str, typing.Any] | None`
    :   Image-specific metadata

    `is_demo_media: bool | None`
    :   Whether this is demo media

    `media_status: str | None`
    :   Media processing status

    `media_usages: list[typing.Any] | None`
    :   Where the media is used

    `name: str | None`
    :   Media name

    `type_: str | None`
    :   Media type

    `updated_at: str | None`
    :   Last update timestamp

    `video_metadata: dict[str, typing.Any] | None`
    :   Video-specific metadata

    `visibility: str | None`
    :   Media visibility setting

<a id="MediaSearchQuery"></a>

`MediaSearchQuery(*args, **kwargs)`
:   Search query for media entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.MediaSortFilter]`
    :   The type of the None singleton.

<a id="MediaSortFilter"></a>

`MediaSortFilter(*args, **kwargs)`
:   Available fields for sorting media search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Literal['asc', 'desc']`
    :   Parent ad account ID

    `created_at: Literal['asc', 'desc']`
    :   Creation timestamp

    `download_link: Literal['asc', 'desc']`
    :   Download URL for the media

    `duration_in_seconds: Literal['asc', 'desc']`
    :   Duration in seconds for video media

    `file_name: Literal['asc', 'desc']`
    :   Original file name

    `file_size_in_bytes: Literal['asc', 'desc']`
    :   File size in bytes

    `hash: Literal['asc', 'desc']`
    :   Media file hash

    `id: Literal['asc', 'desc']`
    :   Unique media identifier

    `image_metadata: Literal['asc', 'desc']`
    :   Image-specific metadata

    `is_demo_media: Literal['asc', 'desc']`
    :   Whether this is demo media

    `media_status: Literal['asc', 'desc']`
    :   Media processing status

    `media_usages: Literal['asc', 'desc']`
    :   Where the media is used

    `name: Literal['asc', 'desc']`
    :   Media name

    `type_: Literal['asc', 'desc']`
    :   Media type

    `updated_at: Literal['asc', 'desc']`
    :   Last update timestamp

    `video_metadata: Literal['asc', 'desc']`
    :   Video-specific metadata

    `visibility: Literal['asc', 'desc']`
    :   Media visibility setting

<a id="MediaStringFilter"></a>

`MediaStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   Parent ad account ID

    `created_at: str`
    :   Creation timestamp

    `download_link: str`
    :   Download URL for the media

    `duration_in_seconds: str`
    :   Duration in seconds for video media

    `file_name: str`
    :   Original file name

    `file_size_in_bytes: str`
    :   File size in bytes

    `hash: str`
    :   Media file hash

    `id: str`
    :   Unique media identifier

    `image_metadata: str`
    :   Image-specific metadata

    `is_demo_media: str`
    :   Whether this is demo media

    `media_status: str`
    :   Media processing status

    `media_usages: str`
    :   Where the media is used

    `name: str`
    :   Media name

    `type_: str`
    :   Media type

    `updated_at: str`
    :   Last update timestamp

    `video_metadata: str`
    :   Video-specific metadata

    `visibility: str`
    :   Media visibility setting

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

    `and: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsAnyCondition]`
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

    `any: airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsAnyValueFilter`
    :   The type of the None singleton.

<a id="OrganizationsAnyValueFilter"></a>

`OrganizationsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accepted_term_version: Any`
    :   Version of accepted terms

    `address_line_1: Any`
    :   Street address

    `administrative_district_level_1: Any`
    :   State or province

    `configuration_settings: Any`
    :   Organization configuration settings

    `contact_email: Any`
    :   Contact email address

    `contact_name: Any`
    :   Contact person name

    `contact_phone: Any`
    :   Contact phone number

    `contact_phone_optin: Any`
    :   Whether the contact opted in for phone communications

    `country: Any`
    :   Country code

    `created_at: Any`
    :   Creation timestamp

    `created_by_caller: Any`
    :   Whether the organization was created by the caller

    `id: Any`
    :   Unique organization identifier

    `locality: Any`
    :   City or locality

    `my_display_name: Any`
    :   Display name of the authenticated user in the organization

    `my_invited_email: Any`
    :   Email used to invite the authenticated user

    `my_member_id: Any`
    :   Member ID of the authenticated user

    `name: Any`
    :   Organization name

    `postal_code: Any`
    :   Postal code

    `roles: Any`
    :   Roles of the authenticated user in this organization

    `state: Any`
    :   Organization state

    `type_: Any`
    :   Organization type

    `updated_at: Any`
    :   Last update timestamp

<a id="OrganizationsContainsCondition"></a>

`OrganizationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsAnyValueFilter`
    :   The type of the None singleton.

<a id="OrganizationsEqCondition"></a>

`OrganizationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationsFuzzyCondition"></a>

`OrganizationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsStringFilter`
    :   The type of the None singleton.

<a id="OrganizationsGetParams"></a>

`OrganizationsGetParams(*args, **kwargs)`
:   Parameters for organizations.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="OrganizationsGtCondition"></a>

`OrganizationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationsGteCondition"></a>

`OrganizationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsSearchFilter`
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

    `in: airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsInFilter`
    :   The type of the None singleton.

<a id="OrganizationsInFilter"></a>

`OrganizationsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accepted_term_version: list[str]`
    :   Version of accepted terms

    `address_line_1: list[str]`
    :   Street address

    `administrative_district_level_1: list[str]`
    :   State or province

    `configuration_settings: list[dict[str, typing.Any]]`
    :   Organization configuration settings

    `contact_email: list[str]`
    :   Contact email address

    `contact_name: list[str]`
    :   Contact person name

    `contact_phone: list[str]`
    :   Contact phone number

    `contact_phone_optin: list[bool]`
    :   Whether the contact opted in for phone communications

    `country: list[str]`
    :   Country code

    `created_at: list[str]`
    :   Creation timestamp

    `created_by_caller: list[bool]`
    :   Whether the organization was created by the caller

    `id: list[str]`
    :   Unique organization identifier

    `locality: list[str]`
    :   City or locality

    `my_display_name: list[str]`
    :   Display name of the authenticated user in the organization

    `my_invited_email: list[str]`
    :   Email used to invite the authenticated user

    `my_member_id: list[str]`
    :   Member ID of the authenticated user

    `name: list[str]`
    :   Organization name

    `postal_code: list[str]`
    :   Postal code

    `roles: list[list[typing.Any]]`
    :   Roles of the authenticated user in this organization

    `state: list[str]`
    :   Organization state

    `type_: list[str]`
    :   Organization type

    `updated_at: list[str]`
    :   Last update timestamp

<a id="OrganizationsKeywordCondition"></a>

`OrganizationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsStringFilter`
    :   The type of the None singleton.

<a id="OrganizationsLikeCondition"></a>

`OrganizationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsStringFilter`
    :   The type of the None singleton.

<a id="OrganizationsListParams"></a>

`OrganizationsListParams(*args, **kwargs)`
:   Parameters for organizations.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="OrganizationsLtCondition"></a>

`OrganizationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationsLteCondition"></a>

`OrganizationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsSearchFilter`
    :   The type of the None singleton.

<a id="OrganizationsNeqCondition"></a>

`OrganizationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsSearchFilter`
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

    `not: airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsAnyCondition`
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

    `or: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsAnyCondition]`
    :   The type of the None singleton.

<a id="OrganizationsSearchFilter"></a>

`OrganizationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering organizations search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accepted_term_version: str | None`
    :   Version of accepted terms

    `address_line_1: str | None`
    :   Street address

    `administrative_district_level_1: str | None`
    :   State or province

    `configuration_settings: dict[str, typing.Any] | None`
    :   Organization configuration settings

    `contact_email: str | None`
    :   Contact email address

    `contact_name: str | None`
    :   Contact person name

    `contact_phone: str | None`
    :   Contact phone number

    `contact_phone_optin: bool | None`
    :   Whether the contact opted in for phone communications

    `country: str | None`
    :   Country code

    `created_at: str | None`
    :   Creation timestamp

    `created_by_caller: bool | None`
    :   Whether the organization was created by the caller

    `id: str | None`
    :   Unique organization identifier

    `locality: str | None`
    :   City or locality

    `my_display_name: str | None`
    :   Display name of the authenticated user in the organization

    `my_invited_email: str | None`
    :   Email used to invite the authenticated user

    `my_member_id: str | None`
    :   Member ID of the authenticated user

    `name: str | None`
    :   Organization name

    `postal_code: str | None`
    :   Postal code

    `roles: list[typing.Any] | None`
    :   Roles of the authenticated user in this organization

    `state: str | None`
    :   Organization state

    `type_: str | None`
    :   Organization type

    `updated_at: str | None`
    :   Last update timestamp

<a id="OrganizationsSearchQuery"></a>

`OrganizationsSearchQuery(*args, **kwargs)`
:   Search query for organizations entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.OrganizationsSortFilter]`
    :   The type of the None singleton.

<a id="OrganizationsSortFilter"></a>

`OrganizationsSortFilter(*args, **kwargs)`
:   Available fields for sorting organizations search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accepted_term_version: Literal['asc', 'desc']`
    :   Version of accepted terms

    `address_line_1: Literal['asc', 'desc']`
    :   Street address

    `administrative_district_level_1: Literal['asc', 'desc']`
    :   State or province

    `configuration_settings: Literal['asc', 'desc']`
    :   Organization configuration settings

    `contact_email: Literal['asc', 'desc']`
    :   Contact email address

    `contact_name: Literal['asc', 'desc']`
    :   Contact person name

    `contact_phone: Literal['asc', 'desc']`
    :   Contact phone number

    `contact_phone_optin: Literal['asc', 'desc']`
    :   Whether the contact opted in for phone communications

    `country: Literal['asc', 'desc']`
    :   Country code

    `created_at: Literal['asc', 'desc']`
    :   Creation timestamp

    `created_by_caller: Literal['asc', 'desc']`
    :   Whether the organization was created by the caller

    `id: Literal['asc', 'desc']`
    :   Unique organization identifier

    `locality: Literal['asc', 'desc']`
    :   City or locality

    `my_display_name: Literal['asc', 'desc']`
    :   Display name of the authenticated user in the organization

    `my_invited_email: Literal['asc', 'desc']`
    :   Email used to invite the authenticated user

    `my_member_id: Literal['asc', 'desc']`
    :   Member ID of the authenticated user

    `name: Literal['asc', 'desc']`
    :   Organization name

    `postal_code: Literal['asc', 'desc']`
    :   Postal code

    `roles: Literal['asc', 'desc']`
    :   Roles of the authenticated user in this organization

    `state: Literal['asc', 'desc']`
    :   Organization state

    `type_: Literal['asc', 'desc']`
    :   Organization type

    `updated_at: Literal['asc', 'desc']`
    :   Last update timestamp

<a id="OrganizationsStringFilter"></a>

`OrganizationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `accepted_term_version: str`
    :   Version of accepted terms

    `address_line_1: str`
    :   Street address

    `administrative_district_level_1: str`
    :   State or province

    `configuration_settings: str`
    :   Organization configuration settings

    `contact_email: str`
    :   Contact email address

    `contact_name: str`
    :   Contact person name

    `contact_phone: str`
    :   Contact phone number

    `contact_phone_optin: str`
    :   Whether the contact opted in for phone communications

    `country: str`
    :   Country code

    `created_at: str`
    :   Creation timestamp

    `created_by_caller: str`
    :   Whether the organization was created by the caller

    `id: str`
    :   Unique organization identifier

    `locality: str`
    :   City or locality

    `my_display_name: str`
    :   Display name of the authenticated user in the organization

    `my_invited_email: str`
    :   Email used to invite the authenticated user

    `my_member_id: str`
    :   Member ID of the authenticated user

    `name: str`
    :   Organization name

    `postal_code: str`
    :   Postal code

    `roles: str`
    :   Roles of the authenticated user in this organization

    `state: str`
    :   Organization state

    `type_: str`
    :   Organization type

    `updated_at: str`
    :   Last update timestamp

<a id="SegmentsAndCondition"></a>

`SegmentsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsAnyCondition]`
    :   The type of the None singleton.

<a id="SegmentsAnyCondition"></a>

`SegmentsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsAnyValueFilter`
    :   The type of the None singleton.

<a id="SegmentsAnyValueFilter"></a>

`SegmentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Any`
    :   Parent ad account ID

    `approximate_number_users: Any`
    :   Approximate number of users in the segment

    `created_at: Any`
    :   Creation timestamp

    `description: Any`
    :   Segment description

    `id: Any`
    :   Unique segment identifier

    `name: Any`
    :   Segment name

    `organization_id: Any`
    :   Parent organization ID

    `retention_in_days: Any`
    :   Data retention period in days

    `source_type: Any`
    :   Segment source type

    `status: Any`
    :   Segment status

    `targetable_status: Any`
    :   Whether the segment is targetable

    `updated_at: Any`
    :   Last update timestamp

    `upload_status: Any`
    :   Upload processing status

    `visible_to: Any`
    :   Visibility settings

<a id="SegmentsContainsCondition"></a>

`SegmentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsAnyValueFilter`
    :   The type of the None singleton.

<a id="SegmentsEqCondition"></a>

`SegmentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsSearchFilter`
    :   The type of the None singleton.

<a id="SegmentsFuzzyCondition"></a>

`SegmentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsStringFilter`
    :   The type of the None singleton.

<a id="SegmentsGetParams"></a>

`SegmentsGetParams(*args, **kwargs)`
:   Parameters for segments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="SegmentsGtCondition"></a>

`SegmentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsSearchFilter`
    :   The type of the None singleton.

<a id="SegmentsGteCondition"></a>

`SegmentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsSearchFilter`
    :   The type of the None singleton.

<a id="SegmentsInCondition"></a>

`SegmentsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsInFilter`
    :   The type of the None singleton.

<a id="SegmentsInFilter"></a>

`SegmentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: list[str]`
    :   Parent ad account ID

    `approximate_number_users: list[int]`
    :   Approximate number of users in the segment

    `created_at: list[str]`
    :   Creation timestamp

    `description: list[str]`
    :   Segment description

    `id: list[str]`
    :   Unique segment identifier

    `name: list[str]`
    :   Segment name

    `organization_id: list[str]`
    :   Parent organization ID

    `retention_in_days: list[int]`
    :   Data retention period in days

    `source_type: list[str]`
    :   Segment source type

    `status: list[str]`
    :   Segment status

    `targetable_status: list[str]`
    :   Whether the segment is targetable

    `updated_at: list[str]`
    :   Last update timestamp

    `upload_status: list[str]`
    :   Upload processing status

    `visible_to: list[list[typing.Any]]`
    :   Visibility settings

<a id="SegmentsKeywordCondition"></a>

`SegmentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsStringFilter`
    :   The type of the None singleton.

<a id="SegmentsLikeCondition"></a>

`SegmentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsStringFilter`
    :   The type of the None singleton.

<a id="SegmentsListParams"></a>

`SegmentsListParams(*args, **kwargs)`
:   Parameters for segments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   The type of the None singleton.

<a id="SegmentsLtCondition"></a>

`SegmentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsSearchFilter`
    :   The type of the None singleton.

<a id="SegmentsLteCondition"></a>

`SegmentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsSearchFilter`
    :   The type of the None singleton.

<a id="SegmentsNeqCondition"></a>

`SegmentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsSearchFilter`
    :   The type of the None singleton.

<a id="SegmentsNotCondition"></a>

`SegmentsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsAnyCondition`
    :   The type of the None singleton.

<a id="SegmentsOrCondition"></a>

`SegmentsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsAnyCondition]`
    :   The type of the None singleton.

<a id="SegmentsSearchFilter"></a>

`SegmentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering segments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str | None`
    :   Parent ad account ID

    `approximate_number_users: int | None`
    :   Approximate number of users in the segment

    `created_at: str | None`
    :   Creation timestamp

    `description: str | None`
    :   Segment description

    `id: str | None`
    :   Unique segment identifier

    `name: str | None`
    :   Segment name

    `organization_id: str | None`
    :   Parent organization ID

    `retention_in_days: int | None`
    :   Data retention period in days

    `source_type: str | None`
    :   Segment source type

    `status: str | None`
    :   Segment status

    `targetable_status: str | None`
    :   Whether the segment is targetable

    `updated_at: str | None`
    :   Last update timestamp

    `upload_status: str | None`
    :   Upload processing status

    `visible_to: list[typing.Any] | None`
    :   Visibility settings

<a id="SegmentsSearchQuery"></a>

`SegmentsSearchQuery(*args, **kwargs)`
:   Search query for segments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsEqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsNeqCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsGtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsGteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsLtCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsLteCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsInCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsLikeCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsFuzzyCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsKeywordCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsContainsCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsNotCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsAndCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsOrCondition | airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.snapchat_marketing.types.SegmentsSortFilter]`
    :   The type of the None singleton.

<a id="SegmentsSortFilter"></a>

`SegmentsSortFilter(*args, **kwargs)`
:   Available fields for sorting segments search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: Literal['asc', 'desc']`
    :   Parent ad account ID

    `approximate_number_users: Literal['asc', 'desc']`
    :   Approximate number of users in the segment

    `created_at: Literal['asc', 'desc']`
    :   Creation timestamp

    `description: Literal['asc', 'desc']`
    :   Segment description

    `id: Literal['asc', 'desc']`
    :   Unique segment identifier

    `name: Literal['asc', 'desc']`
    :   Segment name

    `organization_id: Literal['asc', 'desc']`
    :   Parent organization ID

    `retention_in_days: Literal['asc', 'desc']`
    :   Data retention period in days

    `source_type: Literal['asc', 'desc']`
    :   Segment source type

    `status: Literal['asc', 'desc']`
    :   Segment status

    `targetable_status: Literal['asc', 'desc']`
    :   Whether the segment is targetable

    `updated_at: Literal['asc', 'desc']`
    :   Last update timestamp

    `upload_status: Literal['asc', 'desc']`
    :   Upload processing status

    `visible_to: Literal['asc', 'desc']`
    :   Visibility settings

<a id="SegmentsStringFilter"></a>

`SegmentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ad_account_id: str`
    :   Parent ad account ID

    `approximate_number_users: str`
    :   Approximate number of users in the segment

    `created_at: str`
    :   Creation timestamp

    `description: str`
    :   Segment description

    `id: str`
    :   Unique segment identifier

    `name: str`
    :   Segment name

    `organization_id: str`
    :   Parent organization ID

    `retention_in_days: str`
    :   Data retention period in days

    `source_type: str`
    :   Segment source type

    `status: str`
    :   Segment status

    `targetable_status: str`
    :   Whether the segment is targetable

    `updated_at: str`
    :   Last update timestamp

    `upload_status: str`
    :   Upload processing status

    `visible_to: str`
    :   Visibility settings