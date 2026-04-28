---
id: airbyte_agent_sdk-connectors-stripe-models
title: airbyte_agent_sdk.connectors.stripe.models
---

Module airbyte_agent_sdk.connectors.stripe.models
=================================================
Pydantic models for stripe connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="AirbyteSearchMeta"></a>

`AirbyteSearchMeta(**data: Any)`
:   Pagination metadata for search responses.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   Cursor for fetching the next page of results.

    `has_more: bool`
    :   Whether more results are available.

    `model_config`
    :   The type of the None singleton.

    `took_ms: int | None`
    :   Time taken to execute the search in milliseconds.

<a id="AirbyteSearchResult"></a>

`AirbyteSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult[ChargesSearchData]
    * airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult[CustomersSearchData]
    * airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult[InvoicesSearchData]
    * airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult[RefundsSearchData]
    * airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult[SubscriptionsSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[ChargesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ChargesSearchResult"></a>

`ChargesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CustomersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CustomersSearchResult"></a>

`CustomersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[InvoicesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="InvoicesSearchResult"></a>

`InvoicesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[RefundsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="RefundsSearchResult"></a>

`RefundsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SubscriptionsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SubscriptionsSearchResult"></a>

`SubscriptionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Balance"></a>

`Balance(**data: Any)`
:   Balance type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `available: list[airbyte_agent_sdk.connectors.stripe.models.BalanceAvailableItem] | Any`
    :   The type of the None singleton.

    `connect_reserved: list[airbyte_agent_sdk.connectors.stripe.models.BalanceConnectReservedItem] | Any | None`
    :   The type of the None singleton.

    `instant_available: list[airbyte_agent_sdk.connectors.stripe.models.BalanceInstantAvailableItem] | Any | None`
    :   The type of the None singleton.

    `issuing: airbyte_agent_sdk.connectors.stripe.models.BalanceIssuing | Any | None`
    :   The type of the None singleton.

    `livemode: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `pending: list[airbyte_agent_sdk.connectors.stripe.models.BalancePendingItem] | Any`
    :   The type of the None singleton.

    `refund_and_dispute_prefunding: airbyte_agent_sdk.connectors.stripe.models.BalanceRefundAndDisputePrefunding | Any | None`
    :   The type of the None singleton.

<a id="BalanceAvailableItem"></a>

`BalanceAvailableItem(**data: Any)`
:   Nested schema for Balance.available_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   Balance amount in the smallest currency unit (e.g., cents)

    `currency: str | Any`
    :   Three-letter ISO currency code, in lowercase

    `model_config`
    :   The type of the None singleton.

    `source_types: airbyte_agent_sdk.connectors.stripe.models.BalanceAvailableItemSourceTypes | Any | None`
    :   Breakdown of balance by source types

<a id="BalanceAvailableItemSourceTypes"></a>

`BalanceAvailableItemSourceTypes(**data: Any)`
:   Breakdown of balance by source types
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bank_account: int | Any | None`
    :   Amount for bank_account

    `card: int | Any | None`
    :   Amount for card

    `fpx: int | Any | None`
    :   Amount for fpx

    `model_config`
    :   The type of the None singleton.

<a id="BalanceConnectReservedItem"></a>

`BalanceConnectReservedItem(**data: Any)`
:   Nested schema for Balance.connect_reserved_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   Balance amount in the smallest currency unit

    `currency: str | Any`
    :   Three-letter ISO currency code, in lowercase

    `model_config`
    :   The type of the None singleton.

    `source_types: airbyte_agent_sdk.connectors.stripe.models.BalanceConnectReservedItemSourceTypes | Any | None`
    :   Breakdown of balance by source types

<a id="BalanceConnectReservedItemSourceTypes"></a>

`BalanceConnectReservedItemSourceTypes(**data: Any)`
:   Breakdown of balance by source types
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bank_account: int | Any | None`
    :   Amount for bank_account

    `card: int | Any | None`
    :   Amount for card

    `fpx: int | Any | None`
    :   Amount for fpx

    `model_config`
    :   The type of the None singleton.

<a id="BalanceInstantAvailableItem"></a>

`BalanceInstantAvailableItem(**data: Any)`
:   Nested schema for Balance.instant_available_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   Balance amount in the smallest currency unit

    `currency: str | Any`
    :   Three-letter ISO currency code, in lowercase

    `model_config`
    :   The type of the None singleton.

    `net_available: list[airbyte_agent_sdk.connectors.stripe.models.BalanceInstantAvailableItemNetAvailableItem] | Any | None`
    :   Net balance amount available after deducting fees

    `source_types: airbyte_agent_sdk.connectors.stripe.models.BalanceInstantAvailableItemSourceTypes | Any | None`
    :   Breakdown of balance by source types

<a id="BalanceInstantAvailableItemNetAvailableItem"></a>

`BalanceInstantAvailableItemNetAvailableItem(**data: Any)`
:   Nested schema for BalanceInstantAvailableItem.net_available_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   Net balance amount

    `destination: str | Any`
    :   ID of the external account

    `model_config`
    :   The type of the None singleton.

    `source_types: airbyte_agent_sdk.connectors.stripe.models.BalanceInstantAvailableItemNetAvailableItemSourceTypes | Any | None`
    :   Breakdown of balance by source types

<a id="BalanceInstantAvailableItemNetAvailableItemSourceTypes"></a>

`BalanceInstantAvailableItemNetAvailableItemSourceTypes(**data: Any)`
:   Breakdown of balance by source types
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bank_account: int | Any | None`
    :   Amount for bank_account

    `card: int | Any | None`
    :   Amount for card

    `fpx: int | Any | None`
    :   Amount for fpx

    `model_config`
    :   The type of the None singleton.

<a id="BalanceInstantAvailableItemSourceTypes"></a>

`BalanceInstantAvailableItemSourceTypes(**data: Any)`
:   Breakdown of balance by source types
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bank_account: int | Any | None`
    :   Amount for bank_account

    `card: int | Any | None`
    :   Amount for card

    `fpx: int | Any | None`
    :   Amount for fpx

    `model_config`
    :   The type of the None singleton.

<a id="BalanceIssuing"></a>

`BalanceIssuing(**data: Any)`
:   Funds that are available for use with Issuing cards
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `available: list[airbyte_agent_sdk.connectors.stripe.models.BalanceIssuingAvailableItem] | Any`
    :   Funds available for issuing

    `model_config`
    :   The type of the None singleton.

<a id="BalanceIssuingAvailableItem"></a>

`BalanceIssuingAvailableItem(**data: Any)`
:   Nested schema for BalanceIssuing.available_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   Balance amount

    `currency: str | Any`
    :   Three-letter ISO currency code

    `model_config`
    :   The type of the None singleton.

    `source_types: airbyte_agent_sdk.connectors.stripe.models.BalanceIssuingAvailableItemSourceTypes | Any | None`
    :   Breakdown of balance by source types

<a id="BalanceIssuingAvailableItemSourceTypes"></a>

`BalanceIssuingAvailableItemSourceTypes(**data: Any)`
:   Breakdown of balance by source types
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bank_account: int | Any | None`
    :   Amount for bank_account

    `card: int | Any | None`
    :   Amount for card

    `fpx: int | Any | None`
    :   Amount for fpx

    `model_config`
    :   The type of the None singleton.

<a id="BalancePendingItem"></a>

`BalancePendingItem(**data: Any)`
:   Nested schema for Balance.pending_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   Balance amount in the smallest currency unit

    `currency: str | Any`
    :   Three-letter ISO currency code, in lowercase

    `model_config`
    :   The type of the None singleton.

    `source_types: airbyte_agent_sdk.connectors.stripe.models.BalancePendingItemSourceTypes | Any | None`
    :   Breakdown of balance by source types

<a id="BalancePendingItemSourceTypes"></a>

`BalancePendingItemSourceTypes(**data: Any)`
:   Breakdown of balance by source types
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bank_account: int | Any | None`
    :   Amount for bank_account

    `card: int | Any | None`
    :   Amount for card

    `fpx: int | Any | None`
    :   Amount for fpx

    `model_config`
    :   The type of the None singleton.

<a id="BalanceRefundAndDisputePrefunding"></a>

`BalanceRefundAndDisputePrefunding(**data: Any)`
:   Funds reserved for covering future refunds or disputes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `available: list[airbyte_agent_sdk.connectors.stripe.models.BalanceRefundAndDisputePrefundingAvailableItem] | Any`
    :   Available funds for refunds and disputes

    `model_config`
    :   The type of the None singleton.

    `pending: list[airbyte_agent_sdk.connectors.stripe.models.BalanceRefundAndDisputePrefundingPendingItem] | Any`
    :   Pending funds for refunds and disputes

<a id="BalanceRefundAndDisputePrefundingAvailableItem"></a>

`BalanceRefundAndDisputePrefundingAvailableItem(**data: Any)`
:   Nested schema for BalanceRefundAndDisputePrefunding.available_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   Balance amount

    `currency: str | Any`
    :   Three-letter ISO currency code

    `model_config`
    :   The type of the None singleton.

    `source_types: airbyte_agent_sdk.connectors.stripe.models.BalanceRefundAndDisputePrefundingAvailableItemSourceTypes | Any | None`
    :   Breakdown of balance by source types

<a id="BalanceRefundAndDisputePrefundingAvailableItemSourceTypes"></a>

`BalanceRefundAndDisputePrefundingAvailableItemSourceTypes(**data: Any)`
:   Breakdown of balance by source types
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bank_account: int | Any | None`
    :   Amount for bank_account

    `card: int | Any | None`
    :   Amount for card

    `fpx: int | Any | None`
    :   Amount for fpx

    `model_config`
    :   The type of the None singleton.

<a id="BalanceRefundAndDisputePrefundingPendingItem"></a>

`BalanceRefundAndDisputePrefundingPendingItem(**data: Any)`
:   Nested schema for BalanceRefundAndDisputePrefunding.pending_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   Balance amount

    `currency: str | Any`
    :   Three-letter ISO currency code

    `model_config`
    :   The type of the None singleton.

    `source_types: airbyte_agent_sdk.connectors.stripe.models.BalanceRefundAndDisputePrefundingPendingItemSourceTypes | Any | None`
    :   Breakdown of balance by source types

<a id="BalanceRefundAndDisputePrefundingPendingItemSourceTypes"></a>

`BalanceRefundAndDisputePrefundingPendingItemSourceTypes(**data: Any)`
:   Breakdown of balance by source types
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bank_account: int | Any | None`
    :   Amount for bank_account

    `card: int | Any | None`
    :   Amount for card

    `fpx: int | Any | None`
    :   Amount for fpx

    `model_config`
    :   The type of the None singleton.

<a id="BalanceTransaction"></a>

`BalanceTransaction(**data: Any)`
:   BalanceTransaction type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   The type of the None singleton.

    `available_on: int | Any`
    :   The type of the None singleton.

    `balance_type: str | Any`
    :   The type of the None singleton.

    `created: int | Any`
    :   The type of the None singleton.

    `currency: str | Any`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `exchange_rate: float | Any | None`
    :   The type of the None singleton.

    `fee: int | Any`
    :   The type of the None singleton.

    `fee_details: list[airbyte_agent_sdk.connectors.stripe.models.BalanceTransactionFeeDetailsItem] | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `net: int | Any`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `reporting_category: str | Any`
    :   The type of the None singleton.

    `source: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

<a id="BalanceTransactionFeeDetailsItem"></a>

`BalanceTransactionFeeDetailsItem(**data: Any)`
:   Nested schema for BalanceTransaction.fee_details_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   Amount of the fee, in cents

    `application: str | Any | None`
    :   ID of the Connect application that earned the fee

    `currency: str | Any`
    :   Three-letter ISO currency code, in lowercase

    `description: str | Any | None`
    :   An arbitrary string attached to the object

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Type of the fee

<a id="BalanceTransactionList"></a>

`BalanceTransactionList(**data: Any)`
:   BalanceTransactionList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.BalanceTransaction] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="BalanceTransactionsListResultMeta"></a>

`BalanceTransactionsListResultMeta(**data: Any)`
:   Metadata for balance_transactions.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Charge"></a>

`Charge(**data: Any)`
:   Charge type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   The type of the None singleton.

    `amount_captured: int | Any`
    :   The type of the None singleton.

    `amount_refunded: int | Any`
    :   The type of the None singleton.

    `amount_updates: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `application: str | Any | None`
    :   The type of the None singleton.

    `application_fee: str | Any | None`
    :   The type of the None singleton.

    `application_fee_amount: int | Any | None`
    :   The type of the None singleton.

    `balance_transaction: str | Any | None`
    :   The type of the None singleton.

    `billing_details: airbyte_agent_sdk.connectors.stripe.models.ChargeBillingDetails | Any`
    :   The type of the None singleton.

    `calculated_statement_descriptor: str | Any | None`
    :   The type of the None singleton.

    `captured: bool | Any`
    :   The type of the None singleton.

    `created: int | Any`
    :   The type of the None singleton.

    `currency: str | Any`
    :   The type of the None singleton.

    `customer: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `destination: str | Any | None`
    :   The type of the None singleton.

    `dispute: str | Any | None`
    :   The type of the None singleton.

    `disputed: bool | Any`
    :   The type of the None singleton.

    `failure_balance_transaction: str | Any | None`
    :   The type of the None singleton.

    `failure_code: str | Any | None`
    :   The type of the None singleton.

    `failure_message: str | Any | None`
    :   The type of the None singleton.

    `fraud_details: airbyte_agent_sdk.connectors.stripe.models.ChargeFraudDetails | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `invoice: str | Any | None`
    :   The type of the None singleton.

    `livemode: bool | Any`
    :   The type of the None singleton.

    `metadata: dict[str, str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `on_behalf_of: str | Any | None`
    :   The type of the None singleton.

    `order: str | Any | None`
    :   The type of the None singleton.

    `outcome: airbyte_agent_sdk.connectors.stripe.models.ChargeOutcome | Any | None`
    :   The type of the None singleton.

    `paid: bool | Any`
    :   The type of the None singleton.

    `payment_intent: str | Any | None`
    :   The type of the None singleton.

    `payment_method: str | Any | None`
    :   The type of the None singleton.

    `payment_method_details: airbyte_agent_sdk.connectors.stripe.models.ChargePaymentMethodDetails | Any | None`
    :   The type of the None singleton.

    `presentment_details: airbyte_agent_sdk.connectors.stripe.models.ChargePresentmentDetails | Any | None`
    :   The type of the None singleton.

    `radar_options: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `receipt_email: str | Any | None`
    :   The type of the None singleton.

    `receipt_number: str | Any | None`
    :   The type of the None singleton.

    `receipt_url: str | Any | None`
    :   The type of the None singleton.

    `refunded: bool | Any`
    :   The type of the None singleton.

    `refunds: airbyte_agent_sdk.connectors.stripe.models.ChargeRefunds | Any | None`
    :   The type of the None singleton.

    `review: str | Any | None`
    :   The type of the None singleton.

    `shipping: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `source: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `source_transfer: str | Any | None`
    :   The type of the None singleton.

    `statement_descriptor: str | Any | None`
    :   The type of the None singleton.

    `statement_descriptor_suffix: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `transfer_data: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `transfer_group: str | Any | None`
    :   The type of the None singleton.

<a id="ChargeBillingDetails"></a>

`ChargeBillingDetails(**data: Any)`
:   Billing information associated with the payment method
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: airbyte_agent_sdk.connectors.stripe.models.ChargeBillingDetailsAddress | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `tax_id: str | Any | None`
    :   The type of the None singleton.

<a id="ChargeBillingDetailsAddress"></a>

`ChargeBillingDetailsAddress(**data: Any)`
:   Nested schema for ChargeBillingDetails.address
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `city: str | Any | None`
    :   The type of the None singleton.

    `country: str | Any | None`
    :   The type of the None singleton.

    `line1: str | Any | None`
    :   The type of the None singleton.

    `line2: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `postal_code: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

<a id="ChargeFraudDetails"></a>

`ChargeFraudDetails(**data: Any)`
:   Information on fraud assessments for the charge
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `stripe_report: str | Any | None`
    :   Assessments from Stripe. If set, the value is `fraudulent`.

    `user_report: str | Any | None`
    :   Assessments from you or your users. Possible values are `fraudulent` and `safe`

<a id="ChargeList"></a>

`ChargeList(**data: Any)`
:   ChargeList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.Charge] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="ChargeOutcome"></a>

