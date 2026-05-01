---
id: airbyte_agent_sdk-connectors-paypal_transaction-models
title: airbyte_agent_sdk.connectors.paypal_transaction.models
---

Module airbyte_agent_sdk.connectors.paypal_transaction.models
=============================================================
Pydantic models for paypal-transaction connector.

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

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[BalancesSearchData]
    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[ListDisputesSearchData]
    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[ListPaymentsSearchData]
    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[ListProductsSearchData]
    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[SearchInvoicesSearchData]
    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[ShowProductDetailsSearchData]
    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult[TransactionsSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[BalancesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BalancesSearchResult"></a>

`BalancesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ListDisputesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ListDisputesSearchResult"></a>

`ListDisputesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ListPaymentsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ListPaymentsSearchResult"></a>

`ListPaymentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ListProductsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ListProductsSearchResult"></a>

`ListProductsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SearchInvoicesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SearchInvoicesSearchResult"></a>

`SearchInvoicesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ShowProductDetailsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ShowProductDetailsSearchResult"></a>

`ShowProductDetailsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TransactionsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TransactionsSearchResult"></a>

`TransactionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AuctionInfo"></a>

`AuctionInfo(**data: Any)`
:   Auction information.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auction_buyer_id: str | None`
    :   The type of the None singleton.

    `auction_closing_date: str | None`
    :   The type of the None singleton.

    `auction_item_site: str | None`
    :   The type of the None singleton.

    `auction_site: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BalanceDetail"></a>

`BalanceDetail(**data: Any)`
:   Balance information for a single currency.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `available_balance: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `currency: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `primary: bool | None`
    :   The type of the None singleton.

    `total_balance: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `withheld_balance: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

<a id="BalancesResponse"></a>

`BalancesResponse(**data: Any)`
:   Balances response with account balance details.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   The type of the None singleton.

    `as_of_time: str | None`
    :   The type of the None singleton.

    `balances: list[airbyte_agent_sdk.connectors.paypal_transaction.models.BalanceDetail] | None`
    :   The type of the None singleton.

    `last_refresh_time: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="BalancesSearchData"></a>

`BalancesSearchData(**data: Any)`
:   Search result data for balances entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   The unique identifier of the account.

    `as_of_time: str | None`
    :   The timestamp when the balances data was reported.

    `balances: list[typing.Any] | None`
    :   Object containing information about the account balances.

    `last_refresh_time: str | None`
    :   The timestamp when the balances data was last refreshed.

    `model_config`
    :   The type of the None singleton.

<a id="CartInfo"></a>

`CartInfo(**data: Any)`
:   Cart information for the transaction.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `item_details: list[airbyte_agent_sdk.connectors.paypal_transaction.models.ItemDetail] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paypal_invoice_id: str | None`
    :   The type of the None singleton.

    `tax_inclusive: bool | None`
    :   The type of the None singleton.

<a id="Dispute"></a>

`Dispute(**data: Any)`
:   A PayPal dispute object.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `create_time: str | None`
    :   The type of the None singleton.

    `dispute_amount: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `dispute_channel: str | None`
    :   The type of the None singleton.

    `dispute_id: str | None`
    :   The type of the None singleton.

    `dispute_life_cycle_stage: str | None`
    :   The type of the None singleton.

    `dispute_state: str | None`
    :   The type of the None singleton.

    `disputed_transactions: list[airbyte_agent_sdk.connectors.paypal_transaction.models.DisputeDisputedTransactionsItem] | None`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.paypal_transaction.models.DisputeLinksItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `outcome: str | None`
    :   The type of the None singleton.

    `reason: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `update_time: str | None`
    :   The type of the None singleton.

<a id="DisputeDisputedTransactionsItem"></a>

`DisputeDisputedTransactionsItem(**data: Any)`
:   Nested schema for Dispute.disputed_transactions_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `buyer_transaction_id: str | None`
    :   Buyer's transaction ID.

    `model_config`
    :   The type of the None singleton.

    `seller: airbyte_agent_sdk.connectors.paypal_transaction.models.DisputeDisputedTransactionsItemSeller | None`
    :   The type of the None singleton.

<a id="DisputeDisputedTransactionsItemSeller"></a>

`DisputeDisputedTransactionsItemSeller(**data: Any)`
:   Nested schema for DisputeDisputedTransactionsItem.seller
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `merchant_id: str | None`
    :   Seller's merchant ID.

    `model_config`
    :   The type of the None singleton.

<a id="DisputeLinksItem"></a>

`DisputeLinksItem(**data: Any)`
:   Nested schema for Dispute.links_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `method: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rel: str | None`
    :   The type of the None singleton.

<a id="DisputesList"></a>

`DisputesList(**data: Any)`
:   List of disputes.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `items: list[airbyte_agent_sdk.connectors.paypal_transaction.models.Dispute] | None`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.paypal_transaction.models.DisputesListLinksItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DisputesListLinksItem"></a>

`DisputesListLinksItem(**data: Any)`
:   Nested schema for DisputesList.links_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `method: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rel: str | None`
    :   The type of the None singleton.

<a id="IncentiveDetail"></a>

`IncentiveDetail(**data: Any)`
:   Incentive detail.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `incentive_amount: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `incentive_code: str | None`
    :   The type of the None singleton.

    `incentive_program_code: str | None`
    :   The type of the None singleton.

    `incentive_type: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="IncentiveInfo"></a>

`IncentiveInfo(**data: Any)`
:   Incentive information.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `incentive_details: list[airbyte_agent_sdk.connectors.paypal_transaction.models.IncentiveDetail] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Invoice"></a>

`Invoice(**data: Any)`
:   A PayPal invoice object.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `additional_recipients: list[str] | None`
    :   The type of the None singleton.

    `amount: airbyte_agent_sdk.connectors.paypal_transaction.models.InvoiceAmount | None`
    :   The type of the None singleton.

    `configuration: airbyte_agent_sdk.connectors.paypal_transaction.models.InvoiceConfiguration | None`
    :   The type of the None singleton.

    `detail: airbyte_agent_sdk.connectors.paypal_transaction.models.InvoiceDetail | None`
    :   The type of the None singleton.

    `due_amount: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `invoicer: airbyte_agent_sdk.connectors.paypal_transaction.models.InvoiceInvoicer | None`
    :   The type of the None singleton.

    `items: list[airbyte_agent_sdk.connectors.paypal_transaction.models.InvoiceItemsItem] | None`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.paypal_transaction.models.InvoiceLinksItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `payments: airbyte_agent_sdk.connectors.paypal_transaction.models.InvoicePayments | None`
    :   The type of the None singleton.

    `primary_recipients: list[airbyte_agent_sdk.connectors.paypal_transaction.models.InvoicePrimaryRecipientsItem] | None`
    :   The type of the None singleton.

    `refunds: airbyte_agent_sdk.connectors.paypal_transaction.models.InvoiceRefunds | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

<a id="InvoiceAmount"></a>

`InvoiceAmount(**data: Any)`
:   Total invoice amount.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `breakdown: airbyte_agent_sdk.connectors.paypal_transaction.models.InvoiceAmountBreakdown | None`
    :   The type of the None singleton.

    `currency_code: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

<a id="InvoiceAmountBreakdown"></a>

`InvoiceAmountBreakdown(**data: Any)`
:   Nested schema for InvoiceAmount.breakdown
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `custom: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `discount: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `item_total: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `shipping: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `tax_total: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

<a id="InvoiceConfiguration"></a>

`InvoiceConfiguration(**data: Any)`
:   Invoice configuration.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allow_tip: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `partial_payment: airbyte_agent_sdk.connectors.paypal_transaction.models.InvoiceConfigurationPartialPayment | None`
    :   The type of the None singleton.

    `tax_calculated_after_discount: str | None`
    :   The type of the None singleton.

    `tax_inclusive: str | None`
    :   The type of the None singleton.

    `template_id: str | None`
    :   The type of the None singleton.

<a id="InvoiceConfigurationPartialPayment"></a>

`InvoiceConfigurationPartialPayment(**data: Any)`
:   Nested schema for InvoiceConfiguration.partial_payment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allow_partial_payment: str | None`
    :   The type of the None singleton.

    `minimum_amount_due: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="InvoiceDetail"></a>

`InvoiceDetail(**data: Any)`
:   Invoice detail information.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currency_code: str | None`
    :   Currency code.

    `invoice_date: str | None`
    :   Invoice date.

    `invoice_number: str | None`
    :   Invoice number.

    `memo: str | None`
    :   Memo for the invoice.

    `metadata: airbyte_agent_sdk.connectors.paypal_transaction.models.InvoiceDetailMetadata | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   Note to the recipient.

    `payment_term: airbyte_agent_sdk.connectors.paypal_transaction.models.InvoiceDetailPaymentTerm | None`
    :   The type of the None singleton.

    `reference: str | None`
    :   Reference for the invoice.

    `terms_and_conditions: str | None`
    :   Terms and conditions.

<a id="InvoiceDetailMetadata"></a>

`InvoiceDetailMetadata(**data: Any)`
:   Nested schema for InvoiceDetail.metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cancel_time: str | None`
    :   Cancellation time.

    `cancelled_by: str | None`
    :   Canceller.

    `create_time: str | None`
    :   Invoice creation time.

    `created_by: str | None`
    :   Creator of the invoice.

    `created_by_flow: str | None`
    :   Flow that created the invoice.

    `first_sent_time: str | None`
    :   First sent time.

    `invoicer_view_url: str | None`
    :   Invoicer view URL.

    `last_sent_time: str | None`
    :   Last sent time.

    `last_update_time: str | None`
    :   Last update time.

    `last_updated_by: str | None`
    :   Last updater.

    `model_config`
    :   The type of the None singleton.

    `recipient_view_url: str | None`
    :   Recipient view URL.

<a id="InvoiceDetailPaymentTerm"></a>

`InvoiceDetailPaymentTerm(**data: Any)`
:   Nested schema for InvoiceDetail.payment_term
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `due_date: str | None`
    :   Due date.

    `model_config`
    :   The type of the None singleton.

    `term_type: str | None`
    :   Payment term type.

<a id="InvoiceInvoicer"></a>

`InvoiceInvoicer(**data: Any)`
:   Invoicer details.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `email_address: str | None`
    :   Invoicer email.

    `model_config`
    :   The type of the None singleton.

    `name: airbyte_agent_sdk.connectors.paypal_transaction.models.InvoiceInvoicerName | None`
    :   The type of the None singleton.

<a id="InvoiceInvoicerName"></a>

`InvoiceInvoicerName(**data: Any)`
:   Nested schema for InvoiceInvoicer.name
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `full_name: str | None`
    :   The type of the None singleton.

    `given_name: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `surname: str | None`
    :   The type of the None singleton.

<a id="InvoiceItemsItem"></a>

`InvoiceItemsItem(**data: Any)`
:   Nested schema for Invoice.items_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `quantity: str | None`
    :   The type of the None singleton.

    `tax: airbyte_agent_sdk.connectors.paypal_transaction.models.InvoiceItemsItemTax | None`
    :   The type of the None singleton.

    `unit_amount: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `unit_of_measure: str | None`
    :   The type of the None singleton.

<a id="InvoiceItemsItemTax"></a>

`InvoiceItemsItemTax(**data: Any)`
:   Nested schema for InvoiceItemsItem.tax
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `percent: str | None`
    :   The type of the None singleton.

<a id="InvoiceLinksItem"></a>

`InvoiceLinksItem(**data: Any)`
:   Nested schema for Invoice.links_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `method: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rel: str | None`
    :   The type of the None singleton.

<a id="InvoicePayments"></a>

`InvoicePayments(**data: Any)`
:   Payment records for this invoice.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `paid_amount: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `transactions: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

<a id="InvoicePrimaryRecipientsItem"></a>

`InvoicePrimaryRecipientsItem(**data: Any)`
:   Nested schema for Invoice.primary_recipients_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `billing_info: airbyte_agent_sdk.connectors.paypal_transaction.models.InvoicePrimaryRecipientsItemBillingInfo | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="InvoicePrimaryRecipientsItemBillingInfo"></a>

`InvoicePrimaryRecipientsItemBillingInfo(**data: Any)`
:   Nested schema for InvoicePrimaryRecipientsItem.billing_info
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `additional_info_value: str | None`
    :   The type of the None singleton.

    `email_address: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: airbyte_agent_sdk.connectors.paypal_transaction.models.InvoicePrimaryRecipientsItemBillingInfoName | None`
    :   The type of the None singleton.

<a id="InvoicePrimaryRecipientsItemBillingInfoName"></a>

`InvoicePrimaryRecipientsItemBillingInfoName(**data: Any)`
:   Nested schema for InvoicePrimaryRecipientsItemBillingInfo.name
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `full_name: str | None`
    :   The type of the None singleton.

    `given_name: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `surname: str | None`
    :   The type of the None singleton.

<a id="InvoiceRefunds"></a>

`InvoiceRefunds(**data: Any)`
:   Refund records for this invoice.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `refund_amount: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `transactions: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

<a id="InvoiceSearchParams"></a>

`InvoiceSearchParams(**data: Any)`
:   Parameters for searching invoices.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `creation_date_range: airbyte_agent_sdk.connectors.paypal_transaction.models.InvoiceSearchParamsCreationDateRange | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="InvoiceSearchParamsCreationDateRange"></a>

`InvoiceSearchParamsCreationDateRange(**data: Any)`
:   Filter by invoice creation date range.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end: str | None`
    :   End date in ISO 8601 format.

    `model_config`
    :   The type of the None singleton.

    `start: str | None`
    :   Start date in ISO 8601 format.

<a id="InvoicesList"></a>

`InvoicesList(**data: Any)`
:   Paginated list of invoices from search.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `items: list[airbyte_agent_sdk.connectors.paypal_transaction.models.Invoice] | None`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.paypal_transaction.models.InvoicesListLinksItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_items: int | None`
    :   The type of the None singleton.

    `total_pages: int | None`
    :   The type of the None singleton.

<a id="InvoicesListLinksItem"></a>

`InvoicesListLinksItem(**data: Any)`
:   Nested schema for InvoicesList.links_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `method: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rel: str | None`
    :   The type of the None singleton.

<a id="ItemDetail"></a>

`ItemDetail(**data: Any)`
:   Details for a single cart item.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `invoice_number: str | None`
    :   The type of the None singleton.

    `item_amount: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `item_code: str | None`
    :   The type of the None singleton.

    `item_description: str | None`
    :   The type of the None singleton.

    `item_name: str | None`
    :   The type of the None singleton.

    `item_quantity: str | None`
    :   The type of the None singleton.

    `item_unit_price: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `tax_amounts: list[airbyte_agent_sdk.connectors.paypal_transaction.models.ItemDetailTaxAmountsItem] | None`
    :   The type of the None singleton.

    `total_item_amount: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

<a id="ItemDetailTaxAmountsItem"></a>

`ItemDetailTaxAmountsItem(**data: Any)`
:   Nested schema for ItemDetail.tax_amounts_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `tax_amount: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

<a id="ListDisputesListResultMeta"></a>

`ListDisputesListResultMeta(**data: Any)`
:   Metadata for list_disputes.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

<a id="ListDisputesSearchData"></a>

`ListDisputesSearchData(**data: Any)`
:   Search result data for list_disputes entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

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

<a id="ListPaymentsListResultMeta"></a>

`ListPaymentsListResultMeta(**data: Any)`
:   Metadata for list_payments.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_id: str | None`
    :   The type of the None singleton.

<a id="ListPaymentsSearchData"></a>

`ListPaymentsSearchData(**data: Any)`
:   Search result data for list_payments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

    `payer: dict[str, typing.Any] | None`
    :   Details of the payer who made the payment

    `state: str | None`
    :   The state of the payment.

    `transactions: list[typing.Any] | None`
    :   List of transactions associated with the payment

    `update_time: str | None`
    :   The date and time when the payment was last updated.

<a id="ListProductsListResultMeta"></a>

`ListProductsListResultMeta(**data: Any)`
:   Metadata for list_products.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

<a id="ListProductsSearchData"></a>

`ListProductsSearchData(**data: Any)`
:   Search result data for list_products entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `create_time: str | None`
    :   The time when the product was created

    `description: str | None`
    :   Detailed information or features of the product

    `id: str | None`
    :   Unique identifier for the product

    `links: list[typing.Any] | None`
    :   List of links related to the fetched products.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name or title of the product

<a id="Money"></a>

`Money(**data: Any)`
:   Currency amount with code and value.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currency_code: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

<a id="PayerInfo"></a>

`PayerInfo(**data: Any)`
:   Information about the payer.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   The type of the None singleton.

    `address_status: str | None`
    :   The type of the None singleton.

    `country_code: str | None`
    :   The type of the None singleton.

    `email_address: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `payer_name: airbyte_agent_sdk.connectors.paypal_transaction.models.PayerName | None`
    :   The type of the None singleton.

    `payer_status: str | None`
    :   The type of the None singleton.

<a id="PayerName"></a>

`PayerName(**data: Any)`
:   Payer name details.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `alternate_full_name: str | None`
    :   The type of the None singleton.

    `given_name: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `surname: str | None`
    :   The type of the None singleton.

<a id="Payment"></a>

`Payment(**data: Any)`
:   A PayPal payment object.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cart: str | None`
    :   The type of the None singleton.

    `create_time: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `intent: str | None`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.paypal_transaction.models.PaymentLinksItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `payer: airbyte_agent_sdk.connectors.paypal_transaction.models.PaymentPayer | None`
    :   The type of the None singleton.

    `state: str | None`
    :   The type of the None singleton.

    `transactions: list[airbyte_agent_sdk.connectors.paypal_transaction.models.PaymentTransactionsItem] | None`
    :   The type of the None singleton.

    `update_time: str | None`
    :   The type of the None singleton.

<a id="PaymentLinksItem"></a>

`PaymentLinksItem(**data: Any)`
:   Nested schema for Payment.links_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `method: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rel: str | None`
    :   The type of the None singleton.

<a id="PaymentPayer"></a>

`PaymentPayer(**data: Any)`
:   Payer information.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `payer_info: airbyte_agent_sdk.connectors.paypal_transaction.models.PaymentPayerPayerInfo | None`
    :   The type of the None singleton.

    `payment_method: str | None`
    :   Payment method.

    `status: str | None`
    :   Payer status.

<a id="PaymentPayerPayerInfo"></a>

`PaymentPayerPayerInfo(**data: Any)`
:   Nested schema for PaymentPayer.payer_info
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `country_code: str | None`
    :   Payer country code.

    `email: str | None`
    :   Payer email.

    `first_name: str | None`
    :   Payer first name.

    `last_name: str | None`
    :   Payer last name.

    `model_config`
    :   The type of the None singleton.

    `payer_id: str | None`
    :   Payer ID.

<a id="PaymentTransactionsItem"></a>

`PaymentTransactionsItem(**data: Any)`
:   Nested schema for Payment.transactions_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: airbyte_agent_sdk.connectors.paypal_transaction.models.PaymentTransactionsItemAmount | None`
    :   The type of the None singleton.

    `description: str | None`
    :   Transaction description.

    `model_config`
    :   The type of the None singleton.

    `related_resources: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

<a id="PaymentTransactionsItemAmount"></a>

`PaymentTransactionsItemAmount(**data: Any)`
:   Nested schema for PaymentTransactionsItem.amount
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currency: str | None`
    :   Currency code.

    `details: airbyte_agent_sdk.connectors.paypal_transaction.models.PaymentTransactionsItemAmountDetails | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total: str | None`
    :   Total amount.

<a id="PaymentTransactionsItemAmountDetails"></a>

`PaymentTransactionsItemAmountDetails(**data: Any)`
:   Nested schema for PaymentTransactionsItemAmount.details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `handling_fee: str | None`
    :   The type of the None singleton.

    `insurance: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `shipping: str | None`
    :   The type of the None singleton.

    `shipping_discount: str | None`
    :   The type of the None singleton.

    `subtotal: str | None`
    :   The type of the None singleton.

<a id="PaymentsList"></a>

`PaymentsList(**data: Any)`
:   List of payments.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_id: str | None`
    :   The type of the None singleton.

    `payments: list[airbyte_agent_sdk.connectors.paypal_transaction.models.Payment] | None`
    :   The type of the None singleton.

<a id="PaypalTransactionAuthConfig"></a>

`PaypalTransactionAuthConfig(**data: Any)`
:   PayPal OAuth2 Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str | None`
    :   OAuth2 access token obtained via client credentials grant. Use the PayPal token endpoint with your client_id and client_secret to obtain this.

    `client_id: str`
    :   The Client ID of your PayPal developer application.

    `client_secret: str`
    :   The Client Secret of your PayPal developer application.

    `model_config`
    :   The type of the None singleton.

<a id="PaypalTransactionCheckResult"></a>

`PaypalTransactionCheckResult(**data: Any)`
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

<a id="PaypalTransactionExecuteResult"></a>

`PaypalTransactionExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResult[BalancesResponse]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="PaypalTransactionExecuteResultWithMeta"></a>

`PaypalTransactionExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta[list[Dispute], ListDisputesListResultMeta]
    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta[list[Invoice], SearchInvoicesListResultMeta]
    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta[list[Payment], ListPaymentsListResultMeta]
    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta[list[Product], ListProductsListResultMeta]
    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta[list[Transaction], TransactionsListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`PaypalTransactionExecuteResultWithMeta[list[Dispute], ListDisputesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ListDisputesListResult"></a>

`ListDisputesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PaypalTransactionExecuteResultWithMeta[list[Invoice], SearchInvoicesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SearchInvoicesListResult"></a>

`SearchInvoicesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PaypalTransactionExecuteResultWithMeta[list[Payment], ListPaymentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ListPaymentsListResult"></a>

`ListPaymentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PaypalTransactionExecuteResultWithMeta[list[Product], ListProductsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ListProductsListResult"></a>

`ListProductsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PaypalTransactionExecuteResultWithMeta[list[Transaction], TransactionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TransactionsListResult"></a>

`TransactionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PaypalTransactionExecuteResult[BalancesResponse](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BalancesListResult"></a>

`BalancesListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.paypal_transaction.models.PaypalTransactionExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="PaypalTransactionReplicationConfig"></a>

`PaypalTransactionReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from PayPal.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `start_date: str`
    :   Start date for data extraction in ISO 8601 format. Date must be in range from 3 years till 12 hours before present time.

<a id="Product"></a>

`Product(**data: Any)`
:   A PayPal catalog product (summary).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `create_time: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.paypal_transaction.models.ProductLinksItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

<a id="ProductDetails"></a>

`ProductDetails(**data: Any)`
:   Detailed catalog product information.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `category: str | None`
    :   The type of the None singleton.

    `create_time: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `home_url: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `image_url: str | None`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.paypal_transaction.models.ProductDetailsLinksItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `update_time: str | None`
    :   The type of the None singleton.

<a id="ProductDetailsLinksItem"></a>

`ProductDetailsLinksItem(**data: Any)`
:   Nested schema for ProductDetails.links_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `method: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rel: str | None`
    :   The type of the None singleton.

<a id="ProductLinksItem"></a>

`ProductLinksItem(**data: Any)`
:   Nested schema for Product.links_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `method: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rel: str | None`
    :   The type of the None singleton.

<a id="ProductsList"></a>

`ProductsList(**data: Any)`
:   List of catalog products.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: list[airbyte_agent_sdk.connectors.paypal_transaction.models.ProductsListLinksItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `products: list[airbyte_agent_sdk.connectors.paypal_transaction.models.Product] | None`
    :   The type of the None singleton.

<a id="ProductsListLinksItem"></a>

`ProductsListLinksItem(**data: Any)`
:   Nested schema for ProductsList.links_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `method: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rel: str | None`
    :   The type of the None singleton.

<a id="SearchInvoicesListResultMeta"></a>

`SearchInvoicesListResultMeta(**data: Any)`
:   Metadata for search_invoices.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

<a id="SearchInvoicesSearchData"></a>

`SearchInvoicesSearchData(**data: Any)`
:   Search result data for search_invoices entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

    `payments: dict[str, typing.Any] | None`
    :   Payment transactions associated with the invoice

    `primary_recipients: list[typing.Any] | None`
    :   Primary recipients associated with the invoice

    `refunds: dict[str, typing.Any] | None`
    :   Refund transactions associated with the invoice

    `status: str | None`
    :   Current status of the invoice

<a id="ShippingAddress"></a>

`ShippingAddress(**data: Any)`
:   Shipping address details.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `city: str | None`
    :   The type of the None singleton.

    `country_code: str | None`
    :   The type of the None singleton.

    `line1: str | None`
    :   The type of the None singleton.

    `line2: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `postal_code: str | None`
    :   The type of the None singleton.

<a id="ShippingInfo"></a>

`ShippingInfo(**data: Any)`
:   Shipping information for the transaction.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: airbyte_agent_sdk.connectors.paypal_transaction.models.ShippingAddress | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

<a id="ShowProductDetailsSearchData"></a>

`ShowProductDetailsSearchData(**data: Any)`
:   Search result data for show_product_details entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

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

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the product

    `type_: str | None`
    :   The type or category of the product

    `update_time: str | None`
    :   The date and time when the product was last updated

<a id="StoreInfo"></a>

`StoreInfo(**data: Any)`
:   Store information.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `store_id: str | None`
    :   The type of the None singleton.

    `terminal_id: str | None`
    :   The type of the None singleton.

<a id="Transaction"></a>

`Transaction(**data: Any)`
:   A single PayPal transaction with full details.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auction_info: airbyte_agent_sdk.connectors.paypal_transaction.models.AuctionInfo | None`
    :   The type of the None singleton.

    `cart_info: airbyte_agent_sdk.connectors.paypal_transaction.models.CartInfo | None`
    :   The type of the None singleton.

    `incentive_info: airbyte_agent_sdk.connectors.paypal_transaction.models.IncentiveInfo | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `payer_info: airbyte_agent_sdk.connectors.paypal_transaction.models.PayerInfo | None`
    :   The type of the None singleton.

    `shipping_info: airbyte_agent_sdk.connectors.paypal_transaction.models.ShippingInfo | None`
    :   The type of the None singleton.

    `store_info: airbyte_agent_sdk.connectors.paypal_transaction.models.StoreInfo | None`
    :   The type of the None singleton.

    `transaction_id: str | None`
    :   The type of the None singleton.

    `transaction_info: airbyte_agent_sdk.connectors.paypal_transaction.models.TransactionInfo | None`
    :   The type of the None singleton.

    `transaction_updated_date: str | None`
    :   The type of the None singleton.

<a id="TransactionInfo"></a>

`TransactionInfo(**data: Any)`
:   Detailed transaction information.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `custom_field: str | None`
    :   The type of the None singleton.

    `fee_amount: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `insurance_amount: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `invoice_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paypal_account_id: str | None`
    :   The type of the None singleton.

    `paypal_reference_id: str | None`
    :   The type of the None singleton.

    `paypal_reference_id_type: str | None`
    :   The type of the None singleton.

    `protection_eligibility: str | None`
    :   The type of the None singleton.

    `shipping_amount: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `shipping_discount_amount: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `transaction_amount: airbyte_agent_sdk.connectors.paypal_transaction.models.Money | None`
    :   The type of the None singleton.

    `transaction_event_code: str | None`
    :   The type of the None singleton.

    `transaction_id: str | None`
    :   The type of the None singleton.

    `transaction_initiation_date: str | None`
    :   The type of the None singleton.

    `transaction_note: str | None`
    :   The type of the None singleton.

    `transaction_status: str | None`
    :   The type of the None singleton.

    `transaction_subject: str | None`
    :   The type of the None singleton.

    `transaction_updated_date: str | None`
    :   The type of the None singleton.

<a id="TransactionsList"></a>

`TransactionsList(**data: Any)`
:   Paginated list of transactions.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_number: str | None`
    :   The type of the None singleton.

    `end_date: str | None`
    :   The type of the None singleton.

    `last_refreshed_datetime: str | None`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.paypal_transaction.models.TransactionsListLinksItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `page: int | None`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The type of the None singleton.

    `total_items: int | None`
    :   The type of the None singleton.

    `total_pages: int | None`
    :   The type of the None singleton.

    `transaction_details: list[airbyte_agent_sdk.connectors.paypal_transaction.models.Transaction] | None`
    :   The type of the None singleton.

<a id="TransactionsListLinksItem"></a>

`TransactionsListLinksItem(**data: Any)`
:   Nested schema for TransactionsList.links_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | None`
    :   The type of the None singleton.

    `method: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rel: str | None`
    :   The type of the None singleton.

<a id="TransactionsListResultMeta"></a>

`TransactionsListResultMeta(**data: Any)`
:   Metadata for transactions.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page: int | None`
    :   The type of the None singleton.

    `total_items: int | None`
    :   The type of the None singleton.

    `total_pages: int | None`
    :   The type of the None singleton.

<a id="TransactionsSearchData"></a>

`TransactionsSearchData(**data: Any)`
:   Search result data for transactions entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auction_info: dict[str, typing.Any] | None`
    :   Information related to an auction

    `cart_info: dict[str, typing.Any] | None`
    :   Details of items in the cart

    `incentive_info: dict[str, typing.Any] | None`
    :   Details of any incentives applied

    `model_config`
    :   The type of the None singleton.

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