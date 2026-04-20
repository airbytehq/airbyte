---
id: airbyte_agent_sdk-connectors-orb-types
title: airbyte_agent_sdk.connectors.orb.types
---

Module airbyte_agent_sdk.connectors.orb.types
=============================================
Type definitions for orb connector.

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

`CustomersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.orb.types.CustomersEqCondition | airbyte_agent_sdk.connectors.orb.types.CustomersNeqCondition | airbyte_agent_sdk.connectors.orb.types.CustomersGtCondition | airbyte_agent_sdk.connectors.orb.types.CustomersGteCondition | airbyte_agent_sdk.connectors.orb.types.CustomersLtCondition | airbyte_agent_sdk.connectors.orb.types.CustomersLteCondition | airbyte_agent_sdk.connectors.orb.types.CustomersInCondition | airbyte_agent_sdk.connectors.orb.types.CustomersLikeCondition | airbyte_agent_sdk.connectors.orb.types.CustomersFuzzyCondition | airbyte_agent_sdk.connectors.orb.types.CustomersKeywordCondition | airbyte_agent_sdk.connectors.orb.types.CustomersContainsCondition | airbyte_agent_sdk.connectors.orb.types.CustomersNotCondition | airbyte_agent_sdk.connectors.orb.types.CustomersAndCondition | airbyte_agent_sdk.connectors.orb.types.CustomersOrCondition | airbyte_agent_sdk.connectors.orb.types.CustomersAnyCondition]`
    :   The type of the None singleton.

`CustomersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.orb.types.CustomersAnyValueFilter`
    :   The type of the None singleton.

`CustomersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billing_address: Any`
    :   The billing address of the customer

    `created_at: Any`
    :   The date and time when the customer was created

    `email: Any`
    :   The email address of the customer

    `external_customer_id: Any`
    :   The ID of the customer in an external system

    `id: Any`
    :   The unique identifier of the customer

    `name: Any`
    :   The name of the customer

    `payment_provider: Any`
    :   The payment provider used by the customer

    `payment_provider_id: Any`
    :   The ID of the customer in the payment provider's system

    `shipping_address: Any`
    :   The shipping address of the customer

    `timezone: Any`
    :   The timezone setting of the customer

`CustomersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.orb.types.CustomersAnyValueFilter`
    :   The type of the None singleton.

`CustomersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.orb.types.CustomersSearchFilter`
    :   The type of the None singleton.

`CustomersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.orb.types.CustomersStringFilter`
    :   The type of the None singleton.

`CustomersGetParams(*args, **kwargs)`
:   Parameters for customers.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `customer_id: str`
    :   The type of the None singleton.

`CustomersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.orb.types.CustomersSearchFilter`
    :   The type of the None singleton.

`CustomersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.orb.types.CustomersSearchFilter`
    :   The type of the None singleton.

`CustomersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.orb.types.CustomersInFilter`
    :   The type of the None singleton.

`CustomersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billing_address: list[dict[str, typing.Any]]`
    :   The billing address of the customer

    `created_at: list[str]`
    :   The date and time when the customer was created

    `email: list[str]`
    :   The email address of the customer

    `external_customer_id: list[str]`
    :   The ID of the customer in an external system

    `id: list[str]`
    :   The unique identifier of the customer

    `name: list[str]`
    :   The name of the customer

    `payment_provider: list[str]`
    :   The payment provider used by the customer

    `payment_provider_id: list[str]`
    :   The ID of the customer in the payment provider's system

    `shipping_address: list[dict[str, typing.Any]]`
    :   The shipping address of the customer

    `timezone: list[str]`
    :   The timezone setting of the customer

`CustomersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.orb.types.CustomersStringFilter`
    :   The type of the None singleton.

`CustomersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.orb.types.CustomersStringFilter`
    :   The type of the None singleton.

`CustomersListParams(*args, **kwargs)`
:   Parameters for customers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`CustomersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.orb.types.CustomersSearchFilter`
    :   The type of the None singleton.

`CustomersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.orb.types.CustomersSearchFilter`
    :   The type of the None singleton.

`CustomersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.orb.types.CustomersSearchFilter`
    :   The type of the None singleton.

`CustomersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.orb.types.CustomersEqCondition | airbyte_agent_sdk.connectors.orb.types.CustomersNeqCondition | airbyte_agent_sdk.connectors.orb.types.CustomersGtCondition | airbyte_agent_sdk.connectors.orb.types.CustomersGteCondition | airbyte_agent_sdk.connectors.orb.types.CustomersLtCondition | airbyte_agent_sdk.connectors.orb.types.CustomersLteCondition | airbyte_agent_sdk.connectors.orb.types.CustomersInCondition | airbyte_agent_sdk.connectors.orb.types.CustomersLikeCondition | airbyte_agent_sdk.connectors.orb.types.CustomersFuzzyCondition | airbyte_agent_sdk.connectors.orb.types.CustomersKeywordCondition | airbyte_agent_sdk.connectors.orb.types.CustomersContainsCondition | airbyte_agent_sdk.connectors.orb.types.CustomersNotCondition | airbyte_agent_sdk.connectors.orb.types.CustomersAndCondition | airbyte_agent_sdk.connectors.orb.types.CustomersOrCondition | airbyte_agent_sdk.connectors.orb.types.CustomersAnyCondition`
    :   The type of the None singleton.

`CustomersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.orb.types.CustomersEqCondition | airbyte_agent_sdk.connectors.orb.types.CustomersNeqCondition | airbyte_agent_sdk.connectors.orb.types.CustomersGtCondition | airbyte_agent_sdk.connectors.orb.types.CustomersGteCondition | airbyte_agent_sdk.connectors.orb.types.CustomersLtCondition | airbyte_agent_sdk.connectors.orb.types.CustomersLteCondition | airbyte_agent_sdk.connectors.orb.types.CustomersInCondition | airbyte_agent_sdk.connectors.orb.types.CustomersLikeCondition | airbyte_agent_sdk.connectors.orb.types.CustomersFuzzyCondition | airbyte_agent_sdk.connectors.orb.types.CustomersKeywordCondition | airbyte_agent_sdk.connectors.orb.types.CustomersContainsCondition | airbyte_agent_sdk.connectors.orb.types.CustomersNotCondition | airbyte_agent_sdk.connectors.orb.types.CustomersAndCondition | airbyte_agent_sdk.connectors.orb.types.CustomersOrCondition | airbyte_agent_sdk.connectors.orb.types.CustomersAnyCondition]`
    :   The type of the None singleton.

`CustomersSearchFilter(*args, **kwargs)`
:   Available fields for filtering customers search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billing_address: dict[str, typing.Any] | None`
    :   The billing address of the customer

    `created_at: str | None`
    :   The date and time when the customer was created

    `email: str | None`
    :   The email address of the customer

    `external_customer_id: str | None`
    :   The ID of the customer in an external system

    `id: str`
    :   The unique identifier of the customer

    `name: str | None`
    :   The name of the customer

    `payment_provider: str | None`
    :   The payment provider used by the customer

    `payment_provider_id: str | None`
    :   The ID of the customer in the payment provider's system

    `shipping_address: dict[str, typing.Any] | None`
    :   The shipping address of the customer

    `timezone: str | None`
    :   The timezone setting of the customer

`CustomersSearchQuery(*args, **kwargs)`
:   Search query for customers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.orb.types.CustomersEqCondition | airbyte_agent_sdk.connectors.orb.types.CustomersNeqCondition | airbyte_agent_sdk.connectors.orb.types.CustomersGtCondition | airbyte_agent_sdk.connectors.orb.types.CustomersGteCondition | airbyte_agent_sdk.connectors.orb.types.CustomersLtCondition | airbyte_agent_sdk.connectors.orb.types.CustomersLteCondition | airbyte_agent_sdk.connectors.orb.types.CustomersInCondition | airbyte_agent_sdk.connectors.orb.types.CustomersLikeCondition | airbyte_agent_sdk.connectors.orb.types.CustomersFuzzyCondition | airbyte_agent_sdk.connectors.orb.types.CustomersKeywordCondition | airbyte_agent_sdk.connectors.orb.types.CustomersContainsCondition | airbyte_agent_sdk.connectors.orb.types.CustomersNotCondition | airbyte_agent_sdk.connectors.orb.types.CustomersAndCondition | airbyte_agent_sdk.connectors.orb.types.CustomersOrCondition | airbyte_agent_sdk.connectors.orb.types.CustomersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.orb.types.CustomersSortFilter]`
    :   The type of the None singleton.