`ChargeOutcome(**data: Any)`
:   Details about whether the payment was accepted, and why
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `advice_code: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `network_advice_code: str | Any | None`
    :   The type of the None singleton.

    `network_decline_code: str | Any | None`
    :   The type of the None singleton.

    `network_status: str | Any`
    :   The type of the None singleton.

    `reason: str | Any | None`
    :   The type of the None singleton.

    `risk_level: str | Any`
    :   The type of the None singleton.

    `risk_score: int | Any`
    :   The type of the None singleton.

    `seller_message: str | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

<a id="ChargePaymentMethodDetails"></a>

`ChargePaymentMethodDetails(**data: Any)`
:   Details about the payment method at the time of the transaction
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `card: airbyte_agent_sdk.connectors.stripe.models.ChargePaymentMethodDetailsCard | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

<a id="ChargePaymentMethodDetailsCard"></a>

`ChargePaymentMethodDetailsCard(**data: Any)`
:   Nested schema for ChargePaymentMethodDetails.card
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount_authorized: int | Any | None`
    :   Amount authorized on the card

    `authorization_code: str | Any | None`
    :   Authorization code on the charge

    `brand: str | Any`
    :   Card brand

    `checks: airbyte_agent_sdk.connectors.stripe.models.ChargePaymentMethodDetailsCardChecks | Any | None`
    :   Check results by Card networks on Card address and CVC

    `country: str | Any`
    :   Two-letter ISO code representing the country of the card

    `exp_month: int | Any`
    :   Two-digit number representing the card's expiration month

    `exp_year: int | Any`
    :   Four-digit number representing the card's expiration year

    `extended_authorization: airbyte_agent_sdk.connectors.stripe.models.ChargePaymentMethodDetailsCardExtendedAuthorization | Any | None`
    :   Extended authorization details

    `fingerprint: str | Any`
    :   Uniquely identifies this particular card number

    `funding: str | Any`
    :   Card funding type

    `incremental_authorization: airbyte_agent_sdk.connectors.stripe.models.ChargePaymentMethodDetailsCardIncrementalAuthorization | Any | None`
    :   Incremental authorization details

    `installments: dict[str, typing.Any] | Any | None`
    :   Installment details

    `last4: str | Any`
    :   The last four digits of the card

    `mandate: str | Any | None`
    :   ID of the mandate used to make this payment

    `model_config`
    :   The type of the None singleton.

    `multicapture: airbyte_agent_sdk.connectors.stripe.models.ChargePaymentMethodDetailsCardMulticapture | Any | None`
    :   Multicapture details

    `network: str | Any`
    :   Card network

    `network_token: airbyte_agent_sdk.connectors.stripe.models.ChargePaymentMethodDetailsCardNetworkToken | Any | None`
    :   Network token details

    `network_transaction_id: str | Any | None`
    :   Network transaction identifier

    `overcapture: airbyte_agent_sdk.connectors.stripe.models.ChargePaymentMethodDetailsCardOvercapture | Any | None`
    :   Overcapture details

    `regulated_status: str | Any | None`
    :   Regulated status of the card

    `three_d_secure: dict[str, typing.Any] | Any | None`
    :   3D Secure details

    `wallet: dict[str, typing.Any] | Any | None`
    :   Digital wallet details if used

<a id="ChargePaymentMethodDetailsCardChecks"></a>

`ChargePaymentMethodDetailsCardChecks(**data: Any)`
:   Check results by Card networks on Card address and CVC
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address_line1_check: str | Any | None`
    :   The type of the None singleton.

    `address_postal_code_check: str | Any | None`
    :   The type of the None singleton.

    `cvc_check: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ChargePaymentMethodDetailsCardExtendedAuthorization"></a>

`ChargePaymentMethodDetailsCardExtendedAuthorization(**data: Any)`
:   Extended authorization details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

<a id="ChargePaymentMethodDetailsCardIncrementalAuthorization"></a>

`ChargePaymentMethodDetailsCardIncrementalAuthorization(**data: Any)`
:   Incremental authorization details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

<a id="ChargePaymentMethodDetailsCardMulticapture"></a>

`ChargePaymentMethodDetailsCardMulticapture(**data: Any)`
:   Multicapture details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

<a id="ChargePaymentMethodDetailsCardNetworkToken"></a>

`ChargePaymentMethodDetailsCardNetworkToken(**data: Any)`
:   Network token details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `used: bool | Any`
    :   The type of the None singleton.

<a id="ChargePaymentMethodDetailsCardOvercapture"></a>

`ChargePaymentMethodDetailsCardOvercapture(**data: Any)`
:   Overcapture details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `maximum_amount_capturable: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

<a id="ChargePresentmentDetails"></a>

`ChargePresentmentDetails(**data: Any)`
:   Currency presentation information for multi-currency charges
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount_authorized: int | Any | None`
    :   Amount authorized in the presentment currency

    `amount_charged: int | Any | None`
    :   Amount charged in the presentment currency

    `currency: str | Any | None`
    :   Three-letter ISO currency code for presentment

    `model_config`
    :   The type of the None singleton.

<a id="ChargeRefunds"></a>

`ChargeRefunds(**data: Any)`
:   A list of refunds that have been applied to the charge
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `total_count: int | Any`
    :   Total number of refunds

    `url: str | Any`
    :   URL to access the refunds list

<a id="ChargeSearchResult"></a>

`ChargeSearchResult(**data: Any)`
:   ChargeSearchResult type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.Charge] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="ChargesListResultMeta"></a>

`ChargesListResultMeta(**data: Any)`
:   Metadata for charges.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ChargesSearchData"></a>

`ChargesSearchData(**data: Any)`
:   Search result data for charges entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | None`
    :   Amount intended to be collected by this payment in the smallest currency unit (e.g., 100 cents for $1.00), supporting up to eight digits.

    `amount_captured: int | None`
    :   Amount that was actually captured from this charge.

    `amount_refunded: int | None`
    :   Amount that has been refunded back to the customer.

    `amount_updates: list[typing.Any] | None`
    :   Updates to the amount that have been made during the charge lifecycle.

    `application: str | None`
    :   ID of the application that created this charge (Connect only).

    `application_fee: str | None`
    :   ID of the application fee associated with this charge (Connect only).

    `application_fee_amount: int | None`
    :   The amount of the application fee deducted from this charge (Connect only).

    `balance_transaction: str | None`
    :   ID of the balance transaction that describes the impact of this charge on your account balance (excluding refunds or disputes).

    `billing_details: dict[str, typing.Any] | None`
    :   Billing information associated with the payment method at the time of the transaction, including name, email, phone, and address.

    `calculated_statement_descriptor: str | None`
    :   The full statement descriptor that appears on the customer's credit card statement, combining prefix and suffix.

    `captured: bool | None`
    :   Whether the charge has been captured and funds transferred to your account.

    `card: dict[str, typing.Any] | None`
    :   Deprecated card object containing payment card details if a card was used.

    `created: int | None`
    :   Timestamp indicating when the charge was created.

    `currency: str | None`
    :   Three-letter ISO currency code in lowercase (e.g., 'usd', 'eur') for the charge amount.

    `customer: str | None`
    :   ID of the customer this charge is for, if one exists.

    `description: str | None`
    :   An arbitrary string attached to the charge, often useful for displaying to users or internal reference.

    `destination: str | None`
    :   ID of the destination account where funds are transferred (Connect only).

    `dispute: str | None`
    :   ID of the dispute object if the charge has been disputed.

    `disputed: bool | None`
    :   Whether the charge has been disputed by the customer with their card issuer.

    `failure_balance_transaction: str | None`
    :   ID of the balance transaction that describes the reversal of funds if the charge failed.

    `failure_code: str | None`
    :   Error code explaining the reason for charge failure, if applicable.

    `failure_message: str | None`
    :   Human-readable message providing more details about why the charge failed.

    `fraud_details: dict[str, typing.Any] | None`
    :   Information about fraud assessments and user reports related to this charge.

    `id: str`
    :   Unique identifier for the charge, used to link transactions across other records.

    `invoice: str | None`
    :   ID of the invoice this charge is for, if the charge was created by invoicing.

    `livemode: bool | None`
    :   Whether the charge occurred in live mode (true) or test mode (false).

    `metadata: dict[str, typing.Any] | None`
    :   Key-value pairs for storing additional structured information about the charge, useful for internal tracking.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
    :   String representing the object type, always 'charge' for charge objects.

    `on_behalf_of: str | None`
    :   ID of the account on whose behalf the charge was made (Connect only).

    `order: str | None`
    :   Deprecated field for order information associated with this charge.

    `outcome: dict[str, typing.Any] | None`
    :   Details about the outcome of the charge, including network status, risk assessment, and reason codes.

    `paid: bool | None`
    :   Whether the charge succeeded and funds were successfully collected.

    `payment_intent: str | None`
    :   ID of the PaymentIntent associated with this charge, if one exists.

    `payment_method: str | None`
    :   ID of the payment method used for this charge.

    `payment_method_details: dict[str, typing.Any] | None`
    :   Details about the payment method at the time of the transaction, including card brand, network, and authentication results.

    `receipt_email: str | None`
    :   Email address to which the receipt for this charge was sent.

    `receipt_number: str | None`
    :   Receipt number that appears on email receipts sent for this charge.

    `receipt_url: str | None`
    :   URL to a hosted receipt page for this charge, viewable by the customer.

    `refunded: bool | None`
    :   Whether the charge has been fully refunded (partial refunds will still show as false).

    `refunds: dict[str, typing.Any] | None`
    :   List of refunds that have been applied to this charge.

    `review: str | None`
    :   ID of the review object associated with this charge, if it was flagged for manual review.

    `shipping: dict[str, typing.Any] | None`
    :   Shipping information for the charge, including recipient name, address, and tracking details.

    `source: dict[str, typing.Any] | None`
    :   Deprecated payment source object used to create this charge.

    `source_transfer: str | None`
    :   ID of the transfer from a source account if funds came from another Stripe account (Connect only).

    `statement_description: str | None`
    :   Deprecated alias for statement_descriptor.

    `statement_descriptor: str | None`
    :   Statement descriptor that overrides the account default for card charges, appearing on the customer's statement.

    `statement_descriptor_suffix: str | None`
    :   Suffix concatenated to the account's statement descriptor prefix to form the complete descriptor on customer statements.

    `status: str | None`
    :   Current status of the payment: 'succeeded' (completed), 'pending' (processing), or 'failed' (unsuccessful).

    `transfer_data: dict[str, typing.Any] | None`
    :   Object containing destination and amount for transfers to connected accounts (Connect only).

    `transfer_group: str | None`
    :   String identifier for grouping related charges and transfers together (Connect only).

    `updated: int | None`
    :   Timestamp of the last update to this charge object.

<a id="Customer"></a>

`Customer(**data: Any)`
:   Customer type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: airbyte_agent_sdk.connectors.stripe.models.CustomerAddress | Any | None`
    :   The type of the None singleton.

    `balance: int | Any`
    :   The type of the None singleton.

    `business_name: str | Any | None`
    :   The type of the None singleton.

    `cash_balance: airbyte_agent_sdk.connectors.stripe.models.CustomerCashBalance | Any | None`
    :   The type of the None singleton.

    `created: int | Any`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `customer_account: str | Any | None`
    :   The type of the None singleton.

    `default_currency: str | Any | None`
    :   The type of the None singleton.

    `default_source: str | Any | None`
    :   The type of the None singleton.

    `delinquent: bool | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `discount: airbyte_agent_sdk.connectors.stripe.models.CustomerDiscount | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `individual_name: str | Any | None`
    :   The type of the None singleton.

    `invoice_credit_balance: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `invoice_prefix: str | Any | None`
    :   The type of the None singleton.

    `invoice_settings: airbyte_agent_sdk.connectors.stripe.models.CustomerInvoiceSettings | Any`
    :   The type of the None singleton.

    `livemode: bool | Any`
    :   The type of the None singleton.

    `metadata: dict[str, str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `next_invoice_sequence: int | Any | None`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `preferred_locales: list[str] | Any | None`
    :   The type of the None singleton.

    `shipping: airbyte_agent_sdk.connectors.stripe.models.CustomerShipping | Any | None`
    :   The type of the None singleton.

    `sources: airbyte_agent_sdk.connectors.stripe.models.CustomerSources | Any | None`
    :   The type of the None singleton.

    `subscriptions: airbyte_agent_sdk.connectors.stripe.models.CustomerSubscriptions | Any | None`
    :   The type of the None singleton.

    `tax_exempt: str | Any | None`
    :   The type of the None singleton.

    `test_clock: str | Any | None`
    :   The type of the None singleton.

<a id="CustomerAddress"></a>

`CustomerAddress(**data: Any)`
:   The customer's address
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `city: str | Any | None`
    :   City, district, suburb, town, or village

    `country: str | Any | None`
    :   Two-letter country code (ISO 3166-1 alpha-2)

    `line1: str | Any | None`
    :   Address line 1, such as the street, PO Box, or company name

    `line2: str | Any | None`
    :   Address line 2, such as the apartment, suite, unit, or building

    `model_config`
    :   The type of the None singleton.

    `postal_code: str | Any | None`
    :   ZIP or postal code

    `state: str | Any | None`
    :   State, county, province, or region

<a id="CustomerCashBalance"></a>

`CustomerCashBalance(**data: Any)`
:   The current funds being held by Stripe on behalf of the customer
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `available: dict[str, typing.Any] | Any | None`
    :   A hash of all cash balances available to this customer

    `customer: str | Any`
    :   The ID of the customer whose cash balance this object represents

    `customer_account: str | Any | None`
    :   The ID of the account whose cash balance this object represents

    `livemode: bool | Any`
    :   Has the value true if the object exists in live mode or false if in test mode

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   String representing the object's type

    `settings: airbyte_agent_sdk.connectors.stripe.models.CustomerCashBalanceSettings | Any`
    :   A hash of settings for this cash balance

<a id="CustomerCashBalanceSettings"></a>

`CustomerCashBalanceSettings(**data: Any)`
:   A hash of settings for this cash balance
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `reconciliation_mode: str | Any`
    :   The configuration for how funds that land in the customer cash balance are reconciled

    `using_merchant_default: bool | Any`
    :   A flag to indicate if reconciliation mode returned is the user's default or is specific to this customer cash balance

<a id="CustomerCreateParams"></a>

`CustomerCreateParams(**data: Any)`
:   CustomerCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: airbyte_agent_sdk.connectors.stripe.models.CustomerCreateParamsAddress | Any`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `email: str | Any`
    :   The type of the None singleton.

    `metadata: dict[str, str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `phone: str | Any`
    :   The type of the None singleton.

<a id="CustomerCreateParamsAddress"></a>

`CustomerCreateParamsAddress(**data: Any)`
:   The customer's address
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `city: str | Any`
    :   City, district, suburb, town, or village

    `country: str | Any`
    :   Two-letter country code (ISO 3166-1 alpha-2)

    `line1: str | Any`
    :   Address line 1

    `line2: str | Any`
    :   Address line 2

    `model_config`
    :   The type of the None singleton.

    `postal_code: str | Any`
    :   ZIP or postal code

    `state: str | Any`
    :   State, county, province, or region

<a id="CustomerDeletedResponse"></a>

`CustomerDeletedResponse(**data: Any)`
:   CustomerDeletedResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `deleted: bool | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

<a id="CustomerDiscount"></a>

`CustomerDiscount(**data: Any)`
:   Describes the current discount active on the customer, if there is one
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `checkout_session: str | Any | None`
    :   The Checkout session that this coupon is applied to, if applicable

    `customer: str | Any | None`
    :   The ID of the customer associated with this discount

    `customer_account: str | Any | None`
    :   The ID of the account associated with this discount

    `end: int | Any | None`
    :   If the coupon has a duration of repeating, the date that this discount will end

    `id: str | Any`
    :   The ID of the discount object

    `invoice: str | Any | None`
    :   The invoice that the discount's coupon was applied to

    `invoice_item: str | Any | None`
    :   The invoice item that the discount's coupon was applied to

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   String representing the object's type

    `promotion_code: str | Any | None`
    :   The promotion code applied to create this discount

    `source: airbyte_agent_sdk.connectors.stripe.models.CustomerDiscountSource | Any`
    :   The source of the discount

    `start: int | Any`
    :   Date that the coupon was applied

    `subscription: str | Any | None`
    :   The subscription that this coupon is applied to

    `subscription_item: str | Any | None`
    :   The subscription item that this coupon is applied to

<a id="CustomerDiscountSource"></a>

`CustomerDiscountSource(**data: Any)`
:   The source of the discount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `coupon: str | Any | None`
    :   The coupon that was redeemed to create this discount

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The source type of the discount

<a id="CustomerInvoiceSettings"></a>

`CustomerInvoiceSettings(**data: Any)`
:   The customer's default invoice settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `custom_fields: list[airbyte_agent_sdk.connectors.stripe.models.CustomerInvoiceSettingsCustomFieldsItem] | Any | None`
    :   Default custom fields to be displayed on invoices for this customer

    `default_payment_method: str | Any | None`
    :   ID of a payment method that's attached to the customer

    `footer: str | Any | None`
    :   Default footer to be displayed on invoices for this customer

    `model_config`
    :   The type of the None singleton.

    `rendering_options: airbyte_agent_sdk.connectors.stripe.models.CustomerInvoiceSettingsRenderingOptions | Any | None`
    :   Default options for invoice PDF rendering for this customer

<a id="CustomerInvoiceSettingsCustomFieldsItem"></a>

`CustomerInvoiceSettingsCustomFieldsItem(**data: Any)`
:   Nested schema for CustomerInvoiceSettings.custom_fields_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The name of the custom field

    `value: str | Any`
    :   The value of the custom field

<a id="CustomerInvoiceSettingsRenderingOptions"></a>

`CustomerInvoiceSettingsRenderingOptions(**data: Any)`
:   Default options for invoice PDF rendering for this customer
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount_tax_display: str | Any | None`
    :   How line-item prices and amounts will be displayed with respect to tax on invoice PDFs

    `model_config`
    :   The type of the None singleton.

    `template: str | Any | None`
    :   ID of the invoice rendering template to be used for this customer's invoices

<a id="CustomerList"></a>

`CustomerList(**data: Any)`
:   CustomerList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.Customer] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="CustomerSearchResult"></a>

`CustomerSearchResult(**data: Any)`
:   CustomerSearchResult type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.Customer] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="CustomerShipping"></a>

