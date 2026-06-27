---
id: airbyte_agent_sdk-connectors-amazon_seller_partner-types
title: airbyte_agent_sdk.connectors.amazon_seller_partner.types
---

Module airbyte_agent_sdk.connectors.amazon_seller_partner.types
===============================================================
Type definitions for amazon-seller-partner connector.

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

<a id="CatalogItemsGetParams"></a>

`CatalogItemsGetParams(*args, **kwargs)`
:   Parameters for catalog_items.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `asin: str`
    :   The type of the None singleton.

    `included_data: str`
    :   The type of the None singleton.

    `marketplace_ids: str`
    :   The type of the None singleton.

<a id="CatalogItemsListParams"></a>

`CatalogItemsListParams(*args, **kwargs)`
:   Parameters for catalog_items.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `identifiers: str`
    :   The type of the None singleton.

    `identifiers_type: str`
    :   The type of the None singleton.

    `included_data: str`
    :   The type of the None singleton.

    `keywords: str`
    :   The type of the None singleton.

    `marketplace_ids: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `page_token: str`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsAndCondition"></a>

`ListFinancialEventGroupsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsEqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsNeqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsGtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsGteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsLtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsLteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsInCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsLikeCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsFuzzyCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsKeywordCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsContainsCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsNotCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsAndCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsOrCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsAnyCondition]`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsAnyCondition"></a>

`ListFinancialEventGroupsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsAnyValueFilter"></a>

`ListFinancialEventGroupsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_tail: Any`
    :   The last digits of the account number

    `beginning_balance: Any`
    :   Beginning balance

    `converted_total: Any`
    :   Converted total

    `financial_event_group_end: Any`
    :   End datetime of the financial event group

    `financial_event_group_id: Any`
    :   Unique identifier for the financial event group

    `financial_event_group_start: Any`
    :   Start datetime of the financial event group

    `fund_transfer_date: Any`
    :   Date the fund transfer occurred

    `fund_transfer_status: Any`
    :   Status of the fund transfer

    `original_total: Any`
    :   Original total amount

    `processing_status: Any`
    :   Processing status of the financial event group

    `trace_id: Any`
    :   Unique identifier for tracing

<a id="ListFinancialEventGroupsContainsCondition"></a>

`ListFinancialEventGroupsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsAnyValueFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsEqCondition"></a>

`ListFinancialEventGroupsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsSearchFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsFuzzyCondition"></a>

`ListFinancialEventGroupsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsStringFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsGtCondition"></a>

`ListFinancialEventGroupsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsSearchFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsGteCondition"></a>

`ListFinancialEventGroupsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsSearchFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsInCondition"></a>

`ListFinancialEventGroupsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsInFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsInFilter"></a>

`ListFinancialEventGroupsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_tail: list[str]`
    :   The last digits of the account number

    `beginning_balance: list[dict[str, typing.Any]]`
    :   Beginning balance

    `converted_total: list[dict[str, typing.Any]]`
    :   Converted total

    `financial_event_group_end: list[str]`
    :   End datetime of the financial event group

    `financial_event_group_id: list[str]`
    :   Unique identifier for the financial event group

    `financial_event_group_start: list[str]`
    :   Start datetime of the financial event group

    `fund_transfer_date: list[str]`
    :   Date the fund transfer occurred

    `fund_transfer_status: list[str]`
    :   Status of the fund transfer

    `original_total: list[dict[str, typing.Any]]`
    :   Original total amount

    `processing_status: list[str]`
    :   Processing status of the financial event group

    `trace_id: list[str]`
    :   Unique identifier for tracing

<a id="ListFinancialEventGroupsKeywordCondition"></a>

`ListFinancialEventGroupsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsStringFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsLikeCondition"></a>

`ListFinancialEventGroupsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsStringFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsListParams"></a>

`ListFinancialEventGroupsListParams(*args, **kwargs)`
:   Parameters for list_financial_event_groups.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `financial_event_group_started_after: str`
    :   The type of the None singleton.

    `financial_event_group_started_before: str`
    :   The type of the None singleton.

    `max_results_per_page: int`
    :   The type of the None singleton.

    `next_token: str`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsLtCondition"></a>

`ListFinancialEventGroupsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsSearchFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsLteCondition"></a>

`ListFinancialEventGroupsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsSearchFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsNeqCondition"></a>

`ListFinancialEventGroupsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsSearchFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsNotCondition"></a>

`ListFinancialEventGroupsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsEqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsNeqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsGtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsGteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsLtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsLteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsInCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsLikeCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsFuzzyCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsKeywordCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsContainsCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsNotCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsAndCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsOrCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsAnyCondition`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsOrCondition"></a>

`ListFinancialEventGroupsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsEqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsNeqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsGtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsGteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsLtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsLteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsInCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsLikeCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsFuzzyCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsKeywordCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsContainsCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsNotCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsAndCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsOrCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsAnyCondition]`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsSearchFilter"></a>

`ListFinancialEventGroupsSearchFilter(*args, **kwargs)`
:   Available fields for filtering list_financial_event_groups search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_tail: str | None`
    :   The last digits of the account number

    `beginning_balance: dict[str, typing.Any] | None`
    :   Beginning balance

    `converted_total: dict[str, typing.Any] | None`
    :   Converted total

    `financial_event_group_end: str | None`
    :   End datetime of the financial event group

    `financial_event_group_id: str | None`
    :   Unique identifier for the financial event group

    `financial_event_group_start: str | None`
    :   Start datetime of the financial event group

    `fund_transfer_date: str | None`
    :   Date the fund transfer occurred

    `fund_transfer_status: str | None`
    :   Status of the fund transfer

    `original_total: dict[str, typing.Any] | None`
    :   Original total amount

    `processing_status: str | None`
    :   Processing status of the financial event group

    `trace_id: str | None`
    :   Unique identifier for tracing

<a id="ListFinancialEventGroupsSearchQuery"></a>

`ListFinancialEventGroupsSearchQuery(*args, **kwargs)`
:   Search query for list_financial_event_groups entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsEqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsNeqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsGtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsGteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsLtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsLteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsInCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsLikeCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsFuzzyCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsKeywordCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsContainsCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsNotCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsAndCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsOrCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventGroupsSortFilter]`
    :   The type of the None singleton.

<a id="ListFinancialEventGroupsSortFilter"></a>

`ListFinancialEventGroupsSortFilter(*args, **kwargs)`
:   Available fields for sorting list_financial_event_groups search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_tail: Literal['asc', 'desc']`
    :   The last digits of the account number

    `beginning_balance: Literal['asc', 'desc']`
    :   Beginning balance

    `converted_total: Literal['asc', 'desc']`
    :   Converted total

    `financial_event_group_end: Literal['asc', 'desc']`
    :   End datetime of the financial event group

    `financial_event_group_id: Literal['asc', 'desc']`
    :   Unique identifier for the financial event group

    `financial_event_group_start: Literal['asc', 'desc']`
    :   Start datetime of the financial event group

    `fund_transfer_date: Literal['asc', 'desc']`
    :   Date the fund transfer occurred

    `fund_transfer_status: Literal['asc', 'desc']`
    :   Status of the fund transfer

    `original_total: Literal['asc', 'desc']`
    :   Original total amount

    `processing_status: Literal['asc', 'desc']`
    :   Processing status of the financial event group

    `trace_id: Literal['asc', 'desc']`
    :   Unique identifier for tracing

<a id="ListFinancialEventGroupsStringFilter"></a>

`ListFinancialEventGroupsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_tail: str`
    :   The last digits of the account number

    `beginning_balance: str`
    :   Beginning balance

    `converted_total: str`
    :   Converted total

    `financial_event_group_end: str`
    :   End datetime of the financial event group

    `financial_event_group_id: str`
    :   Unique identifier for the financial event group

    `financial_event_group_start: str`
    :   Start datetime of the financial event group

    `fund_transfer_date: str`
    :   Date the fund transfer occurred

    `fund_transfer_status: str`
    :   Status of the fund transfer

    `original_total: str`
    :   Original total amount

    `processing_status: str`
    :   Processing status of the financial event group

    `trace_id: str`
    :   Unique identifier for tracing