`CustomersSortFilter(*args, **kwargs)`
:   Available fields for sorting customers search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billing_address: Literal['asc', 'desc']`
    :   The billing address of the customer

    `created_at: Literal['asc', 'desc']`
    :   The date and time when the customer was created

    `email: Literal['asc', 'desc']`
    :   The email address of the customer

    `external_customer_id: Literal['asc', 'desc']`
    :   The ID of the customer in an external system

    `id: Literal['asc', 'desc']`
    :   The unique identifier of the customer

    `name: Literal['asc', 'desc']`
    :   The name of the customer

    `payment_provider: Literal['asc', 'desc']`
    :   The payment provider used by the customer

    `payment_provider_id: Literal['asc', 'desc']`
    :   The ID of the customer in the payment provider's system

    `shipping_address: Literal['asc', 'desc']`
    :   The shipping address of the customer

    `timezone: Literal['asc', 'desc']`
    :   The timezone setting of the customer

`CustomersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `billing_address: str`
    :   The billing address of the customer

    `created_at: str`
    :   The date and time when the customer was created

    `email: str`
    :   The email address of the customer

    `external_customer_id: str`
    :   The ID of the customer in an external system

    `id: str`
    :   The unique identifier of the customer

    `name: str`
    :   The name of the customer

    `payment_provider: str`
    :   The payment provider used by the customer

    `payment_provider_id: str`
    :   The ID of the customer in the payment provider's system

    `shipping_address: str`
    :   The shipping address of the customer

    `timezone: str`
    :   The timezone setting of the customer

`InvoicesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.orb.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesInCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesLikeCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesAnyCondition]`
    :   The type of the None singleton.

`InvoicesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.orb.types.InvoicesAnyValueFilter`
    :   The type of the None singleton.

`InvoicesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount_due: Any`
    :   The amount due on the invoice

    `created_at: Any`
    :   The date and time when the invoice was created

    `due_date: Any`
    :   The due date for the invoice

    `hosted_invoice_url: Any`
    :   The URL to view the hosted invoice

    `id: Any`
    :   The unique identifier of the invoice

    `invoice_date: Any`
    :   The date of the invoice

    `invoice_pdf: Any`
    :   The URL to download the PDF version of the invoice

    `issued_at: Any`
    :   The date and time when the invoice was issued

    `line_items: Any`
    :   The line items on the invoice

    `memo: Any`
    :   Any additional notes or comments on the invoice

    `paid_at: Any`
    :   The date and time when the invoice was paid

    `status: Any`
    :   The current status of the invoice

    `subscription: Any`
    :   The subscription associated with the invoice

    `subtotal: Any`
    :   The subtotal amount of the invoice

    `total: Any`
    :   The total amount of the invoice

`InvoicesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.orb.types.InvoicesAnyValueFilter`
    :   The type of the None singleton.

`InvoicesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.orb.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.orb.types.InvoicesStringFilter`
    :   The type of the None singleton.

`InvoicesGetParams(*args, **kwargs)`
:   Parameters for invoices.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `invoice_id: str`
    :   The type of the None singleton.

`InvoicesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.orb.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.orb.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.orb.types.InvoicesInFilter`
    :   The type of the None singleton.

`InvoicesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount_due: list[str]`
    :   The amount due on the invoice

    `created_at: list[str]`
    :   The date and time when the invoice was created

    `due_date: list[str]`
    :   The due date for the invoice

    `hosted_invoice_url: list[str]`
    :   The URL to view the hosted invoice

    `id: list[str]`
    :   The unique identifier of the invoice

    `invoice_date: list[str]`
    :   The date of the invoice

    `invoice_pdf: list[str]`
    :   The URL to download the PDF version of the invoice

    `issued_at: list[str]`
    :   The date and time when the invoice was issued

    `line_items: list[list[typing.Any]]`
    :   The line items on the invoice

    `memo: list[str]`
    :   Any additional notes or comments on the invoice

    `paid_at: list[str]`
    :   The date and time when the invoice was paid

    `status: list[str]`
    :   The current status of the invoice

    `subscription: list[dict[str, typing.Any]]`
    :   The subscription associated with the invoice

    `subtotal: list[str]`
    :   The subtotal amount of the invoice

    `total: list[str]`
    :   The total amount of the invoice

`InvoicesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.orb.types.InvoicesStringFilter`
    :   The type of the None singleton.

`InvoicesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.orb.types.InvoicesStringFilter`
    :   The type of the None singleton.

`InvoicesListParams(*args, **kwargs)`
:   Parameters for invoices.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `customer_id: str`
    :   The type of the None singleton.

    `external_customer_id: str`
    :   The type of the None singleton.

    `invoice_date_gt: str`
    :   The type of the None singleton.

    `invoice_date_gte: str`
    :   The type of the None singleton.

    `invoice_date_lt: str`
    :   The type of the None singleton.

    `invoice_date_lte: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `subscription_id: str`
    :   The type of the None singleton.

`InvoicesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.orb.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.orb.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.orb.types.InvoicesSearchFilter`
    :   The type of the None singleton.

`InvoicesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.orb.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesInCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesLikeCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesAnyCondition`
    :   The type of the None singleton.

`InvoicesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.orb.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesInCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesLikeCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesAnyCondition]`
    :   The type of the None singleton.

`InvoicesSearchFilter(*args, **kwargs)`
:   Available fields for filtering invoices search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount_due: str | None`
    :   The amount due on the invoice

    `created_at: str | None`
    :   The date and time when the invoice was created

    `due_date: str | None`
    :   The due date for the invoice

    `hosted_invoice_url: str | None`
    :   The URL to view the hosted invoice

    `id: str`
    :   The unique identifier of the invoice

    `invoice_date: str | None`
    :   The date of the invoice

    `invoice_pdf: str | None`
    :   The URL to download the PDF version of the invoice

    `issued_at: str | None`
    :   The date and time when the invoice was issued

    `line_items: list[typing.Any] | None`
    :   The line items on the invoice

    `memo: str | None`
    :   Any additional notes or comments on the invoice

    `paid_at: str | None`
    :   The date and time when the invoice was paid

    `status: str | None`
    :   The current status of the invoice

    `subscription: dict[str, typing.Any] | None`
    :   The subscription associated with the invoice

    `subtotal: str | None`
    :   The subtotal amount of the invoice

    `total: str | None`
    :   The total amount of the invoice

`InvoicesSearchQuery(*args, **kwargs)`
:   Search query for invoices entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.orb.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesInCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesLikeCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.orb.types.InvoicesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.orb.types.InvoicesSortFilter]`
    :   The type of the None singleton.

`InvoicesSortFilter(*args, **kwargs)`
:   Available fields for sorting invoices search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount_due: Literal['asc', 'desc']`
    :   The amount due on the invoice

    `created_at: Literal['asc', 'desc']`
    :   The date and time when the invoice was created

    `due_date: Literal['asc', 'desc']`
    :   The due date for the invoice

    `hosted_invoice_url: Literal['asc', 'desc']`
    :   The URL to view the hosted invoice

    `id: Literal['asc', 'desc']`
    :   The unique identifier of the invoice

    `invoice_date: Literal['asc', 'desc']`
    :   The date of the invoice

    `invoice_pdf: Literal['asc', 'desc']`
    :   The URL to download the PDF version of the invoice

    `issued_at: Literal['asc', 'desc']`
    :   The date and time when the invoice was issued

    `line_items: Literal['asc', 'desc']`
    :   The line items on the invoice

    `memo: Literal['asc', 'desc']`
    :   Any additional notes or comments on the invoice

    `paid_at: Literal['asc', 'desc']`
    :   The date and time when the invoice was paid

    `status: Literal['asc', 'desc']`
    :   The current status of the invoice

    `subscription: Literal['asc', 'desc']`
    :   The subscription associated with the invoice

    `subtotal: Literal['asc', 'desc']`
    :   The subtotal amount of the invoice

    `total: Literal['asc', 'desc']`
    :   The total amount of the invoice

`InvoicesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount_due: str`
    :   The amount due on the invoice

    `created_at: str`
    :   The date and time when the invoice was created

    `due_date: str`
    :   The due date for the invoice

    `hosted_invoice_url: str`
    :   The URL to view the hosted invoice

    `id: str`
    :   The unique identifier of the invoice

    `invoice_date: str`
    :   The date of the invoice

    `invoice_pdf: str`
    :   The URL to download the PDF version of the invoice

    `issued_at: str`
    :   The date and time when the invoice was issued

    `line_items: str`
    :   The line items on the invoice

    `memo: str`
    :   Any additional notes or comments on the invoice

    `paid_at: str`
    :   The date and time when the invoice was paid

    `status: str`
    :   The current status of the invoice

    `subscription: str`
    :   The subscription associated with the invoice

    `subtotal: str`
    :   The subtotal amount of the invoice

    `total: str`
    :   The total amount of the invoice

`PlansAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.orb.types.PlansEqCondition | airbyte_agent_sdk.connectors.orb.types.PlansNeqCondition | airbyte_agent_sdk.connectors.orb.types.PlansGtCondition | airbyte_agent_sdk.connectors.orb.types.PlansGteCondition | airbyte_agent_sdk.connectors.orb.types.PlansLtCondition | airbyte_agent_sdk.connectors.orb.types.PlansLteCondition | airbyte_agent_sdk.connectors.orb.types.PlansInCondition | airbyte_agent_sdk.connectors.orb.types.PlansLikeCondition | airbyte_agent_sdk.connectors.orb.types.PlansFuzzyCondition | airbyte_agent_sdk.connectors.orb.types.PlansKeywordCondition | airbyte_agent_sdk.connectors.orb.types.PlansContainsCondition | airbyte_agent_sdk.connectors.orb.types.PlansNotCondition | airbyte_agent_sdk.connectors.orb.types.PlansAndCondition | airbyte_agent_sdk.connectors.orb.types.PlansOrCondition | airbyte_agent_sdk.connectors.orb.types.PlansAnyCondition]`
    :   The type of the None singleton.

`PlansAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.orb.types.PlansAnyValueFilter`
    :   The type of the None singleton.

`PlansAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   The date and time when the plan was created

    `description: Any`
    :   A description of the plan

    `id: Any`
    :   The unique identifier of the plan

    `name: Any`
    :   The name of the plan

    `prices: Any`
    :   The pricing options for the plan

    `product: Any`
    :   The product associated with the plan

`PlansContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.orb.types.PlansAnyValueFilter`
    :   The type of the None singleton.

`PlansEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.orb.types.PlansSearchFilter`
    :   The type of the None singleton.

`PlansFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.orb.types.PlansStringFilter`
    :   The type of the None singleton.

`PlansGetParams(*args, **kwargs)`
:   Parameters for plans.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `plan_id: str`
    :   The type of the None singleton.

`PlansGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.orb.types.PlansSearchFilter`
    :   The type of the None singleton.

`PlansGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.orb.types.PlansSearchFilter`
    :   The type of the None singleton.

`PlansInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.orb.types.PlansInFilter`
    :   The type of the None singleton.

`PlansInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   The date and time when the plan was created

    `description: list[str]`
    :   A description of the plan

    `id: list[str]`
    :   The unique identifier of the plan

    `name: list[str]`
    :   The name of the plan

    `prices: list[list[typing.Any]]`
    :   The pricing options for the plan

    `product: list[dict[str, typing.Any]]`
    :   The product associated with the plan

`PlansKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.orb.types.PlansStringFilter`
    :   The type of the None singleton.

`PlansLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.orb.types.PlansStringFilter`
    :   The type of the None singleton.

`PlansListParams(*args, **kwargs)`
:   Parameters for plans.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

`PlansLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.orb.types.PlansSearchFilter`
    :   The type of the None singleton.

`PlansLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.orb.types.PlansSearchFilter`
    :   The type of the None singleton.

`PlansNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.orb.types.PlansSearchFilter`
    :   The type of the None singleton.

`PlansNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.orb.types.PlansEqCondition | airbyte_agent_sdk.connectors.orb.types.PlansNeqCondition | airbyte_agent_sdk.connectors.orb.types.PlansGtCondition | airbyte_agent_sdk.connectors.orb.types.PlansGteCondition | airbyte_agent_sdk.connectors.orb.types.PlansLtCondition | airbyte_agent_sdk.connectors.orb.types.PlansLteCondition | airbyte_agent_sdk.connectors.orb.types.PlansInCondition | airbyte_agent_sdk.connectors.orb.types.PlansLikeCondition | airbyte_agent_sdk.connectors.orb.types.PlansFuzzyCondition | airbyte_agent_sdk.connectors.orb.types.PlansKeywordCondition | airbyte_agent_sdk.connectors.orb.types.PlansContainsCondition | airbyte_agent_sdk.connectors.orb.types.PlansNotCondition | airbyte_agent_sdk.connectors.orb.types.PlansAndCondition | airbyte_agent_sdk.connectors.orb.types.PlansOrCondition | airbyte_agent_sdk.connectors.orb.types.PlansAnyCondition`
    :   The type of the None singleton.

`PlansOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.orb.types.PlansEqCondition | airbyte_agent_sdk.connectors.orb.types.PlansNeqCondition | airbyte_agent_sdk.connectors.orb.types.PlansGtCondition | airbyte_agent_sdk.connectors.orb.types.PlansGteCondition | airbyte_agent_sdk.connectors.orb.types.PlansLtCondition | airbyte_agent_sdk.connectors.orb.types.PlansLteCondition | airbyte_agent_sdk.connectors.orb.types.PlansInCondition | airbyte_agent_sdk.connectors.orb.types.PlansLikeCondition | airbyte_agent_sdk.connectors.orb.types.PlansFuzzyCondition | airbyte_agent_sdk.connectors.orb.types.PlansKeywordCondition | airbyte_agent_sdk.connectors.orb.types.PlansContainsCondition | airbyte_agent_sdk.connectors.orb.types.PlansNotCondition | airbyte_agent_sdk.connectors.orb.types.PlansAndCondition | airbyte_agent_sdk.connectors.orb.types.PlansOrCondition | airbyte_agent_sdk.connectors.orb.types.PlansAnyCondition]`
    :   The type of the None singleton.

`PlansSearchFilter(*args, **kwargs)`
:   Available fields for filtering plans search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   The date and time when the plan was created

    `description: str | None`
    :   A description of the plan

    `id: str`
    :   The unique identifier of the plan

    `name: str | None`
    :   The name of the plan

    `prices: list[typing.Any] | None`
    :   The pricing options for the plan

    `product: dict[str, typing.Any] | None`
    :   The product associated with the plan

`PlansSearchQuery(*args, **kwargs)`
:   Search query for plans entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.orb.types.PlansEqCondition | airbyte_agent_sdk.connectors.orb.types.PlansNeqCondition | airbyte_agent_sdk.connectors.orb.types.PlansGtCondition | airbyte_agent_sdk.connectors.orb.types.PlansGteCondition | airbyte_agent_sdk.connectors.orb.types.PlansLtCondition | airbyte_agent_sdk.connectors.orb.types.PlansLteCondition | airbyte_agent_sdk.connectors.orb.types.PlansInCondition | airbyte_agent_sdk.connectors.orb.types.PlansLikeCondition | airbyte_agent_sdk.connectors.orb.types.PlansFuzzyCondition | airbyte_agent_sdk.connectors.orb.types.PlansKeywordCondition | airbyte_agent_sdk.connectors.orb.types.PlansContainsCondition | airbyte_agent_sdk.connectors.orb.types.PlansNotCondition | airbyte_agent_sdk.connectors.orb.types.PlansAndCondition | airbyte_agent_sdk.connectors.orb.types.PlansOrCondition | airbyte_agent_sdk.connectors.orb.types.PlansAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.orb.types.PlansSortFilter]`
    :   The type of the None singleton.

`PlansSortFilter(*args, **kwargs)`
:   Available fields for sorting plans search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   The date and time when the plan was created

    `description: Literal['asc', 'desc']`
    :   A description of the plan

    `id: Literal['asc', 'desc']`
    :   The unique identifier of the plan

    `name: Literal['asc', 'desc']`
    :   The name of the plan

    `prices: Literal['asc', 'desc']`
    :   The pricing options for the plan

    `product: Literal['asc', 'desc']`
    :   The product associated with the plan

`PlansStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   The date and time when the plan was created

    `description: str`
    :   A description of the plan

    `id: str`
    :   The unique identifier of the plan

    `name: str`
    :   The name of the plan

    `prices: str`
    :   The pricing options for the plan

    `product: str`
    :   The product associated with the plan

`SubscriptionsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.orb.types.SubscriptionsEqCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsNeqCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsGtCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsGteCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsLtCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsLteCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsInCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsLikeCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsFuzzyCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsKeywordCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsContainsCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsNotCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsAndCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsOrCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsAnyCondition]`
    :   The type of the None singleton.

`SubscriptionsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.orb.types.SubscriptionsAnyValueFilter`
    :   The type of the None singleton.

`SubscriptionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   The date and time when the subscription was created

    `end_date: Any`
    :   The date and time when the subscription ends

    `id: Any`
    :   The unique identifier of the subscription

    `start_date: Any`
    :   The date and time when the subscription starts

    `status: Any`
    :   The current status of the subscription

`SubscriptionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.orb.types.SubscriptionsAnyValueFilter`
    :   The type of the None singleton.

`SubscriptionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.orb.types.SubscriptionsSearchFilter`
    :   The type of the None singleton.

`SubscriptionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.orb.types.SubscriptionsStringFilter`
    :   The type of the None singleton.

`SubscriptionsGetParams(*args, **kwargs)`
:   Parameters for subscriptions.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `subscription_id: str`
    :   The type of the None singleton.

`SubscriptionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.orb.types.SubscriptionsSearchFilter`
    :   The type of the None singleton.

`SubscriptionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.orb.types.SubscriptionsSearchFilter`
    :   The type of the None singleton.

`SubscriptionsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.orb.types.SubscriptionsInFilter`
    :   The type of the None singleton.

`SubscriptionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   The date and time when the subscription was created

    `end_date: list[str]`
    :   The date and time when the subscription ends

    `id: list[str]`
    :   The unique identifier of the subscription

    `start_date: list[str]`
    :   The date and time when the subscription starts

    `status: list[str]`
    :   The current status of the subscription

`SubscriptionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.orb.types.SubscriptionsStringFilter`
    :   The type of the None singleton.

`SubscriptionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.orb.types.SubscriptionsStringFilter`
    :   The type of the None singleton.

`SubscriptionsListParams(*args, **kwargs)`
:   Parameters for subscriptions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `customer_id: str`
    :   The type of the None singleton.

    `external_customer_id: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

`SubscriptionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.orb.types.SubscriptionsSearchFilter`
    :   The type of the None singleton.

`SubscriptionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.orb.types.SubscriptionsSearchFilter`
    :   The type of the None singleton.

`SubscriptionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.orb.types.SubscriptionsSearchFilter`
    :   The type of the None singleton.

`SubscriptionsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.orb.types.SubscriptionsEqCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsNeqCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsGtCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsGteCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsLtCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsLteCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsInCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsLikeCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsFuzzyCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsKeywordCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsContainsCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsNotCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsAndCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsOrCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsAnyCondition`
    :   The type of the None singleton.

`SubscriptionsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.orb.types.SubscriptionsEqCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsNeqCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsGtCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsGteCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsLtCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsLteCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsInCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsLikeCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsFuzzyCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsKeywordCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsContainsCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsNotCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsAndCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsOrCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsAnyCondition]`
    :   The type of the None singleton.

`SubscriptionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering subscriptions search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   The date and time when the subscription was created

    `end_date: str | None`
    :   The date and time when the subscription ends

    `id: str`
    :   The unique identifier of the subscription

    `start_date: str | None`
    :   The date and time when the subscription starts

    `status: str | None`
    :   The current status of the subscription

`SubscriptionsSearchQuery(*args, **kwargs)`
:   Search query for subscriptions entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.orb.types.SubscriptionsEqCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsNeqCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsGtCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsGteCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsLtCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsLteCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsInCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsLikeCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsFuzzyCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsKeywordCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsContainsCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsNotCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsAndCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsOrCondition | airbyte_agent_sdk.connectors.orb.types.SubscriptionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.orb.types.SubscriptionsSortFilter]`
    :   The type of the None singleton.

`SubscriptionsSortFilter(*args, **kwargs)`
:   Available fields for sorting subscriptions search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   The date and time when the subscription was created

    `end_date: Literal['asc', 'desc']`
    :   The date and time when the subscription ends

    `id: Literal['asc', 'desc']`
    :   The unique identifier of the subscription

    `start_date: Literal['asc', 'desc']`
    :   The date and time when the subscription starts

    `status: Literal['asc', 'desc']`
    :   The current status of the subscription

`SubscriptionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   The date and time when the subscription was created

    `end_date: str`
    :   The date and time when the subscription ends

    `id: str`
    :   The unique identifier of the subscription

    `start_date: str`
    :   The date and time when the subscription starts

    `status: str`
    :   The current status of the subscription