`CustomerShipping(**data: Any)`
:   Mailing and shipping address for the customer
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: airbyte_agent_sdk.connectors.stripe.models.CustomerShippingAddress | Any`
    :   Customer shipping address

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Customer name

    `phone: str | Any | None`
    :   Customer phone (including extension)

<a id="CustomerShippingAddress"></a>

`CustomerShippingAddress(**data: Any)`
:   Customer shipping address
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `city: str | Any | None`
    :   City, district, suburb, town, or village

    `country: str | Any | None`
    :   Two-letter country code (ISO 3166-1 alpha-2)

    `line1: str | Any | None`
    :   Address line 1, such as the street, PO Box, or company name

    `line2: str | Any | None`
    :   Address line 2, such as the apartment, suite, unit, or building

    `model_config`
    :   The type of the None singleton.

    `postal_code: str | Any | None`
    :   ZIP or postal code

    `state: str | Any | None`
    :   State, county, province, or region

<a id="CustomerSources"></a>

`CustomerSources(**data: Any)`
:   The customer's payment sources, if any
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.CustomerSourcesDataItem] | Any`
    :   Details about each object

    `has_more: bool | Any`
    :   True if this list has another page of items after this one

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   String representing the object's type

    `url: str | Any`
    :   The URL where this list can be accessed

<a id="CustomerSourcesDataItem"></a>

`CustomerSourcesDataItem(**data: Any)`
:   Nested schema for CustomerSources.data_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: str | Any | None`
    :   The account this bank account belongs to

    `account_holder_name: str | Any | None`
    :   The name of the person or business that owns the bank account

    `account_holder_type: str | Any | None`
    :   The type of entity that holds the account

    `account_type: str | Any | None`
    :   The bank account type

    `available_payout_methods: list[str] | Any | None`
    :   A set of available payout methods for this bank account

    `bank_name: str | Any | None`
    :   Name of the bank associated with the routing number

    `country: str | Any`
    :   Two-letter ISO code representing the country the bank account is located in

    `currency: str | Any`
    :   Three-letter ISO code for the currency paid out to the bank account

    `customer: str | Any | None`
    :   The ID of the customer that the bank account is associated with

    `fingerprint: str | Any | None`
    :   Uniquely identifies this particular bank account

    `id: str | Any`
    :   Unique identifier for the object

    `last4: str | Any`
    :   The last four digits of the bank account number

    `metadata: dict[str, str] | Any | None`
    :   Set of key-value pairs that you can attach to an object

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   String representing the object's type

    `routing_number: str | Any | None`
    :   The routing transit number for the bank account

    `status: str | Any`
    :   The status of the bank account

<a id="CustomerSubscriptions"></a>

`CustomerSubscriptions(**data: Any)`
:   The customer's current subscriptions, if any
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.Subscription] | Any`
    :   Details about each subscription

    `has_more: bool | Any`
    :   True if this list has another page of items after this one

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   String representing the object's type

    `url: str | Any`
    :   The URL where this list can be accessed

<a id="CustomerUpdateParams"></a>