<a id="ListFinancialEventsAndCondition"></a>

`ListFinancialEventsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsEqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsNeqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsGtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsGteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsLtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsLteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsInCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsLikeCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsFuzzyCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsKeywordCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsContainsCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsNotCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsAndCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsOrCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsAnyCondition]`
    :   The type of the None singleton.

<a id="ListFinancialEventsAnyCondition"></a>

`ListFinancialEventsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsAnyValueFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventsAnyValueFilter"></a>

`ListFinancialEventsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adhoc_disbursement_event_list: Any`
    :   List of adhoc disbursement events

    `adjustment_event_list: Any`
    :   List of adjustment events

    `affordability_expense_event_list: Any`
    :   List of affordability expense events

    `affordability_expense_reversal_event_list: Any`
    :   List of affordability expense reversal events

    `capacity_reservation_billing_event_list: Any`
    :   List of capacity reservation billing events

    `charge_refund_event_list: Any`
    :   List of charge refund events

    `chargeback_event_list: Any`
    :   List of chargeback events

    `coupon_payment_event_list: Any`
    :   List of coupon payment events

    `debt_recovery_event_list: Any`
    :   List of debt recovery events

    `failed_adhoc_disbursement_event_list: Any`
    :   List of failed adhoc disbursement events

    `fba_liquidation_event_list: Any`
    :   List of FBA liquidation events

    `guarantee_claim_event_list: Any`
    :   List of guarantee claim events

    `imaging_services_fee_event_list: Any`
    :   List of imaging services fee events

    `loan_servicing_event_list: Any`
    :   List of loan servicing events

    `network_commingling_transaction_event_list: Any`
    :   List of network commingling events

    `pay_with_amazon_event_list: Any`
    :   List of Pay with Amazon events

    `performance_bond_refund_event_list: Any`
    :   List of performance bond refund events

    `posted_before: Any`
    :   Date filter for events posted before

    `product_ads_payment_event_list: Any`
    :   List of product ads payment events

    `refund_event_list: Any`
    :   List of refund events

    `removal_shipment_adjustment_event_list: Any`
    :   List of removal shipment adjustment events

    `removal_shipment_event_list: Any`
    :   List of removal shipment events

    `rental_transaction_event_list: Any`
    :   List of rental transaction events

    `retrocharge_event_list: Any`
    :   List of retrocharge events

    `safet_reimbursement_event_list: Any`
    :   List of SAFET reimbursement events

    `seller_deal_payment_event_list: Any`
    :   List of seller deal payment events

    `seller_review_enrollment_payment_event_list: Any`
    :   List of seller review enrollment events

    `service_fee_event_list: Any`
    :   List of service fee events

    `service_provider_credit_event_list: Any`
    :   List of service provider credit events

    `shipment_event_list: Any`
    :   List of shipment events

    `shipment_settle_event_list: Any`
    :   List of shipment settlement events

    `tax_withholding_event_list: Any`
    :   List of tax withholding events

    `tds_reimbursement_event_list: Any`
    :   List of TDS reimbursement events

    `trial_shipment_event_list: Any`
    :   List of trial shipment events

    `value_added_service_charge_event_list: Any`
    :   List of value-added service charge events

<a id="ListFinancialEventsContainsCondition"></a>

`ListFinancialEventsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsAnyValueFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventsEqCondition"></a>

`ListFinancialEventsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsSearchFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventsFuzzyCondition"></a>

`ListFinancialEventsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsStringFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventsGtCondition"></a>

`ListFinancialEventsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsSearchFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventsGteCondition"></a>

`ListFinancialEventsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsSearchFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventsInCondition"></a>

`ListFinancialEventsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsInFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventsInFilter"></a>

`ListFinancialEventsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adhoc_disbursement_event_list: list[list[typing.Any]]`
    :   List of adhoc disbursement events

    `adjustment_event_list: list[list[typing.Any]]`
    :   List of adjustment events

    `affordability_expense_event_list: list[list[typing.Any]]`
    :   List of affordability expense events

    `affordability_expense_reversal_event_list: list[list[typing.Any]]`
    :   List of affordability expense reversal events

    `capacity_reservation_billing_event_list: list[list[typing.Any]]`
    :   List of capacity reservation billing events

    `charge_refund_event_list: list[list[typing.Any]]`
    :   List of charge refund events

    `chargeback_event_list: list[list[typing.Any]]`
    :   List of chargeback events

    `coupon_payment_event_list: list[list[typing.Any]]`
    :   List of coupon payment events

    `debt_recovery_event_list: list[list[typing.Any]]`
    :   List of debt recovery events

    `failed_adhoc_disbursement_event_list: list[list[typing.Any]]`
    :   List of failed adhoc disbursement events

    `fba_liquidation_event_list: list[list[typing.Any]]`
    :   List of FBA liquidation events

    `guarantee_claim_event_list: list[list[typing.Any]]`
    :   List of guarantee claim events

    `imaging_services_fee_event_list: list[list[typing.Any]]`
    :   List of imaging services fee events

    `loan_servicing_event_list: list[list[typing.Any]]`
    :   List of loan servicing events

    `network_commingling_transaction_event_list: list[list[typing.Any]]`
    :   List of network commingling events

    `pay_with_amazon_event_list: list[list[typing.Any]]`
    :   List of Pay with Amazon events

    `performance_bond_refund_event_list: list[list[typing.Any]]`
    :   List of performance bond refund events

    `posted_before: list[str]`
    :   Date filter for events posted before

    `product_ads_payment_event_list: list[list[typing.Any]]`
    :   List of product ads payment events

    `refund_event_list: list[list[typing.Any]]`
    :   List of refund events

    `removal_shipment_adjustment_event_list: list[list[typing.Any]]`
    :   List of removal shipment adjustment events

    `removal_shipment_event_list: list[list[typing.Any]]`
    :   List of removal shipment events

    `rental_transaction_event_list: list[list[typing.Any]]`
    :   List of rental transaction events

    `retrocharge_event_list: list[list[typing.Any]]`
    :   List of retrocharge events

    `safet_reimbursement_event_list: list[list[typing.Any]]`
    :   List of SAFET reimbursement events

    `seller_deal_payment_event_list: list[list[typing.Any]]`
    :   List of seller deal payment events

    `seller_review_enrollment_payment_event_list: list[list[typing.Any]]`
    :   List of seller review enrollment events

    `service_fee_event_list: list[list[typing.Any]]`
    :   List of service fee events

    `service_provider_credit_event_list: list[list[typing.Any]]`
    :   List of service provider credit events

    `shipment_event_list: list[list[typing.Any]]`
    :   List of shipment events

    `shipment_settle_event_list: list[list[typing.Any]]`
    :   List of shipment settlement events

    `tax_withholding_event_list: list[list[typing.Any]]`
    :   List of tax withholding events

    `tds_reimbursement_event_list: list[list[typing.Any]]`
    :   List of TDS reimbursement events

    `trial_shipment_event_list: list[list[typing.Any]]`
    :   List of trial shipment events

    `value_added_service_charge_event_list: list[list[typing.Any]]`
    :   List of value-added service charge events

<a id="ListFinancialEventsKeywordCondition"></a>

`ListFinancialEventsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsStringFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventsLikeCondition"></a>

`ListFinancialEventsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsStringFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventsListParams"></a>

`ListFinancialEventsListParams(*args, **kwargs)`
:   Parameters for list_financial_events.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `max_results_per_page: int`
    :   The type of the None singleton.

    `next_token: str`
    :   The type of the None singleton.

    `posted_after: str`
    :   The type of the None singleton.

    `posted_before: str`
    :   The type of the None singleton.

<a id="ListFinancialEventsLtCondition"></a>

`ListFinancialEventsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsSearchFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventsLteCondition"></a>

`ListFinancialEventsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsSearchFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventsNeqCondition"></a>

`ListFinancialEventsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsSearchFilter`
    :   The type of the None singleton.

<a id="ListFinancialEventsNotCondition"></a>

`ListFinancialEventsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsEqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsNeqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsGtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsGteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsLtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsLteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsInCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsLikeCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsFuzzyCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsKeywordCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsContainsCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsNotCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsAndCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsOrCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsAnyCondition`
    :   The type of the None singleton.

<a id="ListFinancialEventsOrCondition"></a>

`ListFinancialEventsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsEqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsNeqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsGtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsGteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsLtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsLteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsInCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsLikeCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsFuzzyCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsKeywordCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsContainsCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsNotCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsAndCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsOrCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsAnyCondition]`
    :   The type of the None singleton.

<a id="ListFinancialEventsSearchFilter"></a>

`ListFinancialEventsSearchFilter(*args, **kwargs)`
:   Available fields for filtering list_financial_events search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adhoc_disbursement_event_list: list[typing.Any] | None`
    :   List of adhoc disbursement events

    `adjustment_event_list: list[typing.Any] | None`
    :   List of adjustment events

    `affordability_expense_event_list: list[typing.Any] | None`
    :   List of affordability expense events

    `affordability_expense_reversal_event_list: list[typing.Any] | None`
    :   List of affordability expense reversal events

    `capacity_reservation_billing_event_list: list[typing.Any] | None`
    :   List of capacity reservation billing events

    `charge_refund_event_list: list[typing.Any] | None`
    :   List of charge refund events

    `chargeback_event_list: list[typing.Any] | None`
    :   List of chargeback events

    `coupon_payment_event_list: list[typing.Any] | None`
    :   List of coupon payment events

    `debt_recovery_event_list: list[typing.Any] | None`
    :   List of debt recovery events

    `failed_adhoc_disbursement_event_list: list[typing.Any] | None`
    :   List of failed adhoc disbursement events

    `fba_liquidation_event_list: list[typing.Any] | None`
    :   List of FBA liquidation events

    `guarantee_claim_event_list: list[typing.Any] | None`
    :   List of guarantee claim events

    `imaging_services_fee_event_list: list[typing.Any] | None`
    :   List of imaging services fee events

    `loan_servicing_event_list: list[typing.Any] | None`
    :   List of loan servicing events

    `network_commingling_transaction_event_list: list[typing.Any] | None`
    :   List of network commingling events

    `pay_with_amazon_event_list: list[typing.Any] | None`
    :   List of Pay with Amazon events

    `performance_bond_refund_event_list: list[typing.Any] | None`
    :   List of performance bond refund events

    `posted_before: str | None`
    :   Date filter for events posted before

    `product_ads_payment_event_list: list[typing.Any] | None`
    :   List of product ads payment events

    `refund_event_list: list[typing.Any] | None`
    :   List of refund events

    `removal_shipment_adjustment_event_list: list[typing.Any] | None`
    :   List of removal shipment adjustment events

    `removal_shipment_event_list: list[typing.Any] | None`
    :   List of removal shipment events

    `rental_transaction_event_list: list[typing.Any] | None`
    :   List of rental transaction events

    `retrocharge_event_list: list[typing.Any] | None`
    :   List of retrocharge events

    `safet_reimbursement_event_list: list[typing.Any] | None`
    :   List of SAFET reimbursement events

    `seller_deal_payment_event_list: list[typing.Any] | None`
    :   List of seller deal payment events

    `seller_review_enrollment_payment_event_list: list[typing.Any] | None`
    :   List of seller review enrollment events

    `service_fee_event_list: list[typing.Any] | None`
    :   List of service fee events

    `service_provider_credit_event_list: list[typing.Any] | None`
    :   List of service provider credit events

    `shipment_event_list: list[typing.Any] | None`
    :   List of shipment events

    `shipment_settle_event_list: list[typing.Any] | None`
    :   List of shipment settlement events

    `tax_withholding_event_list: list[typing.Any] | None`
    :   List of tax withholding events

    `tds_reimbursement_event_list: list[typing.Any] | None`
    :   List of TDS reimbursement events

    `trial_shipment_event_list: list[typing.Any] | None`
    :   List of trial shipment events

    `value_added_service_charge_event_list: list[typing.Any] | None`
    :   List of value-added service charge events

<a id="ListFinancialEventsSearchQuery"></a>

`ListFinancialEventsSearchQuery(*args, **kwargs)`
:   Search query for list_financial_events entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsEqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsNeqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsGtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsGteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsLtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsLteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsInCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsLikeCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsFuzzyCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsKeywordCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsContainsCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsNotCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsAndCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsOrCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.amazon_seller_partner.types.ListFinancialEventsSortFilter]`
    :   The type of the None singleton.

<a id="ListFinancialEventsSortFilter"></a>

`ListFinancialEventsSortFilter(*args, **kwargs)`
:   Available fields for sorting list_financial_events search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adhoc_disbursement_event_list: Literal['asc', 'desc']`
    :   List of adhoc disbursement events

    `adjustment_event_list: Literal['asc', 'desc']`
    :   List of adjustment events

    `affordability_expense_event_list: Literal['asc', 'desc']`
    :   List of affordability expense events

    `affordability_expense_reversal_event_list: Literal['asc', 'desc']`
    :   List of affordability expense reversal events

    `capacity_reservation_billing_event_list: Literal['asc', 'desc']`
    :   List of capacity reservation billing events

    `charge_refund_event_list: Literal['asc', 'desc']`
    :   List of charge refund events

    `chargeback_event_list: Literal['asc', 'desc']`
    :   List of chargeback events

    `coupon_payment_event_list: Literal['asc', 'desc']`
    :   List of coupon payment events

    `debt_recovery_event_list: Literal['asc', 'desc']`
    :   List of debt recovery events

    `failed_adhoc_disbursement_event_list: Literal['asc', 'desc']`
    :   List of failed adhoc disbursement events

    `fba_liquidation_event_list: Literal['asc', 'desc']`
    :   List of FBA liquidation events

    `guarantee_claim_event_list: Literal['asc', 'desc']`
    :   List of guarantee claim events

    `imaging_services_fee_event_list: Literal['asc', 'desc']`
    :   List of imaging services fee events

    `loan_servicing_event_list: Literal['asc', 'desc']`
    :   List of loan servicing events

    `network_commingling_transaction_event_list: Literal['asc', 'desc']`
    :   List of network commingling events

    `pay_with_amazon_event_list: Literal['asc', 'desc']`
    :   List of Pay with Amazon events

    `performance_bond_refund_event_list: Literal['asc', 'desc']`
    :   List of performance bond refund events

    `posted_before: Literal['asc', 'desc']`
    :   Date filter for events posted before

    `product_ads_payment_event_list: Literal['asc', 'desc']`
    :   List of product ads payment events

    `refund_event_list: Literal['asc', 'desc']`
    :   List of refund events

    `removal_shipment_adjustment_event_list: Literal['asc', 'desc']`
    :   List of removal shipment adjustment events

    `removal_shipment_event_list: Literal['asc', 'desc']`
    :   List of removal shipment events

    `rental_transaction_event_list: Literal['asc', 'desc']`
    :   List of rental transaction events

    `retrocharge_event_list: Literal['asc', 'desc']`
    :   List of retrocharge events

    `safet_reimbursement_event_list: Literal['asc', 'desc']`
    :   List of SAFET reimbursement events

    `seller_deal_payment_event_list: Literal['asc', 'desc']`
    :   List of seller deal payment events

    `seller_review_enrollment_payment_event_list: Literal['asc', 'desc']`
    :   List of seller review enrollment events

    `service_fee_event_list: Literal['asc', 'desc']`
    :   List of service fee events

    `service_provider_credit_event_list: Literal['asc', 'desc']`
    :   List of service provider credit events

    `shipment_event_list: Literal['asc', 'desc']`
    :   List of shipment events

    `shipment_settle_event_list: Literal['asc', 'desc']`
    :   List of shipment settlement events

    `tax_withholding_event_list: Literal['asc', 'desc']`
    :   List of tax withholding events

    `tds_reimbursement_event_list: Literal['asc', 'desc']`
    :   List of TDS reimbursement events

    `trial_shipment_event_list: Literal['asc', 'desc']`
    :   List of trial shipment events

    `value_added_service_charge_event_list: Literal['asc', 'desc']`
    :   List of value-added service charge events

