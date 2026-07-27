---
id: airbyte_agent_sdk-connectors-paypal_transaction-types
title: airbyte_agent_sdk.connectors.paypal_transaction.types
---

Module airbyte_agent_sdk.connectors.paypal_transaction.types
============================================================
Type definitions for paypal-transaction connector.

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

<a id="BalancesAndCondition"></a>

`BalancesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesAnyCondition]`
    :   The type of the None singleton.

<a id="BalancesAnyCondition"></a>

`BalancesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesAnyValueFilter`
    :   The type of the None singleton.

<a id="BalancesAnyValueFilter"></a>

`BalancesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Any`
    :   The unique identifier of the account.

    `as_of_time: Any`
    :   The timestamp when the balances data was reported.

    `balances: Any`
    :   Object containing information about the account balances.

    `last_refresh_time: Any`
    :   The timestamp when the balances data was last refreshed.

<a id="BalancesContainsCondition"></a>

`BalancesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesAnyValueFilter`
    :   The type of the None singleton.

<a id="BalancesEqCondition"></a>

`BalancesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesSearchFilter`
    :   The type of the None singleton.

<a id="BalancesFuzzyCondition"></a>

`BalancesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesStringFilter`
    :   The type of the None singleton.

<a id="BalancesGtCondition"></a>

`BalancesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesSearchFilter`
    :   The type of the None singleton.

<a id="BalancesGteCondition"></a>

`BalancesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesSearchFilter`
    :   The type of the None singleton.

<a id="BalancesInCondition"></a>

`BalancesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesInFilter`
    :   The type of the None singleton.

<a id="BalancesInFilter"></a>

`BalancesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: list[str]`
    :   The unique identifier of the account.

    `as_of_time: list[str]`
    :   The timestamp when the balances data was reported.

    `balances: list[list[typing.Any]]`
    :   Object containing information about the account balances.

    `last_refresh_time: list[str]`
    :   The timestamp when the balances data was last refreshed.

<a id="BalancesKeywordCondition"></a>

`BalancesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesStringFilter`
    :   The type of the None singleton.

<a id="BalancesLikeCondition"></a>

`BalancesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesStringFilter`
    :   The type of the None singleton.

<a id="BalancesListParams"></a>

`BalancesListParams(*args, **kwargs)`
:   Parameters for balances.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `as_of_time: str`
    :   The type of the None singleton.

    `currency_code: str`
    :   The type of the None singleton.

<a id="BalancesLtCondition"></a>

`BalancesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesSearchFilter`
    :   The type of the None singleton.

<a id="BalancesLteCondition"></a>

`BalancesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesSearchFilter`
    :   The type of the None singleton.

<a id="BalancesNeqCondition"></a>

`BalancesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesSearchFilter`
    :   The type of the None singleton.

<a id="BalancesNotCondition"></a>

`BalancesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesAnyCondition`
    :   The type of the None singleton.

<a id="BalancesOrCondition"></a>

`BalancesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesAnyCondition]`
    :   The type of the None singleton.

<a id="BalancesSearchFilter"></a>

`BalancesSearchFilter(*args, **kwargs)`
:   Available fields for filtering balances search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str | None`
    :   The unique identifier of the account.

    `as_of_time: str | None`
    :   The timestamp when the balances data was reported.

    `balances: list[typing.Any] | None`
    :   Object containing information about the account balances.

    `last_refresh_time: str | None`
    :   The timestamp when the balances data was last refreshed.

<a id="BalancesSearchQuery"></a>

`BalancesSearchQuery(*args, **kwargs)`
:   Search query for balances entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.paypal_transaction.types.BalancesSortFilter]`
    :   The type of the None singleton.

<a id="BalancesSortFilter"></a>