`CustomerUpdateParams(**data: Any)`
:   CustomerUpdateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: airbyte_agent_sdk.connectors.stripe.models.CustomerUpdateParamsAddress | Any`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `email: str | Any`
    :   The type of the None singleton.

    `metadata: dict[str, str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `phone: str | Any`
    :   The type of the None singleton.

<a id="CustomerUpdateParamsAddress"></a>

`CustomerUpdateParamsAddress(**data: Any)`
:   The customer's address
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `city: str | Any`
    :   City, district, suburb, town, or village

    `country: str | Any`
    :   Two-letter country code (ISO 3166-1 alpha-2)

    `line1: str | Any`
    :   Address line 1

    `line2: str | Any`
    :   Address line 2

    `model_config`
    :   The type of the None singleton.

    `postal_code: str | Any`
    :   ZIP or postal code

    `state: str | Any`
    :   State, county, province, or region

<a id="CustomersApiSearchResultMeta"></a>

`CustomersApiSearchResultMeta(**data: Any)`
:   Metadata for customers.Action.API_SEARCH operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CustomersListResultMeta"></a>

`CustomersListResultMeta(**data: Any)`
:   Metadata for customers.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CustomersSearchData"></a>

`CustomersSearchData(**data: Any)`
:   Search result data for customers entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_balance: int | None`
    :   Current balance value representing funds owed by or to the customer.

    `address: dict[str, typing.Any] | None`
    :   The customer's address information including line1, line2, city, state, postal code, and country.

    `balance: int | None`
    :   Current balance (positive or negative) that is automatically applied to the customer's next invoice.

    `cards: list[typing.Any] | None`
    :   Card payment methods associated with the customer account.

    `created: int | None`
    :   Timestamp indicating when the customer object was created.

    `currency: str | None`
    :   Three-letter ISO currency code representing the customer's default currency.

    `default_card: str | None`
    :   The default card to be used for charges when no specific payment method is provided.

    `default_source: str | None`
    :   The default payment source (card or bank account) for the customer.

    `delinquent: bool | None`
    :   Boolean indicating whether the customer is currently delinquent on payments.

    `description: str | None`
    :   An arbitrary string attached to the customer, often useful for displaying to users.

    `discount: dict[str, typing.Any] | None`
    :   Discount object describing any active discount applied to the customer.

    `email: str | None`
    :   The customer's email address for communication and tracking purposes.

    `id: str | None`
    :   Unique identifier for the customer object.

    `invoice_prefix: str | None`
    :   The prefix for invoice numbers generated for this customer.

    `invoice_settings: dict[str, typing.Any] | None`
    :   Customer's invoice-related settings including default payment method and custom fields.

    `is_deleted: bool | None`
    :   Boolean indicating whether the customer has been deleted.

    `livemode: bool | None`
    :   Boolean indicating whether the object exists in live mode or test mode.

    `metadata: dict[str, typing.Any] | None`
    :   Set of key-value pairs for storing additional structured information about the customer.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The customer's full name or business name.

    `next_invoice_sequence: int | None`
    :   The sequence number for the next invoice generated for this customer.

    `object_: str | None`
    :   String representing the object type, always 'customer'.

    `phone: str | None`
    :   The customer's phone number.

    `preferred_locales: list[typing.Any] | None`
    :   Array of preferred locales for the customer, used for invoice and receipt localization.

    `shipping: dict[str, typing.Any] | None`
    :   Mailing and shipping address for the customer, appears on invoices emailed to the customer.

    `sources: str`
    :   Payment sources (cards, bank accounts) attached to the customer for making payments.

    `subscriptions: dict[str, typing.Any] | None`
    :   List of active subscriptions associated with the customer.

    `tax_exempt: str | None`
    :   Describes the customer's tax exemption status (none, exempt, or reverse).

    `tax_info: str | None`
    :   Tax identification information for the customer.

    `tax_info_verification: str | None`
    :   Verification status of the customer's tax information.

    `test_clock: str | None`
    :   ID of the test clock associated with this customer for testing time-dependent scenarios.

    `updated: int | None`
    :   Timestamp indicating when the customer object was last updated.

<a id="Dispute"></a>

`Dispute(**data: Any)`
:   Dispute type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   The type of the None singleton.

    `balance_transactions: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `charge: str | Any`
    :   The type of the None singleton.

    `created: int | Any`
    :   The type of the None singleton.

    `currency: str | Any`
    :   The type of the None singleton.

    `enhanced_eligibility_types: list[str] | Any`
    :   The type of the None singleton.

    `evidence: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `evidence_details: airbyte_agent_sdk.connectors.stripe.models.DisputeEvidenceDetails | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_charge_refundable: bool | Any`
    :   The type of the None singleton.

    `livemode: bool | Any`
    :   The type of the None singleton.

    `metadata: dict[str, str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `payment_intent: str | Any | None`
    :   The type of the None singleton.

    `payment_method_details: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `reason: str | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

<a id="DisputeEvidenceDetails"></a>

`DisputeEvidenceDetails(**data: Any)`
:   Information about the evidence submission
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `due_by: int | Any | None`
    :   Date by which evidence must be submitted, measured in seconds since the Unix epoch

    `has_evidence: bool | Any`
    :   Whether evidence has been staged for this dispute

    `model_config`
    :   The type of the None singleton.

    `past_due: bool | Any`
    :   Whether the last evidence submission was submitted past the due date

    `submission_count: int | Any`
    :   The number of times evidence has been submitted

<a id="DisputeList"></a>

`DisputeList(**data: Any)`
:   DisputeList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.Dispute] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="DisputesListResultMeta"></a>

`DisputesListResultMeta(**data: Any)`
:   Metadata for disputes.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Invoice"></a>

`Invoice(**data: Any)`
:   Invoice type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_country: str | Any | None`
    :   The type of the None singleton.

    `account_name: str | Any | None`
    :   The type of the None singleton.

    `account_tax_ids: list[str] | Any | None`
    :   The type of the None singleton.

    `amount_due: int | Any`
    :   The type of the None singleton.

    `amount_overpaid: int | Any`
    :   The type of the None singleton.

    `amount_paid: int | Any`
    :   The type of the None singleton.

    `amount_remaining: int | Any`
    :   The type of the None singleton.

    `amount_shipping: int | Any`
    :   The type of the None singleton.

    `application: str | Any | None`
    :   The type of the None singleton.

    `application_fee_amount: int | Any | None`
    :   The type of the None singleton.

    `attempt_count: int | Any`
    :   The type of the None singleton.

    `attempted: bool | Any`
    :   The type of the None singleton.

    `auto_advance: bool | Any`
    :   The type of the None singleton.

    `automatic_tax: airbyte_agent_sdk.connectors.stripe.models.InvoiceAutomaticTax | Any`
    :   The type of the None singleton.

    `automatically_finalizes_at: int | Any | None`
    :   The type of the None singleton.

    `billing_reason: str | Any | None`
    :   The type of the None singleton.

    `charge: str | Any | None`
    :   The type of the None singleton.

    `collection_method: str | Any`
    :   The type of the None singleton.

    `confirmation_secret: airbyte_agent_sdk.connectors.stripe.models.InvoiceConfirmationSecret | Any | None`
    :   The type of the None singleton.

    `created: int | Any`
    :   The type of the None singleton.

    `currency: str | Any`
    :   The type of the None singleton.

    `custom_fields: list[airbyte_agent_sdk.connectors.stripe.models.InvoiceCustomFieldsItem] | Any | None`
    :   The type of the None singleton.

    `customer: str | Any`
    :   The type of the None singleton.

    `customer_account: str | Any | None`
    :   The type of the None singleton.

    `customer_address: airbyte_agent_sdk.connectors.stripe.models.InvoiceCustomerAddress | Any | None`
    :   The type of the None singleton.

    `customer_email: str | Any | None`
    :   The type of the None singleton.

    `customer_name: str | Any | None`
    :   The type of the None singleton.

    `customer_phone: str | Any | None`
    :   The type of the None singleton.

    `customer_shipping: airbyte_agent_sdk.connectors.stripe.models.InvoiceCustomerShipping | Any | None`
    :   The type of the None singleton.

    `customer_tax_exempt: str | Any | None`
    :   The type of the None singleton.

    `customer_tax_ids: list[airbyte_agent_sdk.connectors.stripe.models.InvoiceCustomerTaxIdsItem] | Any | None`
    :   The type of the None singleton.

    `default_payment_method: str | Any | None`
    :   The type of the None singleton.

    `default_source: str | Any | None`
    :   The type of the None singleton.

    `default_tax_rates: list[airbyte_agent_sdk.connectors.stripe.models.InvoiceDefaultTaxRatesItem] | Any`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `discount: airbyte_agent_sdk.connectors.stripe.models.InvoiceDiscount | Any | None`
    :   The type of the None singleton.

    `discounts: list[str] | Any`
    :   The type of the None singleton.

    `due_date: int | Any | None`
    :   The type of the None singleton.

    `effective_at: int | Any | None`
    :   The type of the None singleton.

    `ending_balance: int | Any | None`
    :   The type of the None singleton.

    `footer: str | Any | None`
    :   The type of the None singleton.

    `from_invoice: airbyte_agent_sdk.connectors.stripe.models.InvoiceFromInvoice | Any | None`
    :   The type of the None singleton.

    `hosted_invoice_url: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `invoice_pdf: str | Any | None`
    :   The type of the None singleton.

    `issuer: airbyte_agent_sdk.connectors.stripe.models.InvoiceIssuer | Any`
    :   The type of the None singleton.

    `last_finalization_error: airbyte_agent_sdk.connectors.stripe.models.InvoiceLastFinalizationError | Any | None`
    :   The type of the None singleton.

    `latest_revision: str | Any | None`
    :   The type of the None singleton.

    `lines: airbyte_agent_sdk.connectors.stripe.models.InvoiceLines | Any`
    :   The type of the None singleton.

    `livemode: bool | Any`
    :   The type of the None singleton.

    `metadata: dict[str, str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_payment_attempt: int | Any | None`
    :   The type of the None singleton.

    `number: str | Any | None`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `on_behalf_of: str | Any | None`
    :   The type of the None singleton.

    `paid: bool | Any | None`
    :   The type of the None singleton.

    `paid_out_of_band: bool | Any | None`
    :   The type of the None singleton.

    `parent: airbyte_agent_sdk.connectors.stripe.models.InvoiceParent | Any | None`
    :   The type of the None singleton.

    `payment_intent: str | Any | None`
    :   The type of the None singleton.

    `payment_settings: airbyte_agent_sdk.connectors.stripe.models.InvoicePaymentSettings | Any`
    :   The type of the None singleton.

    `payments: airbyte_agent_sdk.connectors.stripe.models.InvoicePayments | Any`
    :   The type of the None singleton.

    `period_end: int | Any`
    :   The type of the None singleton.

    `period_start: int | Any`
    :   The type of the None singleton.

    `post_payment_credit_notes_amount: int | Any`
    :   The type of the None singleton.

    `pre_payment_credit_notes_amount: int | Any`
    :   The type of the None singleton.

    `quote: str | Any | None`
    :   The type of the None singleton.

    `receipt_number: str | Any | None`
    :   The type of the None singleton.

    `rendering: airbyte_agent_sdk.connectors.stripe.models.InvoiceRendering | Any | None`
    :   The type of the None singleton.

    `rendering_options: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `shipping_cost: airbyte_agent_sdk.connectors.stripe.models.InvoiceShippingCost | Any | None`
    :   The type of the None singleton.

    `shipping_details: airbyte_agent_sdk.connectors.stripe.models.InvoiceShippingDetails | Any | None`
    :   The type of the None singleton.

    `starting_balance: int | Any`
    :   The type of the None singleton.

    `statement_descriptor: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `status_transitions: airbyte_agent_sdk.connectors.stripe.models.InvoiceStatusTransitions | Any`
    :   The type of the None singleton.

    `subscription: str | Any | None`
    :   The type of the None singleton.

    `subscription_details: airbyte_agent_sdk.connectors.stripe.models.InvoiceSubscriptionDetails | Any | None`
    :   The type of the None singleton.

    `subtotal: int | Any`
    :   The type of the None singleton.

    `subtotal_excluding_tax: int | Any | None`
    :   The type of the None singleton.

    `tax: int | Any | None`
    :   The type of the None singleton.

    `test_clock: str | Any | None`
    :   The type of the None singleton.

    `threshold_reason: airbyte_agent_sdk.connectors.stripe.models.InvoiceThresholdReason | Any | None`
    :   The type of the None singleton.

    `total: int | Any`
    :   The type of the None singleton.

    `total_discount_amounts: list[airbyte_agent_sdk.connectors.stripe.models.InvoiceTotalDiscountAmountsItem] | Any | None`
    :   The type of the None singleton.

    `total_excluding_tax: int | Any | None`
    :   The type of the None singleton.

    `total_pretax_credit_amounts: list[airbyte_agent_sdk.connectors.stripe.models.InvoiceTotalPretaxCreditAmountsItem] | Any | None`
    :   The type of the None singleton.

    `total_tax_amounts: list[airbyte_agent_sdk.connectors.stripe.models.InvoiceTotalTaxAmountsItem] | Any | None`
    :   The type of the None singleton.

    `total_taxes: list[airbyte_agent_sdk.connectors.stripe.models.InvoiceTotalTaxesItem] | Any | None`
    :   The type of the None singleton.

    `transfer_data: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `webhooks_delivered_at: int | Any | None`
    :   The type of the None singleton.

<a id="InvoiceAutomaticTax"></a>

`InvoiceAutomaticTax(**data: Any)`
:   Settings and latest results for automatic tax lookup for this invoice
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `disabled_reason: str | Any | None`
    :   If Stripe disabled automatic tax, this enum describes why

    `enabled: bool | Any`
    :   Whether Stripe automatically computes tax on this invoice

    `liability: airbyte_agent_sdk.connectors.stripe.models.InvoiceAutomaticTaxLiability | Any | None`
    :   The account that's liable for tax

    `model_config`
    :   The type of the None singleton.

    `provider: str | Any | None`
    :   The tax provider powering automatic tax

    `status: str | Any | None`
    :   The status of the most recent automated tax calculation for this invoice

<a id="InvoiceAutomaticTaxLiability"></a>

`InvoiceAutomaticTaxLiability(**data: Any)`
:   The account that's liable for tax
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: str | Any | None`
    :   The connected account being referenced when type is account

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Type of the account referenced

<a id="InvoiceConfirmationSecret"></a>

`InvoiceConfirmationSecret(**data: Any)`
:   The confirmation secret associated with this invoice
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_secret: str | Any`
    :   The client_secret of the payment that Stripe creates for the invoice after finalization

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of client_secret

<a id="InvoiceCustomFieldsItem"></a>

`InvoiceCustomFieldsItem(**data: Any)`
:   Nested schema for Invoice.custom_fields_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The name of the custom field

    `value: str | Any`
    :   The value of the custom field

<a id="InvoiceCustomerAddress"></a>

`InvoiceCustomerAddress(**data: Any)`
:   The customer's address
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `city: str | Any | None`
    :   City, district, suburb, town, or village

    `country: str | Any | None`
    :   Two-letter country code (ISO 3166-1 alpha-2)

    `line1: str | Any | None`
    :   Address line 1

    `line2: str | Any | None`
    :   Address line 2

    `model_config`
    :   The type of the None singleton.

    `postal_code: str | Any | None`
    :   ZIP or postal code

    `state: str | Any | None`
    :   State, county, province, or region

<a id="InvoiceCustomerShipping"></a>

`InvoiceCustomerShipping(**data: Any)`
:   The customer's shipping information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: airbyte_agent_sdk.connectors.stripe.models.InvoiceCustomerShippingAddress | Any`
    :   Customer shipping address

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Customer name

    `phone: str | Any | None`
    :   Customer phone (including extension)

<a id="InvoiceCustomerShippingAddress"></a>

`InvoiceCustomerShippingAddress(**data: Any)`
:   Customer shipping address
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `city: str | Any | None`
    :   City, district, suburb, town, or village

    `country: str | Any | None`
    :   Two-letter country code (ISO 3166-1 alpha-2)

    `line1: str | Any | None`
    :   Address line 1

    `line2: str | Any | None`
    :   Address line 2

    `model_config`
    :   The type of the None singleton.

    `postal_code: str | Any | None`
    :   ZIP or postal code

    `state: str | Any | None`
    :   State, county, province, or region

<a id="InvoiceCustomerTaxIdsItem"></a>

`InvoiceCustomerTaxIdsItem(**data: Any)`
:   Nested schema for Invoice.customer_tax_ids_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the tax ID

    `value: str | Any | None`
    :   The value of the tax ID

<a id="InvoiceDefaultTaxRatesItem"></a>

`InvoiceDefaultTaxRatesItem(**data: Any)`
:   Nested schema for Invoice.default_tax_rates_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | Any`
    :   Defaults to true

    `country: str | Any | None`
    :   Two-letter country code (ISO 3166-1 alpha-2)

    `created: int | Any`
    :   Time at which the object was created

    `description: str | Any | None`
    :   An arbitrary string attached to the tax rate for your internal use only

    `display_name: str | Any`
    :   The display name of the tax rate

    `effective_percentage: float | Any | None`
    :   Actual/effective tax rate percentage out of 100

    `flat_amount: airbyte_agent_sdk.connectors.stripe.models.InvoiceDefaultTaxRatesItemFlatAmount | Any | None`
    :   The amount of the tax rate when the rate_type is flat_amount

    `id: str | Any`
    :   Unique identifier for the object

    `inclusive: bool | Any`
    :   This specifies if the tax rate is inclusive or exclusive

    `jurisdiction: str | Any | None`
    :   The jurisdiction for the tax rate

    `jurisdiction_level: str | Any | None`
    :   The level of the jurisdiction that imposes this tax rate

    `livemode: bool | Any`
    :   Has the value true if the object exists in live mode

    `metadata: dict[str, str] | Any | None`
    :   Set of key-value pairs

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   String representing the object's type

    `percentage: float | Any`
    :   Tax rate percentage out of 100

    `rate_type: str | Any | None`
    :   Indicates the type of tax rate applied to the taxable amount

    `state: str | Any | None`
    :   ISO 3166-2 subdivision code

    `tax_type: str | Any | None`
    :   The high-level tax type

<a id="InvoiceDefaultTaxRatesItemFlatAmount"></a>

`InvoiceDefaultTaxRatesItemFlatAmount(**data: Any)`
:   The amount of the tax rate when the rate_type is flat_amount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   Amount of the tax when the rate_type is flat_amount

    `currency: str | Any`
    :   Three-letter ISO currency code

    `model_config`
    :   The type of the None singleton.

<a id="InvoiceDiscount"></a>

`InvoiceDiscount(**data: Any)`
:   The discount applied to the invoice
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `checkout_session: str | Any | None`
    :   The type of the None singleton.

    `coupon: airbyte_agent_sdk.connectors.stripe.models.InvoiceDiscountCoupon | Any | None`
    :   The type of the None singleton.

    `customer: str | Any`
    :   The type of the None singleton.

    `customer_account: str | Any | None`
    :   The type of the None singleton.

    `end: int | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `invoice: str | Any | None`
    :   The type of the None singleton.

    `invoice_item: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `promotion_code: str | Any | None`
    :   The type of the None singleton.

    `start: int | Any`
    :   The type of the None singleton.

    `subscription: str | Any | None`
    :   The type of the None singleton.

    `subscription_item: str | Any | None`
    :   The type of the None singleton.

<a id="InvoiceDiscountCoupon"></a>

`InvoiceDiscountCoupon(**data: Any)`
:   Nested schema for InvoiceDiscount.coupon
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount_off: int | Any | None`
    :   The type of the None singleton.

    `created: int | Any`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `duration: str | Any`
    :   The type of the None singleton.

    `duration_in_months: int | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `livemode: bool | Any`
    :   The type of the None singleton.

    `max_redemptions: int | Any | None`
    :   The type of the None singleton.

    `metadata: dict[str, str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `percent_off: float | Any | None`
    :   The type of the None singleton.

    `redeem_by: int | Any | None`
    :   The type of the None singleton.

    `times_redeemed: int | Any`
    :   The type of the None singleton.

    `valid: bool | Any`
    :   The type of the None singleton.

<a id="InvoiceFromInvoice"></a>

`InvoiceFromInvoice(**data: Any)`
:   Details of the invoice that was cloned
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action: str | Any`
    :   The type of the None singleton.

    `invoice: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="InvoiceIssuer"></a>

`InvoiceIssuer(**data: Any)`
:   The connected account that issues the invoice
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: str | Any | None`
    :   The connected account being referenced when type is account

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Type of the account referenced

<a id="InvoiceLastFinalizationError"></a>

`InvoiceLastFinalizationError(**data: Any)`
:   The error encountered during the last finalization attempt
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `advice_code: str | Any | None`
    :   For card errors resulting from a card issuer decline

    `code: str | Any | None`
    :   For some errors that could be handled programmatically, a short string indicating the error code

    `doc_url: str | Any | None`
    :   A URL to more information about the error code reported

    `message: str | Any | None`
    :   A human-readable message providing more details about the error

    `model_config`
    :   The type of the None singleton.

    `network_advice_code: str | Any | None`
    :   For card errors resulting from a card issuer decline

    `network_decline_code: str | Any | None`
    :   For payments declined by the network

    `param: str | Any | None`
    :   If the error is parameter-specific, the parameter related to the error

    `payment_method_type: str | Any | None`
    :   If the error is specific to the type of payment method

    `type_: str | Any`
    :   The type of error returned

<a id="InvoiceLines"></a>

`InvoiceLines(**data: Any)`
:   The individual line items that make up the invoice
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.InvoiceLinesDataItem] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `total_count: int | Any | None`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="InvoiceLinesDataItem"></a>

`InvoiceLinesDataItem(**data: Any)`
:   Nested schema for InvoiceLines.data_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   The amount in cents

    `currency: str | Any`
    :   Three-letter ISO currency code

    `description: str | Any | None`
    :   An arbitrary string attached to the object

    `discount_amounts: list[airbyte_agent_sdk.connectors.stripe.models.InvoiceLinesDataItemDiscountAmountsItem] | Any | None`
    :   The amount of discount calculated per discount for this line item

    `discountable: bool | Any`
    :   If true, discounts will apply to this line item

    `discounts: list[str] | Any`
    :   The discounts applied to the invoice line item

    `id: str | Any`
    :   Unique identifier for the object

    `invoice: str | Any | None`
    :   The ID of the invoice that contains this line item

    `livemode: bool | Any`
    :   Has the value true if the object exists in live mode

    `metadata: dict[str, str] | Any`
    :   Set of key-value pairs

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   String representing the object's type

    `period: airbyte_agent_sdk.connectors.stripe.models.InvoiceLinesDataItemPeriod | Any`
    :   The period this line_item covers

    `proration: bool | Any`
    :   Whether this is a proration

    `quantity: int | Any | None`
    :   The quantity of the subscription

<a id="InvoiceLinesDataItemDiscountAmountsItem"></a>

`InvoiceLinesDataItemDiscountAmountsItem(**data: Any)`
:   Nested schema for InvoiceLinesDataItem.discount_amounts_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   The amount of the discount

    `discount: str | Any`
    :   The discount that was applied

    `model_config`
    :   The type of the None singleton.

<a id="InvoiceLinesDataItemPeriod"></a>

`InvoiceLinesDataItemPeriod(**data: Any)`
:   The period this line_item covers
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end: int | Any`
    :   The end of the period

    `model_config`
    :   The type of the None singleton.

    `start: int | Any`
    :   The start of the period

<a id="InvoiceList"></a>

`InvoiceList(**data: Any)`
:   InvoiceList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.Invoice] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="InvoiceParent"></a>

`InvoiceParent(**data: Any)`
:   The parent that generated this invoice
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `quote_details: airbyte_agent_sdk.connectors.stripe.models.InvoiceParentQuoteDetails | Any | None`
    :   Details about the quote that generated this invoice

    `subscription_details: airbyte_agent_sdk.connectors.stripe.models.InvoiceParentSubscriptionDetails | Any | None`
    :   Details about the subscription that generated this invoice

    `type_: str | Any`
    :   The type of parent that generated this invoice

<a id="InvoiceParentQuoteDetails"></a>

`InvoiceParentQuoteDetails(**data: Any)`
:   Details about the quote that generated this invoice
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `quote: str | Any`
    :   The quote that generated this invoice

<a id="InvoiceParentSubscriptionDetails"></a>

`InvoiceParentSubscriptionDetails(**data: Any)`
:   Details about the subscription that generated this invoice
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `metadata: dict[str, str] | Any | None`
    :   Set of key-value pairs defined as subscription metadata

    `model_config`
    :   The type of the None singleton.

    `subscription: str | Any`
    :   The subscription that generated this invoice

    `subscription_proration_date: int | Any | None`
    :   Only set for upcoming invoices that preview prorations

<a id="InvoicePaymentSettings"></a>

`InvoicePaymentSettings(**data: Any)`
:   Configuration settings for the PaymentIntent that is generated when the invoice is finalized
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `default_mandate: str | Any | None`
    :   ID of the mandate to be used for this invoice

    `model_config`
    :   The type of the None singleton.

    `payment_method_options: dict[str, typing.Any] | Any | None`
    :   Payment-method-specific configuration to provide to the invoice's PaymentIntent

    `payment_method_types: list[str] | Any | None`
    :   The list of payment method types to provide to the invoice's PaymentIntent

<a id="InvoicePayments"></a>

`InvoicePayments(**data: Any)`
:   Payments for this invoice
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.InvoicePaymentsDataItem] | Any`
    :   Details about each payment

    `has_more: bool | Any`
    :   True if this list has another page of items

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   String representing the object's type

    `url: str | Any`
    :   The URL where this list can be accessed

<a id="InvoicePaymentsDataItem"></a>

`InvoicePaymentsDataItem(**data: Any)`
:   Nested schema for InvoicePayments.data_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount_paid: int | Any | None`
    :   Amount that was actually paid for this invoice

    `amount_requested: int | Any`
    :   Amount intended to be paid toward this invoice

    `created: int | Any`
    :   Time at which the object was created

    `currency: str | Any`
    :   Three-letter ISO currency code

    `id: str | Any`
    :   Unique identifier for the object

    `invoice: str | Any`
    :   The invoice that was paid

    `is_default: bool | Any`
    :   Whether this is the default payment created when the invoice was finalized

    `livemode: bool | Any`
    :   Has the value true if the object exists in live mode

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   String representing the object's type

    `status: str | Any`
    :   The status of the payment