<a id="ListFinancialEventsStringFilter"></a>

`ListFinancialEventsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `adhoc_disbursement_event_list: str`
    :   List of adhoc disbursement events

    `adjustment_event_list: str`
    :   List of adjustment events

    `affordability_expense_event_list: str`
    :   List of affordability expense events

    `affordability_expense_reversal_event_list: str`
    :   List of affordability expense reversal events

    `capacity_reservation_billing_event_list: str`
    :   List of capacity reservation billing events

    `charge_refund_event_list: str`
    :   List of charge refund events

    `chargeback_event_list: str`
    :   List of chargeback events

    `coupon_payment_event_list: str`
    :   List of coupon payment events

    `debt_recovery_event_list: str`
    :   List of debt recovery events

    `failed_adhoc_disbursement_event_list: str`
    :   List of failed adhoc disbursement events

    `fba_liquidation_event_list: str`
    :   List of FBA liquidation events

    `guarantee_claim_event_list: str`
    :   List of guarantee claim events

    `imaging_services_fee_event_list: str`
    :   List of imaging services fee events

    `loan_servicing_event_list: str`
    :   List of loan servicing events

    `network_commingling_transaction_event_list: str`
    :   List of network commingling events

    `pay_with_amazon_event_list: str`
    :   List of Pay with Amazon events

    `performance_bond_refund_event_list: str`
    :   List of performance bond refund events

    `posted_before: str`
    :   Date filter for events posted before

    `product_ads_payment_event_list: str`
    :   List of product ads payment events

    `refund_event_list: str`
    :   List of refund events

    `removal_shipment_adjustment_event_list: str`
    :   List of removal shipment adjustment events

    `removal_shipment_event_list: str`
    :   List of removal shipment events

    `rental_transaction_event_list: str`
    :   List of rental transaction events

    `retrocharge_event_list: str`
    :   List of retrocharge events

    `safet_reimbursement_event_list: str`
    :   List of SAFET reimbursement events

    `seller_deal_payment_event_list: str`
    :   List of seller deal payment events

    `seller_review_enrollment_payment_event_list: str`
    :   List of seller review enrollment events

    `service_fee_event_list: str`
    :   List of service fee events

    `service_provider_credit_event_list: str`
    :   List of service provider credit events

    `shipment_event_list: str`
    :   List of shipment events

    `shipment_settle_event_list: str`
    :   List of shipment settlement events

    `tax_withholding_event_list: str`
    :   List of tax withholding events

    `tds_reimbursement_event_list: str`
    :   List of TDS reimbursement events

    `trial_shipment_event_list: str`
    :   List of trial shipment events

    `value_added_service_charge_event_list: str`
    :   List of value-added service charge events

<a id="OrderItemsAndCondition"></a>

`OrderItemsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsEqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsNeqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsGtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsGteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsLtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsLteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsInCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsLikeCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsFuzzyCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsKeywordCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsContainsCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsNotCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsAndCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsOrCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsAnyCondition]`
    :   The type of the None singleton.

<a id="OrderItemsAnyCondition"></a>

`OrderItemsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsAnyValueFilter`
    :   The type of the None singleton.

<a id="OrderItemsAnyValueFilter"></a>

`OrderItemsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amazon_order_id: Any`
    :   ID of the Amazon order

    `asin: Any`
    :   Amazon Standard Identification Number of the product

    `buyer_info: Any`
    :   Information about the buyer

    `buyer_requested_cancel: Any`
    :   Information about buyer's request for cancellation

    `cod_fee: Any`
    :   Cash on delivery fee

    `cod_fee_discount: Any`
    :   Discount on cash on delivery fee

    `condition_id: Any`
    :   Condition ID of the product

    `condition_note: Any`
    :   Additional notes on the condition of the product

    `condition_subtype_id: Any`
    :   Subtype ID of the product condition

    `deemed_reseller_category: Any`
    :   Category indicating if the seller is considered a reseller

    `ioss_number: Any`
    :   Import One Stop Shop number

    `is_gift: Any`
    :   Flag indicating if the order is a gift

    `is_transparency: Any`
    :   Flag indicating if transparency is applied

    `item_price: Any`
    :   Price of the item

    `item_tax: Any`
    :   Tax applied on the item

    `last_update_date: Any`
    :   Date and time of the last update

    `order_item_id: Any`
    :   ID of the order item

    `points_granted: Any`
    :   Points granted for the purchase

    `price_designation: Any`
    :   Designation of the price

    `product_info: Any`
    :   Information about the product

    `promotion_discount: Any`
    :   Discount applied due to promotion

    `promotion_discount_tax: Any`
    :   Tax applied on the promotion discount

    `promotion_ids: Any`
    :   IDs of promotions applied

    `quantity_ordered: Any`
    :   Quantity of the item ordered

    `quantity_shipped: Any`
    :   Quantity of the item shipped

    `scheduled_delivery_end_date: Any`
    :   End date for scheduled delivery

    `scheduled_delivery_start_date: Any`
    :   Start date for scheduled delivery

    `seller_sku: Any`
    :   SKU of the seller

    `serial_number_required: Any`
    :   Flag indicating if serial number is required

    `serial_numbers: Any`
    :   List of serial numbers

    `shipping_discount: Any`
    :   Discount applied on shipping

    `shipping_discount_tax: Any`
    :   Tax applied on the shipping discount

    `shipping_price: Any`
    :   Price of shipping

    `shipping_tax: Any`
    :   Tax applied on shipping

    `store_chain_store_id: Any`
    :   ID of the store chain

    `tax_collection: Any`
    :   Information about tax collection

    `title: Any`
    :   Title of the product

<a id="OrderItemsContainsCondition"></a>

`OrderItemsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsAnyValueFilter`
    :   The type of the None singleton.

<a id="OrderItemsEqCondition"></a>

`OrderItemsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsSearchFilter`
    :   The type of the None singleton.

<a id="OrderItemsFuzzyCondition"></a>

`OrderItemsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsStringFilter`
    :   The type of the None singleton.

<a id="OrderItemsGtCondition"></a>

`OrderItemsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsSearchFilter`
    :   The type of the None singleton.

<a id="OrderItemsGteCondition"></a>

`OrderItemsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsSearchFilter`
    :   The type of the None singleton.

<a id="OrderItemsInCondition"></a>

`OrderItemsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsInFilter`
    :   The type of the None singleton.

<a id="OrderItemsInFilter"></a>

`OrderItemsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amazon_order_id: list[str]`
    :   ID of the Amazon order

    `asin: list[str]`
    :   Amazon Standard Identification Number of the product

    `buyer_info: list[dict[str, typing.Any]]`
    :   Information about the buyer

    `buyer_requested_cancel: list[dict[str, typing.Any]]`
    :   Information about buyer's request for cancellation

    `cod_fee: list[dict[str, typing.Any]]`
    :   Cash on delivery fee

    `cod_fee_discount: list[dict[str, typing.Any]]`
    :   Discount on cash on delivery fee

    `condition_id: list[str]`
    :   Condition ID of the product

    `condition_note: list[str]`
    :   Additional notes on the condition of the product

    `condition_subtype_id: list[str]`
    :   Subtype ID of the product condition

    `deemed_reseller_category: list[str]`
    :   Category indicating if the seller is considered a reseller

    `ioss_number: list[str]`
    :   Import One Stop Shop number

    `is_gift: list[str]`
    :   Flag indicating if the order is a gift

    `is_transparency: list[bool]`
    :   Flag indicating if transparency is applied

    `item_price: list[dict[str, typing.Any]]`
    :   Price of the item

    `item_tax: list[dict[str, typing.Any]]`
    :   Tax applied on the item

    `last_update_date: list[str]`
    :   Date and time of the last update

    `order_item_id: list[str]`
    :   ID of the order item

    `points_granted: list[dict[str, typing.Any]]`
    :   Points granted for the purchase

    `price_designation: list[str]`
    :   Designation of the price

    `product_info: list[dict[str, typing.Any]]`
    :   Information about the product

    `promotion_discount: list[dict[str, typing.Any]]`
    :   Discount applied due to promotion

    `promotion_discount_tax: list[dict[str, typing.Any]]`
    :   Tax applied on the promotion discount

    `promotion_ids: list[list[typing.Any]]`
    :   IDs of promotions applied

    `quantity_ordered: list[int]`
    :   Quantity of the item ordered

    `quantity_shipped: list[int]`
    :   Quantity of the item shipped

    `scheduled_delivery_end_date: list[str]`
    :   End date for scheduled delivery

    `scheduled_delivery_start_date: list[str]`
    :   Start date for scheduled delivery

    `seller_sku: list[str]`
    :   SKU of the seller

    `serial_number_required: list[bool]`
    :   Flag indicating if serial number is required

    `serial_numbers: list[list[typing.Any]]`
    :   List of serial numbers

    `shipping_discount: list[dict[str, typing.Any]]`
    :   Discount applied on shipping

    `shipping_discount_tax: list[dict[str, typing.Any]]`
    :   Tax applied on the shipping discount

    `shipping_price: list[dict[str, typing.Any]]`
    :   Price of shipping

    `shipping_tax: list[dict[str, typing.Any]]`
    :   Tax applied on shipping

    `store_chain_store_id: list[str]`
    :   ID of the store chain

    `tax_collection: list[dict[str, typing.Any]]`
    :   Information about tax collection

    `title: list[str]`
    :   Title of the product

<a id="OrderItemsKeywordCondition"></a>

`OrderItemsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsStringFilter`
    :   The type of the None singleton.

<a id="OrderItemsLikeCondition"></a>

`OrderItemsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsStringFilter`
    :   The type of the None singleton.

<a id="OrderItemsListParams"></a>

`OrderItemsListParams(*args, **kwargs)`
:   Parameters for order_items.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `next_token: str`
    :   The type of the None singleton.

    `order_id: str`
    :   The type of the None singleton.

<a id="OrderItemsLtCondition"></a>

`OrderItemsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsSearchFilter`
    :   The type of the None singleton.

<a id="OrderItemsLteCondition"></a>

`OrderItemsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsSearchFilter`
    :   The type of the None singleton.

<a id="OrderItemsNeqCondition"></a>

`OrderItemsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsSearchFilter`
    :   The type of the None singleton.

<a id="OrderItemsNotCondition"></a>

`OrderItemsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsEqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsNeqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsGtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsGteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsLtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsLteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsInCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsLikeCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsFuzzyCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsKeywordCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsContainsCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsNotCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsAndCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsOrCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsAnyCondition`
    :   The type of the None singleton.

<a id="OrderItemsOrCondition"></a>

`OrderItemsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsEqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsNeqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsGtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsGteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsLtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsLteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsInCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsLikeCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsFuzzyCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsKeywordCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsContainsCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsNotCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsAndCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsOrCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsAnyCondition]`
    :   The type of the None singleton.

<a id="OrderItemsSearchFilter"></a>

`OrderItemsSearchFilter(*args, **kwargs)`
:   Available fields for filtering order_items search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amazon_order_id: str | None`
    :   ID of the Amazon order

    `asin: str | None`
    :   Amazon Standard Identification Number of the product

    `buyer_info: dict[str, typing.Any] | None`
    :   Information about the buyer

    `buyer_requested_cancel: dict[str, typing.Any] | None`
    :   Information about buyer's request for cancellation

    `cod_fee: dict[str, typing.Any] | None`
    :   Cash on delivery fee

    `cod_fee_discount: dict[str, typing.Any] | None`
    :   Discount on cash on delivery fee

    `condition_id: str | None`
    :   Condition ID of the product

    `condition_note: str | None`
    :   Additional notes on the condition of the product

    `condition_subtype_id: str | None`
    :   Subtype ID of the product condition

    `deemed_reseller_category: str | None`
    :   Category indicating if the seller is considered a reseller

    `ioss_number: str | None`
    :   Import One Stop Shop number

    `is_gift: str | None`
    :   Flag indicating if the order is a gift

    `is_transparency: bool | None`
    :   Flag indicating if transparency is applied

    `item_price: dict[str, typing.Any] | None`
    :   Price of the item

    `item_tax: dict[str, typing.Any] | None`
    :   Tax applied on the item

    `last_update_date: str | None`
    :   Date and time of the last update

    `order_item_id: str | None`
    :   ID of the order item

    `points_granted: dict[str, typing.Any] | None`
    :   Points granted for the purchase

    `price_designation: str | None`
    :   Designation of the price

    `product_info: dict[str, typing.Any] | None`
    :   Information about the product

    `promotion_discount: dict[str, typing.Any] | None`
    :   Discount applied due to promotion

    `promotion_discount_tax: dict[str, typing.Any] | None`
    :   Tax applied on the promotion discount

    `promotion_ids: list[typing.Any] | None`
    :   IDs of promotions applied

    `quantity_ordered: int | None`
    :   Quantity of the item ordered

    `quantity_shipped: int | None`
    :   Quantity of the item shipped

    `scheduled_delivery_end_date: str | None`
    :   End date for scheduled delivery

    `scheduled_delivery_start_date: str | None`
    :   Start date for scheduled delivery

    `seller_sku: str | None`
    :   SKU of the seller

    `serial_number_required: bool | None`
    :   Flag indicating if serial number is required

    `serial_numbers: list[typing.Any] | None`
    :   List of serial numbers

    `shipping_discount: dict[str, typing.Any] | None`
    :   Discount applied on shipping

    `shipping_discount_tax: dict[str, typing.Any] | None`
    :   Tax applied on the shipping discount

    `shipping_price: dict[str, typing.Any] | None`
    :   Price of shipping

    `shipping_tax: dict[str, typing.Any] | None`
    :   Tax applied on shipping

    `store_chain_store_id: str | None`
    :   ID of the store chain

    `tax_collection: dict[str, typing.Any] | None`
    :   Information about tax collection

    `title: str | None`
    :   Title of the product