`BalancesSortFilter(*args, **kwargs)`
:   Available fields for sorting balances search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: Literal['asc', 'desc']`
    :   The unique identifier of the account.

    `as_of_time: Literal['asc', 'desc']`
    :   The timestamp when the balances data was reported.

    `balances: Literal['asc', 'desc']`
    :   Object containing information about the account balances.

    `last_refresh_time: Literal['asc', 'desc']`
    :   The timestamp when the balances data was last refreshed.

<a id="BalancesStringFilter"></a>

`BalancesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_id: str`
    :   The unique identifier of the account.

    `as_of_time: str`
    :   The timestamp when the balances data was reported.

    `balances: str`
    :   Object containing information about the account balances.

    `last_refresh_time: str`
    :   The timestamp when the balances data was last refreshed.

<a id="ListDisputesAndCondition"></a>

`ListDisputesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesAnyCondition]`
    :   The type of the None singleton.

<a id="ListDisputesAnyCondition"></a>

`ListDisputesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesAnyValueFilter`
    :   The type of the None singleton.

<a id="ListDisputesAnyValueFilter"></a>

`ListDisputesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: Any`
    :   The timestamp when the dispute was created.

    `dispute_amount: Any`
    :   Details about the disputed amount.

    `dispute_channel: Any`
    :   The channel through which the dispute was initiated.

    `dispute_id: Any`
    :   The unique identifier for the dispute.

    `dispute_life_cycle_stage: Any`
    :   The stage in the life cycle of the dispute.

    `dispute_state: Any`
    :   The current state of the dispute.

    `disputed_transactions: Any`
    :   Details of transactions involved in the dispute.

    `links: Any`
    :   Links related to the dispute.

    `outcome: Any`
    :   The outcome of the dispute resolution.

    `reason: Any`
    :   The reason for the dispute.

    `status: Any`
    :   The current status of the dispute.

    `update_time: Any`
    :   The timestamp when the dispute was last updated.

    `updated_time_cut: Any`
    :   The cut-off timestamp for the last update.

<a id="ListDisputesContainsCondition"></a>

`ListDisputesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesAnyValueFilter`
    :   The type of the None singleton.

<a id="ListDisputesEqCondition"></a>

`ListDisputesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesSearchFilter`
    :   The type of the None singleton.

<a id="ListDisputesFuzzyCondition"></a>

`ListDisputesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesStringFilter`
    :   The type of the None singleton.

<a id="ListDisputesGtCondition"></a>

`ListDisputesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesSearchFilter`
    :   The type of the None singleton.

<a id="ListDisputesGteCondition"></a>

`ListDisputesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesSearchFilter`
    :   The type of the None singleton.

<a id="ListDisputesInCondition"></a>

`ListDisputesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesInFilter`
    :   The type of the None singleton.

<a id="ListDisputesInFilter"></a>

`ListDisputesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: list[str]`
    :   The timestamp when the dispute was created.

    `dispute_amount: list[dict[str, typing.Any]]`
    :   Details about the disputed amount.

    `dispute_channel: list[str]`
    :   The channel through which the dispute was initiated.

    `dispute_id: list[str]`
    :   The unique identifier for the dispute.

    `dispute_life_cycle_stage: list[str]`
    :   The stage in the life cycle of the dispute.

    `dispute_state: list[str]`
    :   The current state of the dispute.

    `disputed_transactions: list[list[typing.Any]]`
    :   Details of transactions involved in the dispute.

    `links: list[list[typing.Any]]`
    :   Links related to the dispute.

    `outcome: list[str]`
    :   The outcome of the dispute resolution.

    `reason: list[str]`
    :   The reason for the dispute.

    `status: list[str]`
    :   The current status of the dispute.

    `update_time: list[str]`
    :   The timestamp when the dispute was last updated.

    `updated_time_cut: list[str]`
    :   The cut-off timestamp for the last update.

<a id="ListDisputesKeywordCondition"></a>

`ListDisputesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesStringFilter`
    :   The type of the None singleton.

<a id="ListDisputesLikeCondition"></a>

`ListDisputesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesStringFilter`
    :   The type of the None singleton.

<a id="ListDisputesListParams"></a>

`ListDisputesListParams(*args, **kwargs)`
:   Parameters for list_disputes.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `next_page_token: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `update_time_after: str`
    :   The type of the None singleton.

    `update_time_before: str`
    :   The type of the None singleton.

<a id="ListDisputesLtCondition"></a>

`ListDisputesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesSearchFilter`
    :   The type of the None singleton.

<a id="ListDisputesLteCondition"></a>

`ListDisputesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesSearchFilter`
    :   The type of the None singleton.

<a id="ListDisputesNeqCondition"></a>

`ListDisputesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesSearchFilter`
    :   The type of the None singleton.

<a id="ListDisputesNotCondition"></a>

`ListDisputesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesAnyCondition`
    :   The type of the None singleton.

<a id="ListDisputesOrCondition"></a>

`ListDisputesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesAnyCondition]`
    :   The type of the None singleton.

<a id="ListDisputesSearchFilter"></a>

`ListDisputesSearchFilter(*args, **kwargs)`
:   Available fields for filtering list_disputes search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: str | None`
    :   The timestamp when the dispute was created.

    `dispute_amount: dict[str, typing.Any] | None`
    :   Details about the disputed amount.

    `dispute_channel: str | None`
    :   The channel through which the dispute was initiated.

    `dispute_id: str | None`
    :   The unique identifier for the dispute.

    `dispute_life_cycle_stage: str | None`
    :   The stage in the life cycle of the dispute.

    `dispute_state: str | None`
    :   The current state of the dispute.

    `disputed_transactions: list[typing.Any] | None`
    :   Details of transactions involved in the dispute.

    `links: list[typing.Any] | None`
    :   Links related to the dispute.

    `outcome: str | None`
    :   The outcome of the dispute resolution.

    `reason: str | None`
    :   The reason for the dispute.

    `status: str | None`
    :   The current status of the dispute.

    `update_time: str | None`
    :   The timestamp when the dispute was last updated.

    `updated_time_cut: str | None`
    :   The cut-off timestamp for the last update.

<a id="ListDisputesSearchQuery"></a>

`ListDisputesSearchQuery(*args, **kwargs)`
:   Search query for list_disputes entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.paypal_transaction.types.ListDisputesSortFilter]`
    :   The type of the None singleton.

<a id="ListDisputesSortFilter"></a>