<a id="InvoiceRendering"></a>

`InvoiceRendering(**data: Any)`
:   The rendering-related settings that control how the invoice is displayed
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount_tax_display: str | Any | None`
    :   How line-item prices and amounts will be displayed with respect to tax

    `model_config`
    :   The type of the None singleton.

    `pdf: airbyte_agent_sdk.connectors.stripe.models.InvoiceRenderingPdf | Any | None`
    :   Invoice pdf rendering options

    `template: str | Any | None`
    :   ID of the rendering template that the invoice is formatted by

    `template_version: int | Any | None`
    :   Version of the rendering template that the invoice is using

<a id="InvoiceRenderingPdf"></a>

`InvoiceRenderingPdf(**data: Any)`
:   Invoice pdf rendering options
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_size: str | Any | None`
    :   Page size of invoice pdf

<a id="InvoiceSearchResult"></a>

`InvoiceSearchResult(**data: Any)`
:   InvoiceSearchResult type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.Invoice] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="InvoiceShippingCost"></a>

`InvoiceShippingCost(**data: Any)`
:   The details of the cost of shipping
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount_subtotal: int | Any`
    :   Total shipping cost before any taxes are applied

    `amount_tax: int | Any`
    :   Total tax amount applied due to shipping costs

    `amount_total: int | Any`
    :   Total shipping cost after taxes are applied

    `model_config`
    :   The type of the None singleton.

    `shipping_rate: str | Any | None`
    :   The ID of the ShippingRate for this invoice

    `taxes: list[airbyte_agent_sdk.connectors.stripe.models.InvoiceShippingCostTaxesItem] | Any | None`
    :   The taxes applied to the shipping rate

<a id="InvoiceShippingCostTaxesItem"></a>

`InvoiceShippingCostTaxesItem(**data: Any)`
:   Nested schema for InvoiceShippingCost.taxes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   Amount of tax applied for this rate

    `model_config`
    :   The type of the None singleton.

    `taxability_reason: str | Any | None`
    :   The reasoning behind this tax

    `taxable_amount: int | Any | None`
    :   The amount on which tax is calculated

<a id="InvoiceShippingDetails"></a>

`InvoiceShippingDetails(**data: Any)`
:   Shipping details for the invoice
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: airbyte_agent_sdk.connectors.stripe.models.InvoiceShippingDetailsAddress | Any`
    :   Shipping address

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Recipient name

    `phone: str | Any | None`
    :   Recipient phone

<a id="InvoiceShippingDetailsAddress"></a>

`InvoiceShippingDetailsAddress(**data: Any)`
:   Shipping address
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `city: str | Any | None`
    :   City, district, suburb, town, or village

    `country: str | Any | None`
    :   Two-letter country code (ISO 3166-1 alpha-2)

    `line1: str | Any | None`
    :   Address line 1

    `line2: str | Any | None`
    :   Address line 2

    `model_config`
    :   The type of the None singleton.

    `postal_code: str | Any | None`
    :   ZIP or postal code

    `state: str | Any | None`
    :   State, county, province, or region

<a id="InvoiceStatusTransitions"></a>

`InvoiceStatusTransitions(**data: Any)`
:   Status transition timestamps
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `finalized_at: int | Any | None`
    :   The time that the invoice draft was finalized

    `marked_uncollectible_at: int | Any | None`
    :   The time that the invoice was marked uncollectible

    `model_config`
    :   The type of the None singleton.

    `paid_at: int | Any | None`
    :   The time that the invoice was paid

    `voided_at: int | Any | None`
    :   The time that the invoice was voided

<a id="InvoiceSubscriptionDetails"></a>

`InvoiceSubscriptionDetails(**data: Any)`
:   Details about the subscription that this invoice was prepared for, if any
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `metadata: dict[str, str] | Any | None`
    :   Set of key-value pairs defined as subscription metadata when the invoice is created

    `model_config`
    :   The type of the None singleton.

<a id="InvoiceThresholdReason"></a>

`InvoiceThresholdReason(**data: Any)`
:   If billing_reason is set to subscription_threshold this returns more information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount_gte: int | Any | None`
    :   The total invoice amount threshold boundary if it triggered the threshold invoice

    `item_reasons: list[airbyte_agent_sdk.connectors.stripe.models.InvoiceThresholdReasonItemReasonsItem] | Any`
    :   Indicates which line items triggered a threshold invoice

    `model_config`
    :   The type of the None singleton.

<a id="InvoiceThresholdReasonItemReasonsItem"></a>

`InvoiceThresholdReasonItemReasonsItem(**data: Any)`
:   Nested schema for InvoiceThresholdReason.item_reasons_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `line_item_ids: list[str] | Any`
    :   The IDs of the line items that triggered the threshold invoice

    `model_config`
    :   The type of the None singleton.

    `usage_gte: int | Any`
    :   The quantity threshold boundary that applied to the given line item

<a id="InvoiceTotalDiscountAmountsItem"></a>

`InvoiceTotalDiscountAmountsItem(**data: Any)`
:   Nested schema for Invoice.total_discount_amounts_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   The amount of the discount

    `discount: str | Any`
    :   The discount that was applied

    `model_config`
    :   The type of the None singleton.

<a id="InvoiceTotalPretaxCreditAmountsItem"></a>

`InvoiceTotalPretaxCreditAmountsItem(**data: Any)`
:   Nested schema for Invoice.total_pretax_credit_amounts_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   The amount of the pretax credit amount

    `credit_balance_transaction: str | Any | None`
    :   The credit balance transaction that was applied

    `discount: str | Any | None`
    :   The discount that was applied

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Type of the pretax credit amount referenced

<a id="InvoiceTotalTaxAmountsItem"></a>

`InvoiceTotalTaxAmountsItem(**data: Any)`
:   Nested schema for Invoice.total_tax_amounts_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   The amount of the tax

    `inclusive: bool | Any`
    :   Whether the tax amount is included in the line item amount

    `model_config`
    :   The type of the None singleton.

    `tax_rate: str | Any`
    :   The tax rate applied

    `taxability_reason: str | Any | None`
    :   The reasoning behind the tax

    `taxable_amount: int | Any`
    :   The amount on which tax is calculated

<a id="InvoiceTotalTaxesItem"></a>

`InvoiceTotalTaxesItem(**data: Any)`
:   Nested schema for Invoice.total_taxes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   The amount of the tax

    `model_config`
    :   The type of the None singleton.

    `tax_behavior: str | Any`
    :   Whether this tax is inclusive or exclusive

    `tax_rate_details: dict[str, typing.Any] | Any | None`
    :   Additional details about the tax rate

    `taxability_reason: str | Any`
    :   The reasoning behind this tax

    `taxable_amount: int | Any | None`
    :   The amount on which tax is calculated

    `type_: str | Any`
    :   The type of tax information

<a id="InvoicesListResultMeta"></a>

`InvoicesListResultMeta(**data: Any)`
:   Metadata for invoices.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="InvoicesSearchData"></a>

`InvoicesSearchData(**data: Any)`
:   Search result data for invoices entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_country: str | None`
    :   The country of the business associated with this invoice, commonly used to display localized content.

    `account_name: str | None`
    :   The public name of the business associated with this invoice.

    `account_tax_ids: list[typing.Any] | None`
    :   Tax IDs of the account associated with this invoice.

    `amount_due: int | None`
    :   Total amount, in smallest currency unit, that is due and owed by the customer.

    `amount_paid: int | None`
    :   Total amount, in smallest currency unit, that has been paid by the customer.

    `amount_remaining: int | None`
    :   The difference between amount_due and amount_paid, representing the outstanding balance.

    `amount_shipping: int | None`
    :   Total amount of shipping costs on the invoice.

    `application: str | None`
    :   ID of the Connect application that created this invoice.

    `application_fee: int | None`
    :   Amount of application fee charged for this invoice in a Connect scenario.

    `application_fee_amount: int | None`
    :   The fee in smallest currency unit that is collected by the application in a Connect scenario.

    `attempt_count: int | None`
    :   Number of payment attempts made for this invoice.

    `attempted: bool | None`
    :   Whether an attempt has been made to pay the invoice.

    `auto_advance: bool | None`
    :   Controls whether Stripe performs automatic collection of the invoice.

    `automatic_tax: dict[str, typing.Any] | None`
    :   Settings and status for automatic tax calculation on this invoice.

    `billing: str | None`
    :   Billing method used for the invoice (charge_automatically or send_invoice).

    `billing_reason: str | None`
    :   Indicates the reason why the invoice was created (subscription_cycle, manual, etc.).

    `charge: str | None`
    :   ID of the latest charge generated for this invoice, if any.

    `closed: bool | None`
    :   Whether the invoice has been marked as closed and no longer open for collection.

    `collection_method: str | None`
    :   Method by which the invoice is collected: charge_automatically or send_invoice.

    `created: int | None`
    :   Timestamp indicating when the invoice was created.

    `currency: str | None`
    :   Three-letter ISO currency code in which the invoice is denominated.

    `custom_fields: list[typing.Any] | None`
    :   Custom fields displayed on the invoice as specified by the account.

    `customer: str | None`
    :   The customer object or ID associated with this invoice.

    `customer_address: dict[str, typing.Any] | None`
    :   The customer's address at the time the invoice was finalized.

    `customer_email: str | None`
    :   The customer's email address at the time the invoice was finalized.

    `customer_name: str | None`
    :   The customer's name at the time the invoice was finalized.

    `customer_phone: str | None`
    :   The customer's phone number at the time the invoice was finalized.

    `customer_shipping: dict[str, typing.Any] | None`
    :   The customer's shipping information at the time the invoice was finalized.

    `customer_tax_exempt: str | None`
    :   The customer's tax exempt status at the time the invoice was finalized.

    `customer_tax_ids: list[typing.Any] | None`
    :   The customer's tax IDs at the time the invoice was finalized.

    `default_payment_method: str | None`
    :   Default payment method for the invoice, used if no other method is specified.

    `default_source: str | None`
    :   Default payment source for the invoice if no payment method is set.

    `default_tax_rates: list[typing.Any] | None`
    :   The tax rates applied to the invoice by default.

    `description: str | None`
    :   An arbitrary string attached to the invoice, often displayed to customers.

    `discount: dict[str, typing.Any] | None`
    :   The discount object applied to the invoice, if any.

    `discounts: list[typing.Any] | None`
    :   Array of discount IDs or objects currently applied to this invoice.

    `due_date: float | None`
    :   The date by which payment on this invoice is due, if the invoice is not auto-collected.

    `effective_at: int | None`
    :   Timestamp when the invoice becomes effective and finalized for payment.

    `ending_balance: int | None`
    :   The customer's ending account balance after this invoice is finalized.

    `footer: str | None`
    :   Footer text displayed on the invoice.

    `forgiven: bool | None`
    :   Whether the invoice has been forgiven and is considered paid without actual payment.

    `from_invoice: dict[str, typing.Any] | None`
    :   Details about the invoice this invoice was created from, if applicable.

    `hosted_invoice_url: str | None`
    :   URL for the hosted invoice page where customers can view and pay the invoice.

    `id: str | None`
    :   Unique identifier for the invoice object.

    `invoice_pdf: str | None`
    :   URL for the PDF version of the invoice.

    `is_deleted: bool | None`
    :   Indicates whether this invoice has been deleted.

    `issuer: dict[str, typing.Any] | None`
    :   Details about the entity issuing the invoice.

    `last_finalization_error: dict[str, typing.Any] | None`
    :   The error encountered during the last finalization attempt, if any.

    `latest_revision: str | None`
    :   The latest revision of the invoice, if revisions are enabled.

    `lines: dict[str, typing.Any] | None`
    :   The individual line items that make up the invoice, representing products, services, or fees.

    `livemode: bool | None`
    :   Indicates whether the invoice exists in live mode (true) or test mode (false).

    `metadata: dict[str, typing.Any] | None`
    :   Key-value pairs for storing additional structured information about the invoice.

    `model_config`
    :   The type of the None singleton.

    `next_payment_attempt: float | None`
    :   Timestamp of the next automatic payment attempt for this invoice, if applicable.

    `number: str | None`
    :   A unique, human-readable identifier for this invoice, often shown to customers.

    `object_: str | None`
    :   String representing the object type, always 'invoice'.

    `on_behalf_of: str | None`
    :   The account on behalf of which the invoice is being created, used in Connect scenarios.

    `paid: bool | None`
    :   Whether the invoice has been paid in full.

    `paid_out_of_band: bool | None`
    :   Whether payment was made outside of Stripe and manually marked as paid.

    `payment: str | None`
    :   ID of the payment associated with this invoice, if any.

    `payment_intent: str | None`
    :   The PaymentIntent associated with this invoice for processing payment.

    `payment_settings: dict[str, typing.Any] | None`
    :   Configuration settings for how payment should be collected on this invoice.

    `period_end: float | None`
    :   End date of the billing period covered by this invoice.

    `period_start: float | None`
    :   Start date of the billing period covered by this invoice.

    `post_payment_credit_notes_amount: int | None`
    :   Total amount of credit notes issued after the invoice was paid.

    `pre_payment_credit_notes_amount: int | None`
    :   Total amount of credit notes applied before payment was attempted.

    `quote: str | None`
    :   The quote from which this invoice was generated, if applicable.

    `receipt_number: str | None`
    :   The receipt number displayed on the invoice, if available.

    `rendering: dict[str, typing.Any] | None`
    :   Settings that control how the invoice is rendered for display.

    `rendering_options: dict[str, typing.Any] | None`
    :   Options for customizing the visual rendering of the invoice.

    `shipping_cost: dict[str, typing.Any] | None`
    :   Total cost of shipping charges included in the invoice.

    `shipping_details: dict[str, typing.Any] | None`
    :   Detailed shipping information for the invoice, including address and carrier.

    `starting_balance: int | None`
    :   The customer's starting account balance at the beginning of the billing period.

    `statement_description: str | None`
    :   Extra information about the invoice that appears on the customer's credit card statement.

    `statement_descriptor: str | None`
    :   A dynamic descriptor that appears on the customer's credit card statement for this invoice.

    `status: str | None`
    :   The status of the invoice: draft, open, paid, void, or uncollectible.

    `status_transitions: dict[str, typing.Any]`
    :   Timestamps tracking when the invoice transitioned between different statuses.

    `subscription: str | None`
    :   The subscription this invoice was generated for, if applicable.

    `subscription_details: dict[str, typing.Any] | None`
    :   Additional details about the subscription associated with this invoice.

    `subtotal: int | None`
    :   Total of all line items before discounts or tax are applied.

    `subtotal_excluding_tax: int | None`
    :   The subtotal amount excluding any tax calculations.

    `tax: int | None`
    :   Total tax amount applied to the invoice.

    `tax_percent: float | None`
    :   The percentage of tax applied to the invoice (deprecated, use total_tax_amounts instead).

    `test_clock: str | None`
    :   ID of the test clock this invoice belongs to, used for testing time-dependent billing.

    `total: int | None`
    :   Total amount of the invoice after all line items, discounts, and taxes are calculated.

    `total_discount_amounts: list[typing.Any] | None`
    :   Array of the total discount amounts applied, broken down by discount.

    `total_excluding_tax: int | None`
    :   Total amount of the invoice excluding all tax calculations.

    `total_tax_amounts: list[typing.Any] | None`
    :   Array of tax amounts applied to the invoice, broken down by tax rate.

    `transfer_data: dict[str, typing.Any] | None`
    :   Information about the transfer of funds associated with this invoice in Connect scenarios.

    `updated: int | None`
    :   Timestamp indicating when the invoice was last updated.

    `webhooks_delivered_at: float | None`
    :   Timestamp indicating when webhooks for this invoice were successfully delivered.