<a id="OrderItemsSearchQuery"></a>

`OrderItemsSearchQuery(*args, **kwargs)`
:   Search query for order_items entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsEqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsNeqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsGtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsGteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsLtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsLteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsInCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsLikeCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsFuzzyCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsKeywordCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsContainsCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsNotCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsAndCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsOrCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrderItemsSortFilter]`
    :   The type of the None singleton.

<a id="OrderItemsSortFilter"></a>

`OrderItemsSortFilter(*args, **kwargs)`
:   Available fields for sorting order_items search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amazon_order_id: Literal['asc', 'desc']`
    :   ID of the Amazon order

    `asin: Literal['asc', 'desc']`
    :   Amazon Standard Identification Number of the product

    `buyer_info: Literal['asc', 'desc']`
    :   Information about the buyer

    `buyer_requested_cancel: Literal['asc', 'desc']`
    :   Information about buyer's request for cancellation

    `cod_fee: Literal['asc', 'desc']`
    :   Cash on delivery fee

    `cod_fee_discount: Literal['asc', 'desc']`
    :   Discount on cash on delivery fee

    `condition_id: Literal['asc', 'desc']`
    :   Condition ID of the product

    `condition_note: Literal['asc', 'desc']`
    :   Additional notes on the condition of the product

    `condition_subtype_id: Literal['asc', 'desc']`
    :   Subtype ID of the product condition

    `deemed_reseller_category: Literal['asc', 'desc']`
    :   Category indicating if the seller is considered a reseller

    `ioss_number: Literal['asc', 'desc']`
    :   Import One Stop Shop number

    `is_gift: Literal['asc', 'desc']`
    :   Flag indicating if the order is a gift

    `is_transparency: Literal['asc', 'desc']`
    :   Flag indicating if transparency is applied

    `item_price: Literal['asc', 'desc']`
    :   Price of the item

    `item_tax: Literal['asc', 'desc']`
    :   Tax applied on the item

    `last_update_date: Literal['asc', 'desc']`
    :   Date and time of the last update

    `order_item_id: Literal['asc', 'desc']`
    :   ID of the order item

    `points_granted: Literal['asc', 'desc']`
    :   Points granted for the purchase

    `price_designation: Literal['asc', 'desc']`
    :   Designation of the price

    `product_info: Literal['asc', 'desc']`
    :   Information about the product

    `promotion_discount: Literal['asc', 'desc']`
    :   Discount applied due to promotion

    `promotion_discount_tax: Literal['asc', 'desc']`
    :   Tax applied on the promotion discount

    `promotion_ids: Literal['asc', 'desc']`
    :   IDs of promotions applied

    `quantity_ordered: Literal['asc', 'desc']`
    :   Quantity of the item ordered

    `quantity_shipped: Literal['asc', 'desc']`
    :   Quantity of the item shipped

    `scheduled_delivery_end_date: Literal['asc', 'desc']`
    :   End date for scheduled delivery

    `scheduled_delivery_start_date: Literal['asc', 'desc']`
    :   Start date for scheduled delivery

    `seller_sku: Literal['asc', 'desc']`
    :   SKU of the seller

    `serial_number_required: Literal['asc', 'desc']`
    :   Flag indicating if serial number is required

    `serial_numbers: Literal['asc', 'desc']`
    :   List of serial numbers

    `shipping_discount: Literal['asc', 'desc']`
    :   Discount applied on shipping

    `shipping_discount_tax: Literal['asc', 'desc']`
    :   Tax applied on the shipping discount

    `shipping_price: Literal['asc', 'desc']`
    :   Price of shipping

    `shipping_tax: Literal['asc', 'desc']`
    :   Tax applied on shipping

    `store_chain_store_id: Literal['asc', 'desc']`
    :   ID of the store chain

    `tax_collection: Literal['asc', 'desc']`
    :   Information about tax collection

    `title: Literal['asc', 'desc']`
    :   Title of the product