`ListDisputesSortFilter(*args, **kwargs)`
:   Available fields for sorting list_disputes search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: Literal['asc', 'desc']`
    :   The timestamp when the dispute was created.

    `dispute_amount: Literal['asc', 'desc']`
    :   Details about the disputed amount.

    `dispute_channel: Literal['asc', 'desc']`
    :   The channel through which the dispute was initiated.

    `dispute_id: Literal['asc', 'desc']`
    :   The unique identifier for the dispute.

    `dispute_life_cycle_stage: Literal['asc', 'desc']`
    :   The stage in the life cycle of the dispute.

    `dispute_state: Literal['asc', 'desc']`
    :   The current state of the dispute.

    `disputed_transactions: Literal['asc', 'desc']`
    :   Details of transactions involved in the dispute.

    `links: Literal['asc', 'desc']`
    :   Links related to the dispute.

    `outcome: Literal['asc', 'desc']`
    :   The outcome of the dispute resolution.

    `reason: Literal['asc', 'desc']`
    :   The reason for the dispute.

    `status: Literal['asc', 'desc']`
    :   The current status of the dispute.

    `update_time: Literal['asc', 'desc']`
    :   The timestamp when the dispute was last updated.

    `updated_time_cut: Literal['asc', 'desc']`
    :   The cut-off timestamp for the last update.

<a id="ListDisputesStringFilter"></a>

`ListDisputesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: str`
    :   The timestamp when the dispute was created.

    `dispute_amount: str`
    :   Details about the disputed amount.

    `dispute_channel: str`
    :   The channel through which the dispute was initiated.

    `dispute_id: str`
    :   The unique identifier for the dispute.

    `dispute_life_cycle_stage: str`
    :   The stage in the life cycle of the dispute.

    `dispute_state: str`
    :   The current state of the dispute.

    `disputed_transactions: str`
    :   Details of transactions involved in the dispute.

    `links: str`
    :   Links related to the dispute.

    `outcome: str`
    :   The outcome of the dispute resolution.

    `reason: str`
    :   The reason for the dispute.

    `status: str`
    :   The current status of the dispute.

    `update_time: str`
    :   The timestamp when the dispute was last updated.

    `updated_time_cut: str`
    :   The cut-off timestamp for the last update.

<a id="ListPaymentsAndCondition"></a>

`ListPaymentsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsAnyCondition]`
    :   The type of the None singleton.

<a id="ListPaymentsAnyCondition"></a>

`ListPaymentsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsAnyValueFilter`
    :   The type of the None singleton.

<a id="ListPaymentsAnyValueFilter"></a>

`ListPaymentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cart: Any`
    :   Details of the cart associated with the payment.

    `create_time: Any`
    :   The date and time when the payment was created.

    `id: Any`
    :   Unique identifier for the payment.

    `intent: Any`
    :   The intention or purpose behind the payment.

    `links: Any`
    :   Collection of links related to the payment

    `payer: Any`
    :   Details of the payer who made the payment

    `state: Any`
    :   The state of the payment.

    `transactions: Any`
    :   List of transactions associated with the payment

    `update_time: Any`
    :   The date and time when the payment was last updated.

<a id="ListPaymentsContainsCondition"></a>

`ListPaymentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsAnyValueFilter`
    :   The type of the None singleton.

<a id="ListPaymentsEqCondition"></a>

`ListPaymentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsSearchFilter`
    :   The type of the None singleton.

<a id="ListPaymentsFuzzyCondition"></a>

`ListPaymentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsStringFilter`
    :   The type of the None singleton.

<a id="ListPaymentsGtCondition"></a>

`ListPaymentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsSearchFilter`
    :   The type of the None singleton.

<a id="ListPaymentsGteCondition"></a>

`ListPaymentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsSearchFilter`
    :   The type of the None singleton.

<a id="ListPaymentsInCondition"></a>

`ListPaymentsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsInFilter`
    :   The type of the None singleton.

<a id="ListPaymentsInFilter"></a>

`ListPaymentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cart: list[str]`
    :   Details of the cart associated with the payment.

    `create_time: list[str]`
    :   The date and time when the payment was created.

    `id: list[str]`
    :   Unique identifier for the payment.

    `intent: list[str]`
    :   The intention or purpose behind the payment.

    `links: list[list[typing.Any]]`
    :   Collection of links related to the payment

    `payer: list[dict[str, typing.Any]]`
    :   Details of the payer who made the payment

    `state: list[str]`
    :   The state of the payment.

    `transactions: list[list[typing.Any]]`
    :   List of transactions associated with the payment

    `update_time: list[str]`
    :   The date and time when the payment was last updated.

<a id="ListPaymentsKeywordCondition"></a>

`ListPaymentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsStringFilter`
    :   The type of the None singleton.

<a id="ListPaymentsLikeCondition"></a>

`ListPaymentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsStringFilter`
    :   The type of the None singleton.

<a id="ListPaymentsListParams"></a>

`ListPaymentsListParams(*args, **kwargs)`
:   Parameters for list_payments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: int`
    :   The type of the None singleton.

    `end_time: str`
    :   The type of the None singleton.

    `start_id: str`
    :   The type of the None singleton.

    `start_time: str`
    :   The type of the None singleton.

<a id="ListPaymentsLtCondition"></a>

`ListPaymentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsSearchFilter`
    :   The type of the None singleton.

<a id="ListPaymentsLteCondition"></a>

`ListPaymentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsSearchFilter`
    :   The type of the None singleton.

<a id="ListPaymentsNeqCondition"></a>

`ListPaymentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsSearchFilter`
    :   The type of the None singleton.

<a id="ListPaymentsNotCondition"></a>

`ListPaymentsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsAnyCondition`
    :   The type of the None singleton.

<a id="ListPaymentsOrCondition"></a>

`ListPaymentsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsAnyCondition]`
    :   The type of the None singleton.

<a id="ListPaymentsSearchFilter"></a>

`ListPaymentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering list_payments search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cart: str | None`
    :   Details of the cart associated with the payment.

    `create_time: str | None`
    :   The date and time when the payment was created.

    `id: str | None`
    :   Unique identifier for the payment.

    `intent: str | None`
    :   The intention or purpose behind the payment.

    `links: list[typing.Any] | None`
    :   Collection of links related to the payment

    `payer: dict[str, typing.Any] | None`
    :   Details of the payer who made the payment

    `state: str | None`
    :   The state of the payment.

    `transactions: list[typing.Any] | None`
    :   List of transactions associated with the payment

    `update_time: str | None`
    :   The date and time when the payment was last updated.

<a id="ListPaymentsSearchQuery"></a>