<a id="PaymentIntent"></a>

`PaymentIntent(**data: Any)`
:   PaymentIntent type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   The type of the None singleton.

    `amount_capturable: int | Any`
    :   The type of the None singleton.

    `amount_received: int | Any`
    :   The type of the None singleton.

    `application: str | Any | None`
    :   The type of the None singleton.

    `application_fee_amount: int | Any | None`
    :   The type of the None singleton.

    `capture_method: str | Any`
    :   The type of the None singleton.

    `client_secret: str | Any | None`
    :   The type of the None singleton.

    `confirmation_method: str | Any`
    :   The type of the None singleton.

    `created: int | Any`
    :   The type of the None singleton.

    `currency: str | Any`
    :   The type of the None singleton.

    `customer: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `livemode: bool | Any`
    :   The type of the None singleton.

    `metadata: dict[str, str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `payment_method: str | Any | None`
    :   The type of the None singleton.

    `payment_method_types: list[str] | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

<a id="PaymentIntentList"></a>

`PaymentIntentList(**data: Any)`
:   PaymentIntentList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.PaymentIntent] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="PaymentIntentSearchResult"></a>

`PaymentIntentSearchResult(**data: Any)`
:   PaymentIntentSearchResult type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.PaymentIntent] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="PaymentIntentsApiSearchResultMeta"></a>

`PaymentIntentsApiSearchResultMeta(**data: Any)`
:   Metadata for payment_intents.Action.API_SEARCH operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="PaymentIntentsListResultMeta"></a>

`PaymentIntentsListResultMeta(**data: Any)`
:   Metadata for payment_intents.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Payout"></a>

`Payout(**data: Any)`
:   Payout type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   The type of the None singleton.

    `application_fee: str | Any | None`
    :   The type of the None singleton.

    `application_fee_amount: int | Any | None`
    :   The type of the None singleton.

    `arrival_date: int | Any`
    :   The type of the None singleton.

    `automatic: bool | Any`
    :   The type of the None singleton.

    `balance_transaction: str | Any | None`
    :   The type of the None singleton.

    `created: int | Any`
    :   The type of the None singleton.

    `currency: str | Any`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `destination: str | Any | None`
    :   The type of the None singleton.

    `failure_balance_transaction: str | Any | None`
    :   The type of the None singleton.

    `failure_code: str | Any | None`
    :   The type of the None singleton.

    `failure_message: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `livemode: bool | Any`
    :   The type of the None singleton.

    `metadata: dict[str, str] | Any`
    :   The type of the None singleton.

    `method: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `original_payout: str | Any | None`
    :   The type of the None singleton.

    `payout_method: str | Any | None`
    :   The type of the None singleton.

    `reconciliation_status: str | Any`
    :   The type of the None singleton.

    `reversed_by: str | Any | None`
    :   The type of the None singleton.

    `source_balance: str | Any | None`
    :   The type of the None singleton.

    `source_type: str | Any`
    :   The type of the None singleton.

    `statement_descriptor: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `trace_id: airbyte_agent_sdk.connectors.stripe.models.PayoutTraceId | Any | None`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

<a id="PayoutList"></a>

`PayoutList(**data: Any)`
:   PayoutList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.Payout] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="PayoutTraceId"></a>

`PayoutTraceId(**data: Any)`
:   A string that identifies this payout as part of a group
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `status: str | Any`
    :   The status of the trace ID

    `value: str | Any | None`
    :   The trace ID value

<a id="PayoutsListResultMeta"></a>

`PayoutsListResultMeta(**data: Any)`
:   Metadata for payouts.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Product"></a>