<a id="OrderItemsStringFilter"></a>

`OrderItemsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amazon_order_id: str`
    :   ID of the Amazon order

    `asin: str`
    :   Amazon Standard Identification Number of the product

    `buyer_info: str`
    :   Information about the buyer

    `buyer_requested_cancel: str`
    :   Information about buyer's request for cancellation

    `cod_fee: str`
    :   Cash on delivery fee

    `cod_fee_discount: str`
    :   Discount on cash on delivery fee

    `condition_id: str`
    :   Condition ID of the product

    `condition_note: str`
    :   Additional notes on the condition of the product

    `condition_subtype_id: str`
    :   Subtype ID of the product condition

    `deemed_reseller_category: str`
    :   Category indicating if the seller is considered a reseller

    `ioss_number: str`
    :   Import One Stop Shop number

    `is_gift: str`
    :   Flag indicating if the order is a gift

    `is_transparency: str`
    :   Flag indicating if transparency is applied

    `item_price: str`
    :   Price of the item

    `item_tax: str`
    :   Tax applied on the item

    `last_update_date: str`
    :   Date and time of the last update

    `order_item_id: str`
    :   ID of the order item

    `points_granted: str`
    :   Points granted for the purchase

    `price_designation: str`
    :   Designation of the price

    `product_info: str`
    :   Information about the product

    `promotion_discount: str`
    :   Discount applied due to promotion

    `promotion_discount_tax: str`
    :   Tax applied on the promotion discount

    `promotion_ids: str`
    :   IDs of promotions applied

    `quantity_ordered: str`
    :   Quantity of the item ordered

    `quantity_shipped: str`
    :   Quantity of the item shipped

    `scheduled_delivery_end_date: str`
    :   End date for scheduled delivery

    `scheduled_delivery_start_date: str`
    :   Start date for scheduled delivery

    `seller_sku: str`
    :   SKU of the seller

    `serial_number_required: str`
    :   Flag indicating if serial number is required

    `serial_numbers: str`
    :   List of serial numbers

    `shipping_discount: str`
    :   Discount applied on shipping

    `shipping_discount_tax: str`
    :   Tax applied on the shipping discount

    `shipping_price: str`
    :   Price of shipping

    `shipping_tax: str`
    :   Tax applied on shipping

    `store_chain_store_id: str`
    :   ID of the store chain

    `tax_collection: str`
    :   Information about tax collection

    `title: str`
    :   Title of the product

<a id="OrdersAndCondition"></a>

`OrdersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersEqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersNeqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersGtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersGteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersLtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersLteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersInCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersLikeCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersFuzzyCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersKeywordCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersContainsCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersNotCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersAndCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersOrCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersAnyCondition]`
    :   The type of the None singleton.

<a id="OrdersAnyCondition"></a>

`OrdersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersAnyValueFilter`
    :   The type of the None singleton.

<a id="OrdersAnyValueFilter"></a>

`OrdersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amazon_order_id: Any`
    :   Unique identifier for the Amazon order

    `automated_shipping_settings: Any`
    :   Settings related to automated shipping processes

    `buyer_info: Any`
    :   Information about the buyer

    `default_ship_from_location_address: Any`
    :   The default address from which orders are shipped

    `earliest_delivery_date: Any`
    :   Earliest estimated delivery date of the order

    `earliest_ship_date: Any`
    :   Earliest shipment date for the order

    `fulfillment_channel: Any`
    :   Channel through which the order is fulfilled

    `has_regulated_items: Any`
    :   Indicates if the order has regulated items

    `is_access_point_order: Any`
    :   Indicates if the order is an Amazon Hub Counter order

    `is_business_order: Any`
    :   Indicates if the order is a business order

    `is_global_express_enabled: Any`
    :   Indicates if global express is enabled for the order

    `is_ispu: Any`
    :   Indicates if the order is for In-Store Pickup

    `is_premium_order: Any`
    :   Indicates if the order is a premium order

    `is_prime: Any`
    :   Indicates if the order is a Prime order

    `is_replacement_order: Any`
    :   Indicates if the order is a replacement order

    `is_sold_by_ab: Any`
    :   Indicates if the order is sold by Amazon Business

    `last_update_date: Any`
    :   Date and time when the order was last updated

    `latest_delivery_date: Any`
    :   Latest estimated delivery date of the order

    `latest_ship_date: Any`
    :   Latest shipment date for the order

    `marketplace_id: Any`
    :   Identifier for the marketplace where the order was placed

    `number_of_items_shipped: Any`
    :   Number of items shipped in the order

    `number_of_items_unshipped: Any`
    :   Number of items yet to be shipped in the order

    `order_status: Any`
    :   Status of the order

    `order_total: Any`
    :   Total amount of the order

    `order_type: Any`
    :   Type of the order

    `payment_method: Any`
    :   Payment method used for the order

    `payment_method_details: Any`
    :   Details of the payment method used for the order

    `purchase_date: Any`
    :   Date and time when the order was purchased

    `sales_channel: Any`
    :   Channel through which the order was sold

    `seller_id: Any`
    :   Identifier for the seller associated with the order

    `seller_order_id: Any`
    :   Unique identifier given by the seller for the order

    `ship_service_level: Any`
    :   Service level for shipping the order

    `shipment_service_level_category: Any`
    :   Service level category for shipping the order

    `shipping_address: Any`
    :   The address to which the order will be shipped