`ListPaymentsSearchQuery(*args, **kwargs)`
:   Search query for list_payments entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.paypal_transaction.types.ListPaymentsSortFilter]`
    :   The type of the None singleton.

<a id="ListPaymentsSortFilter"></a>

`ListPaymentsSortFilter(*args, **kwargs)`
:   Available fields for sorting list_payments search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cart: Literal['asc', 'desc']`
    :   Details of the cart associated with the payment.

    `create_time: Literal['asc', 'desc']`
    :   The date and time when the payment was created.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the payment.

    `intent: Literal['asc', 'desc']`
    :   The intention or purpose behind the payment.

    `links: Literal['asc', 'desc']`
    :   Collection of links related to the payment

    `payer: Literal['asc', 'desc']`
    :   Details of the payer who made the payment

    `state: Literal['asc', 'desc']`
    :   The state of the payment.

    `transactions: Literal['asc', 'desc']`
    :   List of transactions associated with the payment

    `update_time: Literal['asc', 'desc']`
    :   The date and time when the payment was last updated.

<a id="ListPaymentsStringFilter"></a>

`ListPaymentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cart: str`
    :   Details of the cart associated with the payment.

    `create_time: str`
    :   The date and time when the payment was created.

    `id: str`
    :   Unique identifier for the payment.

    `intent: str`
    :   The intention or purpose behind the payment.

    `links: str`
    :   Collection of links related to the payment

    `payer: str`
    :   Details of the payer who made the payment

    `state: str`
    :   The state of the payment.

    `transactions: str`
    :   List of transactions associated with the payment

    `update_time: str`
    :   The date and time when the payment was last updated.

<a id="ListProductsAndCondition"></a>

`ListProductsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsAnyCondition]`
    :   The type of the None singleton.

<a id="ListProductsAnyCondition"></a>

`ListProductsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsAnyValueFilter`
    :   The type of the None singleton.

<a id="ListProductsAnyValueFilter"></a>

`ListProductsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: Any`
    :   The time when the product was created

    `description: Any`
    :   Detailed information or features of the product

    `id: Any`
    :   Unique identifier for the product

    `links: Any`
    :   List of links related to the fetched products.

    `name: Any`
    :   The name or title of the product

<a id="ListProductsContainsCondition"></a>

`ListProductsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsAnyValueFilter`
    :   The type of the None singleton.

<a id="ListProductsEqCondition"></a>

`ListProductsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsSearchFilter`
    :   The type of the None singleton.

<a id="ListProductsFuzzyCondition"></a>

`ListProductsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsStringFilter`
    :   The type of the None singleton.

<a id="ListProductsGtCondition"></a>

`ListProductsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsSearchFilter`
    :   The type of the None singleton.

<a id="ListProductsGteCondition"></a>

`ListProductsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsSearchFilter`
    :   The type of the None singleton.

<a id="ListProductsInCondition"></a>

`ListProductsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsInFilter`
    :   The type of the None singleton.

<a id="ListProductsInFilter"></a>

`ListProductsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: list[str]`
    :   The time when the product was created

    `description: list[str]`
    :   Detailed information or features of the product

    `id: list[str]`
    :   Unique identifier for the product

    `links: list[list[typing.Any]]`
    :   List of links related to the fetched products.

    `name: list[str]`
    :   The name or title of the product

<a id="ListProductsKeywordCondition"></a>

`ListProductsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsStringFilter`
    :   The type of the None singleton.

<a id="ListProductsLikeCondition"></a>

`ListProductsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsStringFilter`
    :   The type of the None singleton.

<a id="ListProductsListParams"></a>

`ListProductsListParams(*args, **kwargs)`
:   Parameters for list_products.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="ListProductsLtCondition"></a>

`ListProductsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsSearchFilter`
    :   The type of the None singleton.

<a id="ListProductsLteCondition"></a>

`ListProductsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsSearchFilter`
    :   The type of the None singleton.

<a id="ListProductsNeqCondition"></a>

`ListProductsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsSearchFilter`
    :   The type of the None singleton.

<a id="ListProductsNotCondition"></a>

`ListProductsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsAnyCondition`
    :   The type of the None singleton.

<a id="ListProductsOrCondition"></a>

`ListProductsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsAnyCondition]`
    :   The type of the None singleton.

<a id="ListProductsSearchFilter"></a>

`ListProductsSearchFilter(*args, **kwargs)`
:   Available fields for filtering list_products search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: str | None`
    :   The time when the product was created

    `description: str | None`
    :   Detailed information or features of the product

    `id: str | None`
    :   Unique identifier for the product

    `links: list[typing.Any] | None`
    :   List of links related to the fetched products.

    `name: str | None`
    :   The name or title of the product

<a id="ListProductsSearchQuery"></a>

`ListProductsSearchQuery(*args, **kwargs)`
:   Search query for list_products entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.paypal_transaction.types.ListProductsSortFilter]`
    :   The type of the None singleton.

<a id="ListProductsSortFilter"></a>

`ListProductsSortFilter(*args, **kwargs)`
:   Available fields for sorting list_products search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: Literal['asc', 'desc']`
    :   The time when the product was created

    `description: Literal['asc', 'desc']`
    :   Detailed information or features of the product

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the product

    `links: Literal['asc', 'desc']`
    :   List of links related to the fetched products.

    `name: Literal['asc', 'desc']`
    :   The name or title of the product

<a id="ListProductsStringFilter"></a>

`ListProductsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `create_time: str`
    :   The time when the product was created

    `description: str`
    :   Detailed information or features of the product

    `id: str`
    :   Unique identifier for the product

    `links: str`
    :   List of links related to the fetched products.

    `name: str`
    :   The name or title of the product