`Product(**data: Any)`
:   Product type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | Any`
    :   The type of the None singleton.

    `attributes: list[str] | Any`
    :   The type of the None singleton.

    `created: int | Any`
    :   The type of the None singleton.

    `default_price: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `features: list[airbyte_agent_sdk.connectors.stripe.models.ProductFeaturesItem] | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `images: list[str] | Any`
    :   The type of the None singleton.

    `livemode: bool | Any`
    :   The type of the None singleton.

    `marketing_features: list[airbyte_agent_sdk.connectors.stripe.models.ProductMarketingFeaturesItem] | Any`
    :   The type of the None singleton.

    `metadata: dict[str, str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `package_dimensions: airbyte_agent_sdk.connectors.stripe.models.ProductPackageDimensions | Any | None`
    :   The type of the None singleton.

    `shippable: bool | Any | None`
    :   The type of the None singleton.

    `statement_descriptor: str | Any | None`
    :   The type of the None singleton.

    `tax_code: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `unit_label: str | Any | None`
    :   The type of the None singleton.

    `updated: int | Any`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="ProductCreateParams"></a>

`ProductCreateParams(**data: Any)`
:   ProductCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | Any`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `images: list[str] | Any`
    :   The type of the None singleton.

    `marketing_features: list[airbyte_agent_sdk.connectors.stripe.models.ProductCreateParamsMarketingFeaturesItem] | Any`
    :   The type of the None singleton.

    `metadata: dict[str, str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `package_dimensions: airbyte_agent_sdk.connectors.stripe.models.ProductCreateParamsPackageDimensions | Any`
    :   The type of the None singleton.

    `shippable: bool | Any`
    :   The type of the None singleton.

    `statement_descriptor: str | Any`
    :   The type of the None singleton.

    `tax_code: str | Any`
    :   The type of the None singleton.

    `unit_label: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="ProductCreateParamsMarketingFeaturesItem"></a>

`ProductCreateParamsMarketingFeaturesItem(**data: Any)`
:   Nested schema for ProductCreateParams.marketing_features_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The marketing feature name. Up to 80 characters long

<a id="ProductCreateParamsPackageDimensions"></a>

`ProductCreateParamsPackageDimensions(**data: Any)`
:   The dimensions of this product for shipping purposes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `height: float | Any`
    :   Height, in inches

    `length: float | Any`
    :   Length, in inches

    `model_config`
    :   The type of the None singleton.

    `weight: float | Any`
    :   Weight, in ounces

    `width: float | Any`
    :   Width, in inches

<a id="ProductDeletedResponse"></a>

`ProductDeletedResponse(**data: Any)`
:   ProductDeletedResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `deleted: bool | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

<a id="ProductFeaturesItem"></a>

`ProductFeaturesItem(**data: Any)`
:   Nested schema for Product.features_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The feature name

<a id="ProductList"></a>

`ProductList(**data: Any)`
:   ProductList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.Product] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="ProductMarketingFeaturesItem"></a>

`ProductMarketingFeaturesItem(**data: Any)`
:   Nested schema for Product.marketing_features_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The marketing feature name. Up to 80 characters long

<a id="ProductPackageDimensions"></a>

`ProductPackageDimensions(**data: Any)`
:   The dimensions of this product for shipping purposes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `height: float | Any`
    :   Height, in inches

    `length: float | Any`
    :   Length, in inches

    `model_config`
    :   The type of the None singleton.

    `weight: float | Any`
    :   Weight, in ounces

    `width: float | Any`
    :   Width, in inches

<a id="ProductSearchResult"></a>

`ProductSearchResult(**data: Any)`
:   ProductSearchResult type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.Product] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="ProductUpdateParams"></a>

`ProductUpdateParams(**data: Any)`
:   ProductUpdateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | Any`
    :   The type of the None singleton.

    `default_price: str | Any`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `images: list[str] | Any`
    :   The type of the None singleton.

    `marketing_features: list[airbyte_agent_sdk.connectors.stripe.models.ProductUpdateParamsMarketingFeaturesItem] | Any`
    :   The type of the None singleton.

    `metadata: dict[str, str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `package_dimensions: airbyte_agent_sdk.connectors.stripe.models.ProductUpdateParamsPackageDimensions | Any`
    :   The type of the None singleton.

    `shippable: bool | Any`
    :   The type of the None singleton.

    `statement_descriptor: str | Any`
    :   The type of the None singleton.

    `tax_code: str | Any`
    :   The type of the None singleton.

    `unit_label: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="ProductUpdateParamsMarketingFeaturesItem"></a>

`ProductUpdateParamsMarketingFeaturesItem(**data: Any)`
:   Nested schema for ProductUpdateParams.marketing_features_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The marketing feature name. Up to 80 characters long

<a id="ProductUpdateParamsPackageDimensions"></a>

`ProductUpdateParamsPackageDimensions(**data: Any)`
:   The dimensions of this product for shipping purposes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `height: float | Any`
    :   Height, in inches

    `length: float | Any`
    :   Length, in inches

    `model_config`
    :   The type of the None singleton.

    `weight: float | Any`
    :   Weight, in ounces

    `width: float | Any`
    :   Width, in inches

<a id="ProductsApiSearchResultMeta"></a>

`ProductsApiSearchResultMeta(**data: Any)`
:   Metadata for products.Action.API_SEARCH operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ProductsListResultMeta"></a>

`ProductsListResultMeta(**data: Any)`
:   Metadata for products.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Refund"></a>

`Refund(**data: Any)`
:   Refund type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   The type of the None singleton.

    `balance_transaction: str | Any | None`
    :   The type of the None singleton.

    `charge: str | Any | None`
    :   The type of the None singleton.

    `created: int | Any`
    :   The type of the None singleton.

    `currency: str | Any`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `destination_details: airbyte_agent_sdk.connectors.stripe.models.RefundDestinationDetails | Any | None`
    :   The type of the None singleton.

    `failure_balance_transaction: str | Any | None`
    :   The type of the None singleton.

    `failure_reason: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `instructions_email: str | Any | None`
    :   The type of the None singleton.

    `metadata: dict[str, str] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_action: airbyte_agent_sdk.connectors.stripe.models.RefundNextAction | Any | None`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `payment_intent: str | Any | None`
    :   The type of the None singleton.

    `pending_reason: str | Any | None`
    :   The type of the None singleton.

    `reason: str | Any | None`
    :   The type of the None singleton.

    `receipt_number: str | Any | None`
    :   The type of the None singleton.

    `source_transfer_reversal: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `transfer_reversal: str | Any | None`
    :   The type of the None singleton.

<a id="RefundCreateParams"></a>

`RefundCreateParams(**data: Any)`
:   RefundCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   The type of the None singleton.

    `charge: str | Any`
    :   The type of the None singleton.

    `metadata: dict[str, str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `payment_intent: str | Any`
    :   The type of the None singleton.

    `reason: str | Any`
    :   The type of the None singleton.

    `refund_application_fee: bool | Any`
    :   The type of the None singleton.

    `reverse_transfer: bool | Any`
    :   The type of the None singleton.

<a id="RefundDestinationDetails"></a>

`RefundDestinationDetails(**data: Any)`
:   Transaction-specific details for the refund
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `affirm: dict[str, typing.Any] | Any | None`
    :   If this is a affirm refund, this hash contains the transaction specific details

    `afterpay_clearpay: dict[str, typing.Any] | Any | None`
    :   If this is a afterpay_clearpay refund, this hash contains the transaction specific details

    `alipay: dict[str, typing.Any] | Any | None`
    :   If this is a alipay refund, this hash contains the transaction specific details

    `alma: dict[str, typing.Any] | Any | None`
    :   If this is a alma refund, this hash contains the transaction specific details

    `amazon_pay: dict[str, typing.Any] | Any | None`
    :   If this is a amazon_pay refund, this hash contains the transaction specific details

    `au_bank_transfer: dict[str, typing.Any] | Any | None`
    :   If this is a au_bank_transfer refund, this hash contains the transaction specific details

    `blik: airbyte_agent_sdk.connectors.stripe.models.RefundDestinationDetailsBlik | Any | None`
    :   If this is a blik refund, this hash contains the transaction specific details

    `br_bank_transfer: airbyte_agent_sdk.connectors.stripe.models.RefundDestinationDetailsBrBankTransfer | Any | None`
    :   If this is a br_bank_transfer refund, this hash contains the transaction specific details

    `card: airbyte_agent_sdk.connectors.stripe.models.RefundDestinationDetailsCard | Any | None`
    :   If this is a card refund, this hash contains the transaction specific details

    `cashapp: dict[str, typing.Any] | Any | None`
    :   If this is a cashapp refund, this hash contains the transaction specific details

    `crypto: airbyte_agent_sdk.connectors.stripe.models.RefundDestinationDetailsCrypto | Any | None`
    :   If this is a crypto refund, this hash contains the transaction specific details

    `customer_cash_balance: dict[str, typing.Any] | Any | None`
    :   If this is a customer_cash_balance refund, this hash contains the transaction specific details

    `eps: dict[str, typing.Any] | Any | None`
    :   If this is a eps refund, this hash contains the transaction specific details

    `eu_bank_transfer: airbyte_agent_sdk.connectors.stripe.models.RefundDestinationDetailsEuBankTransfer | Any | None`
    :   If this is a eu_bank_transfer refund, this hash contains the transaction specific details

    `gb_bank_transfer: airbyte_agent_sdk.connectors.stripe.models.RefundDestinationDetailsGbBankTransfer | Any | None`
    :   If this is a gb_bank_transfer refund, this hash contains the transaction specific details

    `giropay: dict[str, typing.Any] | Any | None`
    :   If this is a giropay refund, this hash contains the transaction specific details

    `grabpay: dict[str, typing.Any] | Any | None`
    :   If this is a grabpay refund, this hash contains the transaction specific details

    `jp_bank_transfer: airbyte_agent_sdk.connectors.stripe.models.RefundDestinationDetailsJpBankTransfer | Any | None`
    :   If this is a jp_bank_transfer refund, this hash contains the transaction specific details

    `klarna: dict[str, typing.Any] | Any | None`
    :   If this is a klarna refund, this hash contains the transaction specific details

    `mb_way: airbyte_agent_sdk.connectors.stripe.models.RefundDestinationDetailsMbWay | Any | None`
    :   If this is a mb_way refund, this hash contains the transaction specific details

    `model_config`
    :   The type of the None singleton.

    `multibanco: airbyte_agent_sdk.connectors.stripe.models.RefundDestinationDetailsMultibanco | Any | None`
    :   If this is a multibanco refund, this hash contains the transaction specific details

    `mx_bank_transfer: airbyte_agent_sdk.connectors.stripe.models.RefundDestinationDetailsMxBankTransfer | Any | None`
    :   If this is a mx_bank_transfer refund, this hash contains the transaction specific details

    `nz_bank_transfer: dict[str, typing.Any] | Any | None`
    :   If this is a nz_bank_transfer refund, this hash contains the transaction specific details

    `p24: airbyte_agent_sdk.connectors.stripe.models.RefundDestinationDetailsP24 | Any | None`
    :   If this is a p24 refund, this hash contains the transaction specific details

    `paynow: dict[str, typing.Any] | Any | None`
    :   If this is a paynow refund, this hash contains the transaction specific details

    `paypal: airbyte_agent_sdk.connectors.stripe.models.RefundDestinationDetailsPaypal | Any | None`
    :   If this is a paypal refund, this hash contains the transaction specific details

    `pix: dict[str, typing.Any] | Any | None`
    :   If this is a pix refund, this hash contains the transaction specific details

    `revolut: dict[str, typing.Any] | Any | None`
    :   If this is a revolut refund, this hash contains the transaction specific details

    `sofort: dict[str, typing.Any] | Any | None`
    :   If this is a sofort refund, this hash contains the transaction specific details

    `swish: airbyte_agent_sdk.connectors.stripe.models.RefundDestinationDetailsSwish | Any | None`
    :   If this is a swish refund, this hash contains the transaction specific details

    `th_bank_transfer: airbyte_agent_sdk.connectors.stripe.models.RefundDestinationDetailsThBankTransfer | Any | None`
    :   If this is a th_bank_transfer refund, this hash contains the transaction specific details

    `twint: dict[str, typing.Any] | Any | None`
    :   If this is a twint refund, this hash contains the transaction specific details

    `type_: str | Any`
    :   The type of transaction-specific details of the payment method used in the refund

    `us_bank_transfer: airbyte_agent_sdk.connectors.stripe.models.RefundDestinationDetailsUsBankTransfer | Any | None`
    :   If this is a us_bank_transfer refund, this hash contains the transaction specific details

    `wechat_pay: dict[str, typing.Any] | Any | None`
    :   If this is a wechat_pay refund, this hash contains the transaction specific details

    `zip: dict[str, typing.Any] | Any | None`
    :   If this is a zip refund, this hash contains the transaction specific details

<a id="RefundDestinationDetailsBlik"></a>

`RefundDestinationDetailsBlik(**data: Any)`
:   If this is a blik refund, this hash contains the transaction specific details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `network_decline_code: str | Any | None`
    :   For refunds declined by the network, a decline code provided by the network

    `reference: str | Any | None`
    :   The reference assigned to the refund

    `reference_status: str | Any | None`
    :   Status of the reference on the refund

<a id="RefundDestinationDetailsBrBankTransfer"></a>

`RefundDestinationDetailsBrBankTransfer(**data: Any)`
:   If this is a br_bank_transfer refund, this hash contains the transaction specific details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `reference: str | Any | None`
    :   The reference assigned to the refund

    `reference_status: str | Any | None`
    :   Status of the reference on the refund

<a id="RefundDestinationDetailsCard"></a>

`RefundDestinationDetailsCard(**data: Any)`
:   If this is a card refund, this hash contains the transaction specific details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `reference: str | Any | None`
    :   Value of the reference number assigned to the refund

    `reference_status: str | Any | None`
    :   Status of the reference number on the refund

    `reference_type: str | Any | None`
    :   Type of the reference number assigned to the refund

    `type_: str | Any`
    :   The type of refund

<a id="RefundDestinationDetailsCrypto"></a>

`RefundDestinationDetailsCrypto(**data: Any)`
:   If this is a crypto refund, this hash contains the transaction specific details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `reference: str | Any | None`
    :   The transaction hash of the refund

<a id="RefundDestinationDetailsEuBankTransfer"></a>

`RefundDestinationDetailsEuBankTransfer(**data: Any)`
:   If this is a eu_bank_transfer refund, this hash contains the transaction specific details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `reference: str | Any | None`
    :   The reference assigned to the refund

    `reference_status: str | Any | None`
    :   Status of the reference on the refund

<a id="RefundDestinationDetailsGbBankTransfer"></a>

`RefundDestinationDetailsGbBankTransfer(**data: Any)`
:   If this is a gb_bank_transfer refund, this hash contains the transaction specific details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `reference: str | Any | None`
    :   The reference assigned to the refund

    `reference_status: str | Any | None`
    :   Status of the reference on the refund

<a id="RefundDestinationDetailsJpBankTransfer"></a>

`RefundDestinationDetailsJpBankTransfer(**data: Any)`
:   If this is a jp_bank_transfer refund, this hash contains the transaction specific details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `reference: str | Any | None`
    :   The reference assigned to the refund

    `reference_status: str | Any | None`
    :   Status of the reference on the refund

<a id="RefundDestinationDetailsMbWay"></a>

`RefundDestinationDetailsMbWay(**data: Any)`
:   If this is a mb_way refund, this hash contains the transaction specific details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `reference: str | Any | None`
    :   The reference assigned to the refund

    `reference_status: str | Any | None`
    :   Status of the reference on the refund

<a id="RefundDestinationDetailsMultibanco"></a>

`RefundDestinationDetailsMultibanco(**data: Any)`
:   If this is a multibanco refund, this hash contains the transaction specific details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `reference: str | Any | None`
    :   The reference assigned to the refund

    `reference_status: str | Any | None`
    :   Status of the reference on the refund

<a id="RefundDestinationDetailsMxBankTransfer"></a>

`RefundDestinationDetailsMxBankTransfer(**data: Any)`
:   If this is a mx_bank_transfer refund, this hash contains the transaction specific details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `reference: str | Any | None`
    :   The reference assigned to the refund

    `reference_status: str | Any | None`
    :   Status of the reference on the refund

<a id="RefundDestinationDetailsP24"></a>

`RefundDestinationDetailsP24(**data: Any)`
:   If this is a p24 refund, this hash contains the transaction specific details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `reference: str | Any | None`
    :   The reference assigned to the refund

    `reference_status: str | Any | None`
    :   Status of the reference on the refund

<a id="RefundDestinationDetailsPaypal"></a>

`RefundDestinationDetailsPaypal(**data: Any)`
:   If this is a paypal refund, this hash contains the transaction specific details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `network_decline_code: str | Any | None`
    :   For refunds declined by the network, a decline code provided by the network

<a id="RefundDestinationDetailsSwish"></a>

`RefundDestinationDetailsSwish(**data: Any)`
:   If this is a swish refund, this hash contains the transaction specific details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `network_decline_code: str | Any | None`
    :   For refunds declined by the network, a decline code provided by the network

    `reference: str | Any | None`
    :   The reference assigned to the refund

    `reference_status: str | Any | None`
    :   Status of the reference on the refund

<a id="RefundDestinationDetailsThBankTransfer"></a>

`RefundDestinationDetailsThBankTransfer(**data: Any)`
:   If this is a th_bank_transfer refund, this hash contains the transaction specific details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `reference: str | Any | None`
    :   The reference assigned to the refund

    `reference_status: str | Any | None`
    :   Status of the reference on the refund

<a id="RefundDestinationDetailsUsBankTransfer"></a>

`RefundDestinationDetailsUsBankTransfer(**data: Any)`
:   If this is a us_bank_transfer refund, this hash contains the transaction specific details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `reference: str | Any | None`
    :   The reference assigned to the refund

    `reference_status: str | Any | None`
    :   Status of the reference on the refund

<a id="RefundList"></a>

`RefundList(**data: Any)`
:   RefundList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `data: list[airbyte_agent_sdk.connectors.stripe.models.Refund] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="RefundNextAction"></a>

`RefundNextAction(**data: Any)`
:   If the refund has a status of requires_action, this property describes what the refund needs to continue processing
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `display_details: airbyte_agent_sdk.connectors.stripe.models.RefundNextActionDisplayDetails | Any | None`
    :   Contains the refund details

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Type of the next action to perform

<a id="RefundNextActionDisplayDetails"></a>

`RefundNextActionDisplayDetails(**data: Any)`
:   Contains the refund details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email_sent: airbyte_agent_sdk.connectors.stripe.models.RefundNextActionDisplayDetailsEmailSent | Any`
    :   Contains information about the email sent to the customer

    `expires_at: int | Any`
    :   The expiry timestamp

    `model_config`
    :   The type of the None singleton.

<a id="RefundNextActionDisplayDetailsEmailSent"></a>

`RefundNextActionDisplayDetailsEmailSent(**data: Any)`
:   Contains information about the email sent to the customer
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email_sent_at: int | Any`
    :   The timestamp when the email was sent

    `email_sent_to: str | Any`
    :   The recipient's email address

    `model_config`
    :   The type of the None singleton.

<a id="RefundsListResultMeta"></a>

`RefundsListResultMeta(**data: Any)`
:   Metadata for refunds.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="RefundsSearchData"></a>

`RefundsSearchData(**data: Any)`
:   Search result data for refunds entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | None`
    :   Amount refunded, in cents (the smallest currency unit).

    `balance_transaction: str | None`
    :   ID of the balance transaction that describes the impact of this refund on your account balance.

    `charge: str | None`
    :   ID of the charge that was refunded.

    `created: int | None`
    :   Timestamp indicating when the refund was created.

    `currency: str | None`
    :   Three-letter ISO currency code in lowercase representing the currency of the refund.

    `destination_details: dict[str, typing.Any] | None`
    :   Details about the destination where the refunded funds should be sent.

    `id: str | None`
    :   Unique identifier for the refund object.

    `metadata: dict[str, typing.Any] | None`
    :   Set of key-value pairs that you can attach to an object for storing additional structured information.

    `model_config`
    :   The type of the None singleton.

    `object_: str | None`
    :   String representing the object type, always 'refund'.

    `payment_intent: str | None`
    :   ID of the PaymentIntent that was refunded.

    `reason: str | None`
    :   Reason for the refund, either user-provided (duplicate, fraudulent, or requested_by_customer) or generated by Stripe internally (expired_uncaptured_charge).

    `receipt_number: str | None`
    :   The transaction number that appears on email receipts sent for this refund.

    `source_transfer_reversal: str | None`
    :   ID of the transfer reversal that was created as a result of refunding a transfer (Connect only).

    `status: str | None`
    :   Status of the refund (pending, requires_action, succeeded, failed, or canceled).

    `transfer_reversal: str | None`
    :   ID of the reversal of the transfer that funded the charge being refunded (Connect only).

    `updated: int | None`
    :   Timestamp indicating when the refund was last updated.

<a id="StripeAuthConfig"></a>

`StripeAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your Stripe API Key (starts with sk_test_ or sk_live_)

    `model_config`
    :   The type of the None singleton.

<a id="StripeCheckResult"></a>

`StripeCheckResult(**data: Any)`
:   Result of a health check operation.
    
    Returned by the check() method to indicate connectivity and credential status.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `checked_action: str | None`
    :   Action name used for the health check.

    `checked_entity: str | None`
    :   Entity name used for the health check.

    `error: str | None`
    :   Error message if status is 'unhealthy', None otherwise.

    `model_config`
    :   The type of the None singleton.

    `status: str`
    :   Health check status: 'healthy' or 'unhealthy'.

<a id="StripeExecuteResult"></a>

`StripeExecuteResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult[ChargeSearchResult]
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult[InvoiceSearchResult]
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult[SubscriptionSearchResult]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="StripeExecuteResultWithMeta"></a>

`StripeExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[BalanceTransaction], BalanceTransactionsListResultMeta]
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Charge], ChargesListResultMeta]
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Customer], CustomersApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Customer], CustomersListResultMeta]
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Dispute], DisputesListResultMeta]
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Invoice], InvoicesListResultMeta]
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[PaymentIntent], PaymentIntentsApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[PaymentIntent], PaymentIntentsListResultMeta]
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Payout], PayoutsListResultMeta]
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Product], ProductsApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Product], ProductsListResultMeta]
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Refund], RefundsListResultMeta]
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Subscription], SubscriptionsListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`StripeExecuteResultWithMeta[list[BalanceTransaction], BalanceTransactionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BalanceTransactionsListResult"></a>

`BalanceTransactionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`StripeExecuteResultWithMeta[list[Charge], ChargesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ChargesListResult"></a>

`ChargesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`StripeExecuteResultWithMeta[list[Customer], CustomersApiSearchResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CustomersApiSearchResult"></a>

`CustomersApiSearchResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`StripeExecuteResultWithMeta[list[Customer], CustomersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CustomersListResult"></a>

`CustomersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`StripeExecuteResultWithMeta[list[Dispute], DisputesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DisputesListResult"></a>

`DisputesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`StripeExecuteResultWithMeta[list[Invoice], InvoicesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="InvoicesListResult"></a>

`InvoicesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`StripeExecuteResultWithMeta[list[PaymentIntent], PaymentIntentsApiSearchResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PaymentIntentsApiSearchResult"></a>

`PaymentIntentsApiSearchResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`StripeExecuteResultWithMeta[list[PaymentIntent], PaymentIntentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PaymentIntentsListResult"></a>

`PaymentIntentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`StripeExecuteResultWithMeta[list[Payout], PayoutsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PayoutsListResult"></a>

`PayoutsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`StripeExecuteResultWithMeta[list[Product], ProductsApiSearchResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProductsApiSearchResult"></a>

`ProductsApiSearchResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`StripeExecuteResultWithMeta[list[Product], ProductsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProductsListResult"></a>

`ProductsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`StripeExecuteResultWithMeta[list[Refund], RefundsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="RefundsListResult"></a>

`RefundsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`StripeExecuteResultWithMeta[list[Subscription], SubscriptionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SubscriptionsListResult"></a>

`SubscriptionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`StripeExecuteResult[ChargeSearchResult](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ChargesApiSearchResult"></a>

`ChargesApiSearchResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`StripeExecuteResult[InvoiceSearchResult](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="InvoicesApiSearchResult"></a>

`InvoicesApiSearchResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`StripeExecuteResult[SubscriptionSearchResult](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SubscriptionsApiSearchResult"></a>

`SubscriptionsApiSearchResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="StripeReplicationConfig"></a>

`StripeReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Stripe.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str`
    :   Your Stripe account ID (starts with 'acct_', find yours at https://dashboard.stripe.com/settings/account)

    `model_config`
    :   The type of the None singleton.

<a id="Subscription"></a>

`Subscription(**data: Any)`
:   Subscription type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `application: str | Any | None`
    :   The type of the None singleton.

    `application_fee_percent: float | Any | None`
    :   The type of the None singleton.

    `automatic_tax: airbyte_agent_sdk.connectors.stripe.models.SubscriptionAutomaticTax | Any`
    :   The type of the None singleton.

    `billing_cycle_anchor: int | Any`
    :   The type of the None singleton.

    `billing_cycle_anchor_config: airbyte_agent_sdk.connectors.stripe.models.SubscriptionBillingCycleAnchorConfig | Any | None`
    :   The type of the None singleton.

    `billing_mode: airbyte_agent_sdk.connectors.stripe.models.SubscriptionBillingMode | Any`
    :   The type of the None singleton.

    `billing_thresholds: airbyte_agent_sdk.connectors.stripe.models.SubscriptionBillingThresholds | Any | None`
    :   The type of the None singleton.

    `cancel_at: int | Any | None`
    :   The type of the None singleton.

    `cancel_at_period_end: bool | Any`
    :   The type of the None singleton.

    `canceled_at: int | Any | None`
    :   The type of the None singleton.

    `cancellation_details: airbyte_agent_sdk.connectors.stripe.models.SubscriptionCancellationDetails | Any | None`
    :   The type of the None singleton.

    `collection_method: str | Any`
    :   The type of the None singleton.

    `created: int | Any`
    :   The type of the None singleton.

    `currency: str | Any`
    :   The type of the None singleton.

    `current_period_end: int | Any`
    :   The type of the None singleton.

    `current_period_start: int | Any`
    :   The type of the None singleton.

    `customer: str | Any`
    :   The type of the None singleton.

    `customer_account: str | Any | None`
    :   The type of the None singleton.

    `days_until_due: int | Any | None`
    :   The type of the None singleton.

    `default_payment_method: str | Any | None`
    :   The type of the None singleton.

    `default_source: str | Any | None`
    :   The type of the None singleton.

    `default_tax_rates: list[airbyte_agent_sdk.connectors.stripe.models.SubscriptionDefaultTaxRatesItem] | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `discount: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `discounts: list[str] | Any`
    :   The type of the None singleton.

    `ended_at: int | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `invoice_settings: airbyte_agent_sdk.connectors.stripe.models.SubscriptionInvoiceSettings | Any`
    :   The type of the None singleton.

    `items: airbyte_agent_sdk.connectors.stripe.models.SubscriptionItems | Any`
    :   The type of the None singleton.

    `latest_invoice: str | Any | None`
    :   The type of the None singleton.

    `livemode: bool | Any`
    :   The type of the None singleton.

    `metadata: dict[str, str] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_pending_invoice_item_invoice: int | Any | None`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `on_behalf_of: str | Any | None`
    :   The type of the None singleton.

    `pause_collection: airbyte_agent_sdk.connectors.stripe.models.SubscriptionPauseCollection | Any | None`
    :   The type of the None singleton.

    `payment_settings: airbyte_agent_sdk.connectors.stripe.models.SubscriptionPaymentSettings | Any | None`
    :   The type of the None singleton.

    `pending_invoice_item_interval: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `pending_setup_intent: str | Any | None`
    :   The type of the None singleton.

    `pending_update: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `plan: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `quantity: int | Any | None`
    :   The type of the None singleton.

    `schedule: str | Any | None`
    :   The type of the None singleton.

    `start_date: int | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `test_clock: str | Any | None`
    :   The type of the None singleton.

    `transfer_data: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `trial_end: int | Any | None`
    :   The type of the None singleton.

    `trial_settings: airbyte_agent_sdk.connectors.stripe.models.SubscriptionTrialSettings | Any | None`
    :   The type of the None singleton.

    `trial_start: int | Any | None`
    :   The type of the None singleton.

<a id="SubscriptionAutomaticTax"></a>

`SubscriptionAutomaticTax(**data: Any)`
:   Automatic tax settings for this subscription
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `disabled_reason: str | Any | None`
    :   If Stripe disabled automatic tax, this enum describes why

    `enabled: bool | Any`
    :   Whether Stripe automatically computes tax on this subscription

    `liability: airbyte_agent_sdk.connectors.stripe.models.SubscriptionAutomaticTaxLiability | Any | None`
    :   The account that's liable for tax

    `model_config`
    :   The type of the None singleton.

<a id="SubscriptionAutomaticTaxLiability"></a>

`SubscriptionAutomaticTaxLiability(**data: Any)`
:   The account that's liable for tax
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: str | Any | None`
    :   The connected account being referenced when type is account

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Type of the account referenced

<a id="SubscriptionBillingCycleAnchorConfig"></a>

`SubscriptionBillingCycleAnchorConfig(**data: Any)`
:   The fixed values used to calculate the billing_cycle_anchor
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `day_of_month: int | Any`
    :   The day of the month of the billing_cycle_anchor

    `hour: int | Any | None`
    :   The hour of the day of the billing_cycle_anchor

    `minute: int | Any | None`
    :   The minute of the hour of the billing_cycle_anchor

    `model_config`
    :   The type of the None singleton.

    `month: int | Any | None`
    :   The month to start full cycle billing periods

    `second: int | Any | None`
    :   The second of the minute of the billing_cycle_anchor

<a id="SubscriptionBillingMode"></a>

`SubscriptionBillingMode(**data: Any)`
:   Controls how prorations and invoices for subscriptions are calculated and orchestrated
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `flexible: airbyte_agent_sdk.connectors.stripe.models.SubscriptionBillingModeFlexible | Any | None`
    :   Configure behavior for flexible billing mode

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Controls how prorations and invoices for subscriptions are calculated and orchestrated

    `updated_at: int | Any | None`
    :   Details on when the current billing_mode was adopted

<a id="SubscriptionBillingModeFlexible"></a>

`SubscriptionBillingModeFlexible(**data: Any)`
:   Configure behavior for flexible billing mode
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `proration_discounts: str | Any`
    :   Controls how invoices and invoice items display proration amounts and discount amounts

<a id="SubscriptionBillingThresholds"></a>

`SubscriptionBillingThresholds(**data: Any)`
:   Define thresholds at which an invoice will be sent, and the subscription advanced to a new billing period
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount_gte: int | Any | None`
    :   Monetary threshold that triggers the subscription to create an invoice

    `model_config`
    :   The type of the None singleton.

    `reset_billing_cycle_anchor: bool | Any | None`
    :   Indicates if the billing_cycle_anchor should be reset when a threshold is reached

<a id="SubscriptionCancellationDetails"></a>

`SubscriptionCancellationDetails(**data: Any)`
:   Details about why this subscription was cancelled
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `comment: str | Any | None`
    :   Additional comments about why the user canceled the subscription

    `feedback: str | Any | None`
    :   The customer submitted reason for why they canceled

    `model_config`
    :   The type of the None singleton.

    `reason: str | Any | None`
    :   Why this subscription was canceled

<a id="SubscriptionDefaultTaxRatesItem"></a>

`SubscriptionDefaultTaxRatesItem(**data: Any)`
:   Nested schema for Subscription.default_tax_rates_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | Any`
    :   Defaults to true

    `country: str | Any | None`
    :   Two-letter country code (ISO 3166-1 alpha-2)

    `created: int | Any`
    :   Time at which the object was created

    `description: str | Any | None`
    :   An arbitrary string attached to the tax rate for your internal use only

    `display_name: str | Any`
    :   The display name of the tax rates

    `effective_percentage: float | Any | None`
    :   Actual/effective tax rate percentage out of 100

    `flat_amount: airbyte_agent_sdk.connectors.stripe.models.SubscriptionDefaultTaxRatesItemFlatAmount | Any | None`
    :   The amount of the tax rate when the rate_type is flat_amount

    `id: str | Any`
    :   Unique identifier for the object

    `inclusive: bool | Any`
    :   This specifies if the tax rate is inclusive or exclusive

    `jurisdiction: str | Any | None`
    :   The jurisdiction for the tax rate

    `jurisdiction_level: str | Any | None`
    :   The level of the jurisdiction that imposes this tax rate

    `livemode: bool | Any`
    :   Has the value true if the object exists in live mode or false if in test mode

    `metadata: dict[str, str] | Any | None`
    :   Set of key-value pairs

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   String representing the object's type

    `percentage: float | Any`
    :   Tax rate percentage out of 100

    `rate_type: str | Any | None`
    :   Indicates the type of tax rate applied to the taxable amount

    `state: str | Any | None`
    :   ISO 3166-2 subdivision code, without country prefix

    `tax_type: str | Any | None`
    :   The high-level tax type

<a id="SubscriptionDefaultTaxRatesItemFlatAmount"></a>

`SubscriptionDefaultTaxRatesItemFlatAmount(**data: Any)`
:   The amount of the tax rate when the rate_type is flat_amount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: int | Any`
    :   Amount of the tax when the rate_type is flat_amount

    `currency: str | Any`
    :   Three-letter ISO currency code, in lowercase

    `model_config`
    :   The type of the None singleton.

<a id="SubscriptionInvoiceSettings"></a>

`SubscriptionInvoiceSettings(**data: Any)`
:   All invoices will be billed using the specified settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_tax_ids: list[str] | Any | None`
    :   The account tax IDs associated with the subscription

    `issuer: airbyte_agent_sdk.connectors.stripe.models.SubscriptionInvoiceSettingsIssuer | Any`
    :   The connected account that issues the invoice

    `model_config`
    :   The type of the None singleton.

<a id="SubscriptionInvoiceSettingsIssuer"></a>

`SubscriptionInvoiceSettingsIssuer(**data: Any)`
:   The connected account that issues the invoice
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: str | Any | None`
    :   The connected account being referenced when type is account

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Type of the account referenced

<a id="SubscriptionItems"></a>

`SubscriptionItems(**data: Any)`
:   List of subscription items, each with an attached price
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.SubscriptionItemsDataItem] | Any`
    :   Details about each object

    `has_more: bool | Any`
    :   True if this list has another page of items after this one

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   String representing the object's type

    `total_count: int | Any`
    :   The total count of items in the list

    `url: str | Any`
    :   The URL where this list can be accessed

<a id="SubscriptionItemsDataItem"></a>

`SubscriptionItemsDataItem(**data: Any)`
:   Nested schema for SubscriptionItems.data_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `billing_thresholds: airbyte_agent_sdk.connectors.stripe.models.SubscriptionItemsDataItemBillingThresholds | Any | None`
    :   Define thresholds at which an invoice will be sent

    `created: int | Any`
    :   Time at which the object was created

    `current_period_end: int | Any`
    :   The end time of this subscription item's current billing period

    `current_period_start: int | Any`
    :   The start time of this subscription item's current billing period

    `discounts: list[str] | Any`
    :   The discounts applied to the subscription item

    `id: str | Any`
    :   Unique identifier for the object

    `metadata: dict[str, str] | Any`
    :   Set of key-value pairs

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   String representing the object's type

    `plan: dict[str, typing.Any] | Any | None`
    :   The plan the customer is subscribed to (deprecated, use price instead)

    `price: dict[str, typing.Any] | Any`
    :   The price the customer is subscribed to

    `quantity: int | Any | None`
    :   The quantity of the plan to which the customer should be subscribed

    `subscription: str | Any`
    :   The subscription this subscription_item belongs to

    `tax_rates: list[dict[str, typing.Any]] | Any | None`
    :   The tax rates which apply to this subscription_item

<a id="SubscriptionItemsDataItemBillingThresholds"></a>

`SubscriptionItemsDataItemBillingThresholds(**data: Any)`
:   Define thresholds at which an invoice will be sent
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `usage_gte: int | Any | None`
    :   Usage threshold that triggers the subscription to create an invoice

<a id="SubscriptionList"></a>

`SubscriptionList(**data: Any)`
:   SubscriptionList type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.Subscription] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="SubscriptionPauseCollection"></a>

`SubscriptionPauseCollection(**data: Any)`
:   If specified, payment collection for this subscription will be paused
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `behavior: str | Any`
    :   The payment collection behavior for this subscription while paused

    `model_config`
    :   The type of the None singleton.

    `resumes_at: int | Any | None`
    :   The time after which the subscription will resume collecting payments

<a id="SubscriptionPaymentSettings"></a>

`SubscriptionPaymentSettings(**data: Any)`
:   Payment settings passed on to invoices created by the subscription
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `payment_method_options: dict[str, typing.Any] | Any | None`
    :   Payment-method-specific configuration to provide to invoices

    `payment_method_types: list[str] | Any | None`
    :   The list of payment method types to provide to every invoice

<a id="SubscriptionSearchResult"></a>

`SubscriptionSearchResult(**data: Any)`
:   SubscriptionSearchResult type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.stripe.models.Subscription] | Any`
    :   The type of the None singleton.

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `object_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="SubscriptionTrialSettings"></a>

`SubscriptionTrialSettings(**data: Any)`
:   Settings related to subscription trials
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_behavior: airbyte_agent_sdk.connectors.stripe.models.SubscriptionTrialSettingsEndBehavior | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SubscriptionTrialSettingsEndBehavior"></a>

`SubscriptionTrialSettingsEndBehavior(**data: Any)`
:   Nested schema for SubscriptionTrialSettings.end_behavior
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `missing_payment_method: str | Any`
    :   Behavior when the trial ends and payment method is missing

    `model_config`
    :   The type of the None singleton.

<a id="SubscriptionsListResultMeta"></a>

`SubscriptionsListResultMeta(**data: Any)`
:   Metadata for subscriptions.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SubscriptionsSearchData"></a>

`SubscriptionsSearchData(**data: Any)`
:   Search result data for subscriptions entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `application: str | None`
    :   For Connect platforms, the application associated with the subscription.

    `application_fee_percent: float | None`
    :   For Connect platforms, the percentage of the subscription amount taken as an application fee.

    `automatic_tax: dict[str, typing.Any] | None`
    :   Automatic tax calculation settings for the subscription.

    `billing: str | None`
    :   Billing mode configuration for the subscription.

    `billing_cycle_anchor: float | None`
    :   Timestamp determining when the billing cycle for the subscription starts.

    `billing_cycle_anchor_config: dict[str, typing.Any] | None`
    :   Configuration for the subscription's billing cycle anchor behavior.

    `billing_thresholds: dict[str, typing.Any] | None`
    :   Defines thresholds at which an invoice will be sent, controlling billing timing based on usage.

    `cancel_at: float | None`
    :   Timestamp indicating when the subscription is scheduled to be canceled.

    `cancel_at_period_end: bool | None`
    :   Boolean indicating whether the subscription will be canceled at the end of the current billing period.

    `canceled_at: float | None`
    :   Timestamp indicating when the subscription was canceled, if applicable.

    `cancellation_details: dict[str, typing.Any] | None`
    :   Details about why and how the subscription was canceled.

    `collection_method: str | None`
    :   How invoices are collected (charge_automatically or send_invoice).

    `created: int | None`
    :   Timestamp indicating when the subscription was created.

    `currency: str | None`
    :   Three-letter ISO currency code in lowercase indicating the currency for the subscription.

    `current_period_end: float | None`
    :   Timestamp marking the end of the current billing period.

    `current_period_start: int | None`
    :   Timestamp marking the start of the current billing period.

    `customer: str | None`
    :   ID of the customer who owns the subscription, expandable to full customer object.

    `days_until_due: int | None`
    :   Number of days until the invoice is due for subscriptions using send_invoice collection method.

    `default_payment_method: str | None`
    :   ID of the default payment method for the subscription, taking precedence over default_source.

    `default_source: str | None`
    :   ID of the default payment source for the subscription.

    `default_tax_rates: list[typing.Any] | None`
    :   Tax rates that apply to the subscription by default.

    `description: str | None`
    :   Human-readable description of the subscription, displayable to the customer.

    `discount: dict[str, typing.Any] | None`
    :   Describes any discount currently applied to the subscription.

    `ended_at: float | None`
    :   Timestamp indicating when the subscription ended, if applicable.

    `id: str | None`
    :   Unique identifier for the subscription object.

    `invoice_settings: dict[str, typing.Any] | None`
    :   Settings for invoices generated by this subscription, such as custom fields and footer.

    `is_deleted: bool | None`
    :   Indicates whether the subscription has been deleted.

    `items: dict[str, typing.Any] | None`
    :   List of subscription items, each with an attached price defining what the customer is subscribed to.

    `latest_invoice: str | None`
    :   The most recent invoice this subscription has generated, expandable to full invoice object.

    `livemode: bool | None`
    :   Indicates whether the subscription exists in live mode (true) or test mode (false).

    `metadata: dict[str, typing.Any] | None`
    :   Set of key-value pairs that you can attach to the subscription for storing additional structured information.

    `model_config`
    :   The type of the None singleton.

    `next_pending_invoice_item_invoice: int | None`
    :   Timestamp when the next invoice for pending invoice items will be created.

    `object_: str | None`
    :   String representing the object type, always 'subscription'.

    `on_behalf_of: str | None`
    :   For Connect platforms, the account for which the subscription is being created or managed.

    `pause_collection: dict[str, typing.Any] | None`
    :   Configuration for pausing collection on the subscription while retaining the subscription structure.

    `payment_settings: dict[str, typing.Any] | None`
    :   Payment settings for invoices generated by this subscription.

    `pending_invoice_item_interval: dict[str, typing.Any] | None`
    :   Specifies an interval for aggregating usage records into pending invoice items.

    `pending_setup_intent: str | None`
    :   SetupIntent used for collecting user authentication when updating payment methods without immediate payment.

    `pending_update: dict[str, typing.Any] | None`
    :   If specified, pending updates that will be applied to the subscription once the latest_invoice has been paid.

    `plan: dict[str, typing.Any] | None`
    :   The plan associated with the subscription (deprecated, use items instead).

    `quantity: int | None`
    :   Quantity of the plan subscribed to (deprecated, use items instead).

    `schedule: str | None`
    :   ID of the subscription schedule managing this subscription's lifecycle, if applicable.

    `start_date: int | None`
    :   Timestamp indicating when the subscription started.

    `status: str | None`
    :   Current status of the subscription (incomplete, incomplete_expired, trialing, active, past_due, canceled, unpaid, or paused).

    `tax_percent: float | None`
    :   The percentage of tax applied to the subscription (deprecated, use default_tax_rates instead).

    `test_clock: str | None`
    :   ID of the test clock associated with this subscription for simulating time-based scenarios.

    `transfer_data: dict[str, typing.Any] | None`
    :   For Connect platforms, the account receiving funds from the subscription and optional percentage transferred.

    `trial_end: float | None`
    :   Timestamp indicating when the trial period ends, if applicable.

    `trial_settings: dict[str, typing.Any] | None`
    :   Settings related to trial periods, including conditions for ending trials.

    `trial_start: int | None`
    :   Timestamp indicating when the trial period began, if applicable.

    `updated: int | None`
    :   Timestamp indicating when the subscription was last updated.