<a id="OrdersContainsCondition"></a>

`OrdersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersAnyValueFilter`
    :   The type of the None singleton.

<a id="OrdersEqCondition"></a>

`OrdersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersSearchFilter`
    :   The type of the None singleton.

<a id="OrdersFuzzyCondition"></a>

`OrdersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersStringFilter`
    :   The type of the None singleton.

<a id="OrdersGetParams"></a>

`OrdersGetParams(*args, **kwargs)`
:   Parameters for orders.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `order_id: str`
    :   The type of the None singleton.

<a id="OrdersGtCondition"></a>

`OrdersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersSearchFilter`
    :   The type of the None singleton.

<a id="OrdersGteCondition"></a>

`OrdersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersSearchFilter`
    :   The type of the None singleton.

<a id="OrdersInCondition"></a>

`OrdersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersInFilter`
    :   The type of the None singleton.

<a id="OrdersInFilter"></a>

`OrdersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amazon_order_id: list[str]`
    :   Unique identifier for the Amazon order

    `automated_shipping_settings: list[dict[str, typing.Any]]`
    :   Settings related to automated shipping processes

    `buyer_info: list[dict[str, typing.Any]]`
    :   Information about the buyer

    `default_ship_from_location_address: list[dict[str, typing.Any]]`
    :   The default address from which orders are shipped

    `earliest_delivery_date: list[str]`
    :   Earliest estimated delivery date of the order

    `earliest_ship_date: list[str]`
    :   Earliest shipment date for the order

    `fulfillment_channel: list[str]`
    :   Channel through which the order is fulfilled

    `has_regulated_items: list[bool]`
    :   Indicates if the order has regulated items

    `is_access_point_order: list[bool]`
    :   Indicates if the order is an Amazon Hub Counter order

    `is_business_order: list[bool]`
    :   Indicates if the order is a business order

    `is_global_express_enabled: list[bool]`
    :   Indicates if global express is enabled for the order

    `is_ispu: list[bool]`
    :   Indicates if the order is for In-Store Pickup

    `is_premium_order: list[bool]`
    :   Indicates if the order is a premium order

    `is_prime: list[bool]`
    :   Indicates if the order is a Prime order

    `is_replacement_order: list[str]`
    :   Indicates if the order is a replacement order

    `is_sold_by_ab: list[bool]`
    :   Indicates if the order is sold by Amazon Business

    `last_update_date: list[str]`
    :   Date and time when the order was last updated

    `latest_delivery_date: list[str]`
    :   Latest estimated delivery date of the order

    `latest_ship_date: list[str]`
    :   Latest shipment date for the order

    `marketplace_id: list[str]`
    :   Identifier for the marketplace where the order was placed

    `number_of_items_shipped: list[int]`
    :   Number of items shipped in the order

    `number_of_items_unshipped: list[int]`
    :   Number of items yet to be shipped in the order

    `order_status: list[str]`
    :   Status of the order

    `order_total: list[dict[str, typing.Any]]`
    :   Total amount of the order

    `order_type: list[str]`
    :   Type of the order

    `payment_method: list[str]`
    :   Payment method used for the order

    `payment_method_details: list[list[typing.Any]]`
    :   Details of the payment method used for the order

    `purchase_date: list[str]`
    :   Date and time when the order was purchased

    `sales_channel: list[str]`
    :   Channel through which the order was sold

    `seller_id: list[str]`
    :   Identifier for the seller associated with the order

    `seller_order_id: list[str]`
    :   Unique identifier given by the seller for the order

    `ship_service_level: list[str]`
    :   Service level for shipping the order

    `shipment_service_level_category: list[str]`
    :   Service level category for shipping the order

    `shipping_address: list[dict[str, typing.Any]]`
    :   The address to which the order will be shipped

<a id="OrdersKeywordCondition"></a>

`OrdersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersStringFilter`
    :   The type of the None singleton.

<a id="OrdersLikeCondition"></a>

`OrdersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersStringFilter`
    :   The type of the None singleton.

<a id="OrdersListParams"></a>

`OrdersListParams(*args, **kwargs)`
:   Parameters for orders.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_after: str`
    :   The type of the None singleton.

    `created_before: str`
    :   The type of the None singleton.

    `last_updated_after: str`
    :   The type of the None singleton.

    `last_updated_before: str`
    :   The type of the None singleton.

    `marketplace_ids: str`
    :   The type of the None singleton.

    `max_results_per_page: int`
    :   The type of the None singleton.

    `next_token: str`
    :   The type of the None singleton.

    `order_statuses: str`
    :   The type of the None singleton.

<a id="OrdersLtCondition"></a>

`OrdersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersSearchFilter`
    :   The type of the None singleton.

<a id="OrdersLteCondition"></a>

`OrdersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersSearchFilter`
    :   The type of the None singleton.

<a id="OrdersNeqCondition"></a>

`OrdersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersSearchFilter`
    :   The type of the None singleton.

<a id="OrdersNotCondition"></a>

`OrdersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersEqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersNeqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersGtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersGteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersLtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersLteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersInCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersLikeCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersFuzzyCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersKeywordCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersContainsCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersNotCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersAndCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersOrCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersAnyCondition`
    :   The type of the None singleton.

<a id="OrdersOrCondition"></a>

`OrdersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersEqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersNeqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersGtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersGteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersLtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersLteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersInCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersLikeCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersFuzzyCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersKeywordCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersContainsCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersNotCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersAndCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersOrCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersAnyCondition]`
    :   The type of the None singleton.

<a id="OrdersSearchFilter"></a>

`OrdersSearchFilter(*args, **kwargs)`
:   Available fields for filtering orders search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amazon_order_id: str | None`
    :   Unique identifier for the Amazon order

    `automated_shipping_settings: dict[str, typing.Any] | None`
    :   Settings related to automated shipping processes

    `buyer_info: dict[str, typing.Any] | None`
    :   Information about the buyer

    `default_ship_from_location_address: dict[str, typing.Any] | None`
    :   The default address from which orders are shipped

    `earliest_delivery_date: str | None`
    :   Earliest estimated delivery date of the order

    `earliest_ship_date: str | None`
    :   Earliest shipment date for the order

    `fulfillment_channel: str | None`
    :   Channel through which the order is fulfilled

    `has_regulated_items: bool | None`
    :   Indicates if the order has regulated items

    `is_access_point_order: bool | None`
    :   Indicates if the order is an Amazon Hub Counter order

    `is_business_order: bool | None`
    :   Indicates if the order is a business order

    `is_global_express_enabled: bool | None`
    :   Indicates if global express is enabled for the order

    `is_ispu: bool | None`
    :   Indicates if the order is for In-Store Pickup

    `is_premium_order: bool | None`
    :   Indicates if the order is a premium order

    `is_prime: bool | None`
    :   Indicates if the order is a Prime order

    `is_replacement_order: str | None`
    :   Indicates if the order is a replacement order

    `is_sold_by_ab: bool | None`
    :   Indicates if the order is sold by Amazon Business

    `last_update_date: str | None`
    :   Date and time when the order was last updated

    `latest_delivery_date: str | None`
    :   Latest estimated delivery date of the order

    `latest_ship_date: str | None`
    :   Latest shipment date for the order

    `marketplace_id: str | None`
    :   Identifier for the marketplace where the order was placed

    `number_of_items_shipped: int | None`
    :   Number of items shipped in the order

    `number_of_items_unshipped: int | None`
    :   Number of items yet to be shipped in the order

    `order_status: str | None`
    :   Status of the order

    `order_total: dict[str, typing.Any] | None`
    :   Total amount of the order

    `order_type: str | None`
    :   Type of the order

    `payment_method: str | None`
    :   Payment method used for the order

    `payment_method_details: list[typing.Any] | None`
    :   Details of the payment method used for the order

    `purchase_date: str | None`
    :   Date and time when the order was purchased

    `sales_channel: str | None`
    :   Channel through which the order was sold

    `seller_id: str | None`
    :   Identifier for the seller associated with the order

    `seller_order_id: str | None`
    :   Unique identifier given by the seller for the order

    `ship_service_level: str | None`
    :   Service level for shipping the order

    `shipment_service_level_category: str | None`
    :   Service level category for shipping the order

    `shipping_address: dict[str, typing.Any] | None`
    :   The address to which the order will be shipped