<a id="SearchInvoicesAndCondition"></a>

`SearchInvoicesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesAnyCondition]`
    :   The type of the None singleton.

<a id="SearchInvoicesAnyCondition"></a>

`SearchInvoicesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesAnyValueFilter`
    :   The type of the None singleton.

<a id="SearchInvoicesAnyValueFilter"></a>

`SearchInvoicesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `additional_recipients: Any`
    :   List of additional recipients associated with the invoice

    `amount: Any`
    :   Detailed breakdown of the invoice amount

    `configuration: Any`
    :   Configuration settings related to the invoice

    `detail: Any`
    :   Detailed information about the invoice

    `due_amount: Any`
    :   Due amount remaining to be paid for the invoice

    `gratuity: Any`
    :   Gratuity amount included in the invoice

    `id: Any`
    :   Unique identifier of the invoice

    `invoicer: Any`
    :   Information about the invoicer associated with the invoice

    `last_update_time: Any`
    :   Date and time of the last update made to the invoice

    `links: Any`
    :   Links associated with the invoice

    `payments: Any`
    :   Payment transactions associated with the invoice

    `primary_recipients: Any`
    :   Primary recipients associated with the invoice

    `refunds: Any`
    :   Refund transactions associated with the invoice

    `status: Any`
    :   Current status of the invoice

<a id="SearchInvoicesContainsCondition"></a>

`SearchInvoicesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesAnyValueFilter`
    :   The type of the None singleton.

<a id="SearchInvoicesEqCondition"></a>

`SearchInvoicesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesSearchFilter`
    :   The type of the None singleton.

<a id="SearchInvoicesFuzzyCondition"></a>

`SearchInvoicesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesStringFilter`
    :   The type of the None singleton.

<a id="SearchInvoicesGtCondition"></a>

`SearchInvoicesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesSearchFilter`
    :   The type of the None singleton.

<a id="SearchInvoicesGteCondition"></a>

`SearchInvoicesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesSearchFilter`
    :   The type of the None singleton.

<a id="SearchInvoicesInCondition"></a>

`SearchInvoicesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesInFilter`
    :   The type of the None singleton.

<a id="SearchInvoicesInFilter"></a>

`SearchInvoicesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `additional_recipients: list[list[typing.Any]]`
    :   List of additional recipients associated with the invoice

    `amount: list[dict[str, typing.Any]]`
    :   Detailed breakdown of the invoice amount

    `configuration: list[dict[str, typing.Any]]`
    :   Configuration settings related to the invoice

    `detail: list[dict[str, typing.Any]]`
    :   Detailed information about the invoice

    `due_amount: list[dict[str, typing.Any]]`
    :   Due amount remaining to be paid for the invoice

    `gratuity: list[dict[str, typing.Any]]`
    :   Gratuity amount included in the invoice

    `id: list[str]`
    :   Unique identifier of the invoice

    `invoicer: list[dict[str, typing.Any]]`
    :   Information about the invoicer associated with the invoice

    `last_update_time: list[str]`
    :   Date and time of the last update made to the invoice

    `links: list[list[typing.Any]]`
    :   Links associated with the invoice

    `payments: list[dict[str, typing.Any]]`
    :   Payment transactions associated with the invoice

    `primary_recipients: list[list[typing.Any]]`
    :   Primary recipients associated with the invoice

    `refunds: list[dict[str, typing.Any]]`
    :   Refund transactions associated with the invoice

    `status: list[str]`
    :   Current status of the invoice

<a id="SearchInvoicesKeywordCondition"></a>

`SearchInvoicesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesStringFilter`
    :   The type of the None singleton.

<a id="SearchInvoicesLikeCondition"></a>

`SearchInvoicesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesStringFilter`
    :   The type of the None singleton.

<a id="SearchInvoicesListParams"></a>

`SearchInvoicesListParams(*args, **kwargs)`
:   Parameters for search_invoices.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `creation_date_range: airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesListParamsCreationDateRange`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="SearchInvoicesListParamsCreationDateRange"></a>

`SearchInvoicesListParamsCreationDateRange(*args, **kwargs)`
:   Filter by invoice creation date range.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `end: str`
    :   The type of the None singleton.

    `start: str`
    :   The type of the None singleton.

<a id="SearchInvoicesLtCondition"></a>

`SearchInvoicesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesSearchFilter`
    :   The type of the None singleton.

<a id="SearchInvoicesLteCondition"></a>

`SearchInvoicesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesSearchFilter`
    :   The type of the None singleton.

<a id="SearchInvoicesNeqCondition"></a>

`SearchInvoicesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesSearchFilter`
    :   The type of the None singleton.

<a id="SearchInvoicesNotCondition"></a>

`SearchInvoicesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesAnyCondition`
    :   The type of the None singleton.

<a id="SearchInvoicesOrCondition"></a>

`SearchInvoicesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesAnyCondition]`
    :   The type of the None singleton.

<a id="SearchInvoicesSearchFilter"></a>