<a id="OrdersSearchQuery"></a>

`OrdersSearchQuery(*args, **kwargs)`
:   Search query for orders entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersEqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersNeqCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersGtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersGteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersLtCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersLteCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersInCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersLikeCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersFuzzyCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersKeywordCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersContainsCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersNotCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersAndCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersOrCondition | airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.amazon_seller_partner.types.OrdersSortFilter]`
    :   The type of the None singleton.

<a id="OrdersSortFilter"></a>

`OrdersSortFilter(*args, **kwargs)`
:   Available fields for sorting orders search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amazon_order_id: Literal['asc', 'desc']`
    :   Unique identifier for the Amazon order

    `automated_shipping_settings: Literal['asc', 'desc']`
    :   Settings related to automated shipping processes

    `buyer_info: Literal['asc', 'desc']`
    :   Information about the buyer

    `default_ship_from_location_address: Literal['asc', 'desc']`
    :   The default address from which orders are shipped

    `earliest_delivery_date: Literal['asc', 'desc']`
    :   Earliest estimated delivery date of the order

    `earliest_ship_date: Literal['asc', 'desc']`
    :   Earliest shipment date for the order

    `fulfillment_channel: Literal['asc', 'desc']`
    :   Channel through which the order is fulfilled

    `has_regulated_items: Literal['asc', 'desc']`
    :   Indicates if the order has regulated items

    `is_access_point_order: Literal['asc', 'desc']`
    :   Indicates if the order is an Amazon Hub Counter order

    `is_business_order: Literal['asc', 'desc']`
    :   Indicates if the order is a business order

    `is_global_express_enabled: Literal['asc', 'desc']`
    :   Indicates if global express is enabled for the order

    `is_ispu: Literal['asc', 'desc']`
    :   Indicates if the order is for In-Store Pickup

    `is_premium_order: Literal['asc', 'desc']`
    :   Indicates if the order is a premium order

    `is_prime: Literal['asc', 'desc']`
    :   Indicates if the order is a Prime order

    `is_replacement_order: Literal['asc', 'desc']`
    :   Indicates if the order is a replacement order

    `is_sold_by_ab: Literal['asc', 'desc']`
    :   Indicates if the order is sold by Amazon Business

    `last_update_date: Literal['asc', 'desc']`
    :   Date and time when the order was last updated

    `latest_delivery_date: Literal['asc', 'desc']`
    :   Latest estimated delivery date of the order

    `latest_ship_date: Literal['asc', 'desc']`
    :   Latest shipment date for the order

    `marketplace_id: Literal['asc', 'desc']`
    :   Identifier for the marketplace where the order was placed

    `number_of_items_shipped: Literal['asc', 'desc']`
    :   Number of items shipped in the order

    `number_of_items_unshipped: Literal['asc', 'desc']`
    :   Number of items yet to be shipped in the order

    `order_status: Literal['asc', 'desc']`
    :   Status of the order

    `order_total: Literal['asc', 'desc']`
    :   Total amount of the order

    `order_type: Literal['asc', 'desc']`
    :   Type of the order

    `payment_method: Literal['asc', 'desc']`
    :   Payment method used for the order

    `payment_method_details: Literal['asc', 'desc']`
    :   Details of the payment method used for the order

    `purchase_date: Literal['asc', 'desc']`
    :   Date and time when the order was purchased

    `sales_channel: Literal['asc', 'desc']`
    :   Channel through which the order was sold

    `seller_id: Literal['asc', 'desc']`
    :   Identifier for the seller associated with the order

    `seller_order_id: Literal['asc', 'desc']`
    :   Unique identifier given by the seller for the order

    `ship_service_level: Literal['asc', 'desc']`
    :   Service level for shipping the order

    `shipment_service_level_category: Literal['asc', 'desc']`
    :   Service level category for shipping the order

    `shipping_address: Literal['asc', 'desc']`
    :   The address to which the order will be shipped

<a id="OrdersStringFilter"></a>

`OrdersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amazon_order_id: str`
    :   Unique identifier for the Amazon order

    `automated_shipping_settings: str`
    :   Settings related to automated shipping processes

    `buyer_info: str`
    :   Information about the buyer

    `default_ship_from_location_address: str`
    :   The default address from which orders are shipped

    `earliest_delivery_date: str`
    :   Earliest estimated delivery date of the order

    `earliest_ship_date: str`
    :   Earliest shipment date for the order

    `fulfillment_channel: str`
    :   Channel through which the order is fulfilled

    `has_regulated_items: str`
    :   Indicates if the order has regulated items

    `is_access_point_order: str`
    :   Indicates if the order is an Amazon Hub Counter order

    `is_business_order: str`
    :   Indicates if the order is a business order

    `is_global_express_enabled: str`
    :   Indicates if global express is enabled for the order

    `is_ispu: str`
    :   Indicates if the order is for In-Store Pickup

    `is_premium_order: str`
    :   Indicates if the order is a premium order

    `is_prime: str`
    :   Indicates if the order is a Prime order

    `is_replacement_order: str`
    :   Indicates if the order is a replacement order

    `is_sold_by_ab: str`
    :   Indicates if the order is sold by Amazon Business

    `last_update_date: str`
    :   Date and time when the order was last updated

    `latest_delivery_date: str`
    :   Latest estimated delivery date of the order

    `latest_ship_date: str`
    :   Latest shipment date for the order

    `marketplace_id: str`
    :   Identifier for the marketplace where the order was placed

    `number_of_items_shipped: str`
    :   Number of items shipped in the order

    `number_of_items_unshipped: str`
    :   Number of items yet to be shipped in the order

    `order_status: str`
    :   Status of the order

    `order_total: str`
    :   Total amount of the order

    `order_type: str`
    :   Type of the order

    `payment_method: str`
    :   Payment method used for the order

    `payment_method_details: str`
    :   Details of the payment method used for the order

    `purchase_date: str`
    :   Date and time when the order was purchased

    `sales_channel: str`
    :   Channel through which the order was sold

    `seller_id: str`
    :   Identifier for the seller associated with the order

    `seller_order_id: str`
    :   Unique identifier given by the seller for the order

    `ship_service_level: str`
    :   Service level for shipping the order

    `shipment_service_level_category: str`
    :   Service level category for shipping the order

    `shipping_address: str`
    :   The address to which the order will be shipped

<a id="ReportsGetParams"></a>

`ReportsGetParams(*args, **kwargs)`
:   Parameters for reports.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `report_id: str`
    :   The type of the None singleton.

<a id="ReportsListParams"></a>

`ReportsListParams(*args, **kwargs)`
:   Parameters for reports.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_since: str`
    :   The type of the None singleton.

    `created_until: str`
    :   The type of the None singleton.

    `marketplace_ids: str`
    :   The type of the None singleton.

    `next_token: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `processing_statuses: str`
    :   The type of the None singleton.

    `report_types: str`
    :   The type of the None singleton.