`SearchInvoicesSearchFilter(*args, **kwargs)`
:   Available fields for filtering search_invoices search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `additional_recipients: list[typing.Any] | None`
    :   List of additional recipients associated with the invoice

    `amount: dict[str, typing.Any] | None`
    :   Detailed breakdown of the invoice amount

    `configuration: dict[str, typing.Any] | None`
    :   Configuration settings related to the invoice

    `detail: dict[str, typing.Any] | None`
    :   Detailed information about the invoice

    `due_amount: dict[str, typing.Any] | None`
    :   Due amount remaining to be paid for the invoice

    `gratuity: dict[str, typing.Any] | None`
    :   Gratuity amount included in the invoice

    `id: str | None`
    :   Unique identifier of the invoice

    `invoicer: dict[str, typing.Any] | None`
    :   Information about the invoicer associated with the invoice

    `last_update_time: str | None`
    :   Date and time of the last update made to the invoice

    `links: list[typing.Any] | None`
    :   Links associated with the invoice

    `payments: dict[str, typing.Any] | None`
    :   Payment transactions associated with the invoice

    `primary_recipients: list[typing.Any] | None`
    :   Primary recipients associated with the invoice

    `refunds: dict[str, typing.Any] | None`
    :   Refund transactions associated with the invoice

    `status: str | None`
    :   Current status of the invoice

<a id="SearchInvoicesSearchQuery"></a>

`SearchInvoicesSearchQuery(*args, **kwargs)`
:   Search query for search_invoices entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.paypal_transaction.types.SearchInvoicesSortFilter]`
    :   The type of the None singleton.

<a id="SearchInvoicesSortFilter"></a>

`SearchInvoicesSortFilter(*args, **kwargs)`
:   Available fields for sorting search_invoices search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `additional_recipients: Literal['asc', 'desc']`
    :   List of additional recipients associated with the invoice

    `amount: Literal['asc', 'desc']`
    :   Detailed breakdown of the invoice amount

    `configuration: Literal['asc', 'desc']`
    :   Configuration settings related to the invoice

    `detail: Literal['asc', 'desc']`
    :   Detailed information about the invoice

    `due_amount: Literal['asc', 'desc']`
    :   Due amount remaining to be paid for the invoice

    `gratuity: Literal['asc', 'desc']`
    :   Gratuity amount included in the invoice

    `id: Literal['asc', 'desc']`
    :   Unique identifier of the invoice

    `invoicer: Literal['asc', 'desc']`
    :   Information about the invoicer associated with the invoice

    `last_update_time: Literal['asc', 'desc']`
    :   Date and time of the last update made to the invoice

    `links: Literal['asc', 'desc']`
    :   Links associated with the invoice

    `payments: Literal['asc', 'desc']`
    :   Payment transactions associated with the invoice

    `primary_recipients: Literal['asc', 'desc']`
    :   Primary recipients associated with the invoice

    `refunds: Literal['asc', 'desc']`
    :   Refund transactions associated with the invoice

    `status: Literal['asc', 'desc']`
    :   Current status of the invoice

<a id="SearchInvoicesStringFilter"></a>

`SearchInvoicesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `additional_recipients: str`
    :   List of additional recipients associated with the invoice

    `amount: str`
    :   Detailed breakdown of the invoice amount

    `configuration: str`
    :   Configuration settings related to the invoice

    `detail: str`
    :   Detailed information about the invoice

    `due_amount: str`
    :   Due amount remaining to be paid for the invoice

    `gratuity: str`
    :   Gratuity amount included in the invoice

    `id: str`
    :   Unique identifier of the invoice

    `invoicer: str`
    :   Information about the invoicer associated with the invoice

    `last_update_time: str`
    :   Date and time of the last update made to the invoice

    `links: str`
    :   Links associated with the invoice

    `payments: str`
    :   Payment transactions associated with the invoice

    `primary_recipients: str`
    :   Primary recipients associated with the invoice

    `refunds: str`
    :   Refund transactions associated with the invoice

    `status: str`
    :   Current status of the invoice

<a id="ShowProductDetailsAndCondition"></a>

`ShowProductDetailsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsAnyCondition]`
    :   The type of the None singleton.

<a id="ShowProductDetailsAnyCondition"></a>

`ShowProductDetailsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsAnyValueFilter`
    :   The type of the None singleton.

<a id="ShowProductDetailsAnyValueFilter"></a>

`ShowProductDetailsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `category: Any`
    :   The category to which the product belongs

    `create_time: Any`
    :   The date and time when the product was created

    `description: Any`
    :   The detailed description of the product

    `home_url: Any`
    :   The URL for the home page of the product

    `id: Any`
    :   The unique identifier for the product

    `image_url: Any`
    :   The URL to the image representing the product

    `links: Any`
    :   Contains links related to the product details.

    `name: Any`
    :   The name of the product

    `type_: Any`
    :   The type or category of the product

    `update_time: Any`
    :   The date and time when the product was last updated

<a id="ShowProductDetailsContainsCondition"></a>

`ShowProductDetailsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsAnyValueFilter`
    :   The type of the None singleton.

<a id="ShowProductDetailsEqCondition"></a>

`ShowProductDetailsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsSearchFilter`
    :   The type of the None singleton.

<a id="ShowProductDetailsFuzzyCondition"></a>

`ShowProductDetailsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsStringFilter`
    :   The type of the None singleton.

<a id="ShowProductDetailsGetParams"></a>

`ShowProductDetailsGetParams(*args, **kwargs)`
:   Parameters for show_product_details.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ShowProductDetailsGtCondition"></a>

`ShowProductDetailsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsSearchFilter`
    :   The type of the None singleton.

<a id="ShowProductDetailsGteCondition"></a>

`ShowProductDetailsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsSearchFilter`
    :   The type of the None singleton.

<a id="ShowProductDetailsInCondition"></a>

`ShowProductDetailsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsInFilter`
    :   The type of the None singleton.

<a id="ShowProductDetailsInFilter"></a>

`ShowProductDetailsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `category: list[str]`
    :   The category to which the product belongs

    `create_time: list[str]`
    :   The date and time when the product was created

    `description: list[str]`
    :   The detailed description of the product

    `home_url: list[str]`
    :   The URL for the home page of the product

    `id: list[str]`
    :   The unique identifier for the product

    `image_url: list[str]`
    :   The URL to the image representing the product

    `links: list[list[typing.Any]]`
    :   Contains links related to the product details.

    `name: list[str]`
    :   The name of the product

    `type_: list[str]`
    :   The type or category of the product

    `update_time: list[str]`
    :   The date and time when the product was last updated

<a id="ShowProductDetailsKeywordCondition"></a>

`ShowProductDetailsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsStringFilter`
    :   The type of the None singleton.

<a id="ShowProductDetailsLikeCondition"></a>

`ShowProductDetailsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsStringFilter`
    :   The type of the None singleton.

<a id="ShowProductDetailsLtCondition"></a>

`ShowProductDetailsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsSearchFilter`
    :   The type of the None singleton.

<a id="ShowProductDetailsLteCondition"></a>

`ShowProductDetailsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsSearchFilter`
    :   The type of the None singleton.

<a id="ShowProductDetailsNeqCondition"></a>

`ShowProductDetailsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsSearchFilter`
    :   The type of the None singleton.

<a id="ShowProductDetailsNotCondition"></a>

`ShowProductDetailsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsAnyCondition`
    :   The type of the None singleton.

<a id="ShowProductDetailsOrCondition"></a>

`ShowProductDetailsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsAnyCondition]`
    :   The type of the None singleton.

<a id="ShowProductDetailsSearchFilter"></a>

`ShowProductDetailsSearchFilter(*args, **kwargs)`
:   Available fields for filtering show_product_details search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `category: str | None`
    :   The category to which the product belongs

    `create_time: str | None`
    :   The date and time when the product was created

    `description: str | None`
    :   The detailed description of the product

    `home_url: str | None`
    :   The URL for the home page of the product

    `id: str | None`
    :   The unique identifier for the product

    `image_url: str | None`
    :   The URL to the image representing the product

    `links: list[typing.Any] | None`
    :   Contains links related to the product details.

    `name: str | None`
    :   The name of the product

    `type_: str | None`
    :   The type or category of the product

    `update_time: str | None`
    :   The date and time when the product was last updated

<a id="ShowProductDetailsSearchQuery"></a>

`ShowProductDetailsSearchQuery(*args, **kwargs)`
:   Search query for show_product_details entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.paypal_transaction.types.ShowProductDetailsSortFilter]`
    :   The type of the None singleton.

<a id="ShowProductDetailsSortFilter"></a>

`ShowProductDetailsSortFilter(*args, **kwargs)`
:   Available fields for sorting show_product_details search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `category: Literal['asc', 'desc']`
    :   The category to which the product belongs

    `create_time: Literal['asc', 'desc']`
    :   The date and time when the product was created

    `description: Literal['asc', 'desc']`
    :   The detailed description of the product

    `home_url: Literal['asc', 'desc']`
    :   The URL for the home page of the product

    `id: Literal['asc', 'desc']`
    :   The unique identifier for the product

    `image_url: Literal['asc', 'desc']`
    :   The URL to the image representing the product

    `links: Literal['asc', 'desc']`
    :   Contains links related to the product details.

    `name: Literal['asc', 'desc']`
    :   The name of the product

    `type_: Literal['asc', 'desc']`
    :   The type or category of the product

    `update_time: Literal['asc', 'desc']`
    :   The date and time when the product was last updated

<a id="ShowProductDetailsStringFilter"></a>

`ShowProductDetailsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `category: str`
    :   The category to which the product belongs

    `create_time: str`
    :   The date and time when the product was created

    `description: str`
    :   The detailed description of the product

    `home_url: str`
    :   The URL for the home page of the product

    `id: str`
    :   The unique identifier for the product

    `image_url: str`
    :   The URL to the image representing the product

    `links: str`
    :   Contains links related to the product details.

    `name: str`
    :   The name of the product

    `type_: str`
    :   The type or category of the product

    `update_time: str`
    :   The date and time when the product was last updated

<a id="TransactionsAndCondition"></a>

`TransactionsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsAnyCondition]`
    :   The type of the None singleton.

<a id="TransactionsAnyCondition"></a>

`TransactionsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsAnyValueFilter`
    :   The type of the None singleton.

<a id="TransactionsAnyValueFilter"></a>

`TransactionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auction_info: Any`
    :   Information related to an auction

    `cart_info: Any`
    :   Details of items in the cart

    `incentive_info: Any`
    :   Details of any incentives applied

    `payer_info: Any`
    :   Information about the payer

    `shipping_info: Any`
    :   Shipping information

    `store_info: Any`
    :   Information about the store

    `transaction_id: Any`
    :   Unique ID of the transaction

    `transaction_info: Any`
    :   Detailed information about the transaction

    `transaction_initiation_date: Any`
    :   Date and time when the transaction was initiated

    `transaction_updated_date: Any`
    :   Date and time when the transaction was last updated

<a id="TransactionsContainsCondition"></a>

`TransactionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsAnyValueFilter`
    :   The type of the None singleton.

<a id="TransactionsEqCondition"></a>

`TransactionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsSearchFilter`
    :   The type of the None singleton.

<a id="TransactionsFuzzyCondition"></a>

`TransactionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsStringFilter`
    :   The type of the None singleton.

<a id="TransactionsGtCondition"></a>

`TransactionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsSearchFilter`
    :   The type of the None singleton.

<a id="TransactionsGteCondition"></a>

`TransactionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsSearchFilter`
    :   The type of the None singleton.

<a id="TransactionsInCondition"></a>

`TransactionsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsInFilter`
    :   The type of the None singleton.

<a id="TransactionsInFilter"></a>

`TransactionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auction_info: list[dict[str, typing.Any]]`
    :   Information related to an auction

    `cart_info: list[dict[str, typing.Any]]`
    :   Details of items in the cart

    `incentive_info: list[dict[str, typing.Any]]`
    :   Details of any incentives applied

    `payer_info: list[dict[str, typing.Any]]`
    :   Information about the payer

    `shipping_info: list[dict[str, typing.Any]]`
    :   Shipping information

    `store_info: list[dict[str, typing.Any]]`
    :   Information about the store

    `transaction_id: list[str]`
    :   Unique ID of the transaction

    `transaction_info: list[dict[str, typing.Any]]`
    :   Detailed information about the transaction

    `transaction_initiation_date: list[str]`
    :   Date and time when the transaction was initiated

    `transaction_updated_date: list[str]`
    :   Date and time when the transaction was last updated

<a id="TransactionsKeywordCondition"></a>

`TransactionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsStringFilter`
    :   The type of the None singleton.

<a id="TransactionsLikeCondition"></a>

`TransactionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsStringFilter`
    :   The type of the None singleton.

<a id="TransactionsListParams"></a>

`TransactionsListParams(*args, **kwargs)`
:   Parameters for transactions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `balance_affecting_records_only: str`
    :   The type of the None singleton.

    `end_date: str`
    :   The type of the None singleton.

    `fields: str`
    :   The type of the None singleton.

    `page: int`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

    `start_date: str`
    :   The type of the None singleton.

    `transaction_currency: str`
    :   The type of the None singleton.

    `transaction_id: str`
    :   The type of the None singleton.

    `transaction_status: str`
    :   The type of the None singleton.

    `transaction_type: str`
    :   The type of the None singleton.

<a id="TransactionsLtCondition"></a>

`TransactionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsSearchFilter`
    :   The type of the None singleton.

<a id="TransactionsLteCondition"></a>

`TransactionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsSearchFilter`
    :   The type of the None singleton.

<a id="TransactionsNeqCondition"></a>

`TransactionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsSearchFilter`
    :   The type of the None singleton.

<a id="TransactionsNotCondition"></a>

`TransactionsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsAnyCondition`
    :   The type of the None singleton.

<a id="TransactionsOrCondition"></a>

`TransactionsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsAnyCondition]`
    :   The type of the None singleton.

<a id="TransactionsSearchFilter"></a>

`TransactionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering transactions search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auction_info: dict[str, typing.Any] | None`
    :   Information related to an auction

    `cart_info: dict[str, typing.Any] | None`
    :   Details of items in the cart

    `incentive_info: dict[str, typing.Any] | None`
    :   Details of any incentives applied

    `payer_info: dict[str, typing.Any] | None`
    :   Information about the payer

    `shipping_info: dict[str, typing.Any] | None`
    :   Shipping information

    `store_info: dict[str, typing.Any] | None`
    :   Information about the store

    `transaction_id: str | None`
    :   Unique ID of the transaction

    `transaction_info: dict[str, typing.Any] | None`
    :   Detailed information about the transaction

    `transaction_initiation_date: str | None`
    :   Date and time when the transaction was initiated

    `transaction_updated_date: str | None`
    :   Date and time when the transaction was last updated

<a id="TransactionsSearchQuery"></a>

`TransactionsSearchQuery(*args, **kwargs)`
:   Search query for transactions entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsEqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsNeqCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsGtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsGteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsLtCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsLteCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsInCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsLikeCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsFuzzyCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsKeywordCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsContainsCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsNotCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsAndCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsOrCondition | airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.paypal_transaction.types.TransactionsSortFilter]`
    :   The type of the None singleton.

<a id="TransactionsSortFilter"></a>

`TransactionsSortFilter(*args, **kwargs)`
:   Available fields for sorting transactions search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auction_info: Literal['asc', 'desc']`
    :   Information related to an auction

    `cart_info: Literal['asc', 'desc']`
    :   Details of items in the cart

    `incentive_info: Literal['asc', 'desc']`
    :   Details of any incentives applied

    `payer_info: Literal['asc', 'desc']`
    :   Information about the payer

    `shipping_info: Literal['asc', 'desc']`
    :   Shipping information

    `store_info: Literal['asc', 'desc']`
    :   Information about the store

    `transaction_id: Literal['asc', 'desc']`
    :   Unique ID of the transaction

    `transaction_info: Literal['asc', 'desc']`
    :   Detailed information about the transaction

    `transaction_initiation_date: Literal['asc', 'desc']`
    :   Date and time when the transaction was initiated

    `transaction_updated_date: Literal['asc', 'desc']`
    :   Date and time when the transaction was last updated

<a id="TransactionsStringFilter"></a>

`TransactionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `auction_info: str`
    :   Information related to an auction

    `cart_info: str`
    :   Details of items in the cart

    `incentive_info: str`
    :   Details of any incentives applied

    `payer_info: str`
    :   Information about the payer

    `shipping_info: str`
    :   Shipping information

    `store_info: str`
    :   Information about the store

    `transaction_id: str`
    :   Unique ID of the transaction

    `transaction_info: str`
    :   Detailed information about the transaction

    `transaction_initiation_date: str`
    :   Date and time when the transaction was initiated

    `transaction_updated_date: str`
    :   Date and time when the transaction was last updated