---
id: airbyte_agent_sdk-connectors-stripe-types
title: airbyte_agent_sdk.connectors.stripe.types
---

Module airbyte_agent_sdk.connectors.stripe.types
================================================
Type definitions for stripe connector.

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

<a id="BalanceGetParams"></a>

`BalanceGetParams(*args, **kwargs)`
:   Parameters for balance.get operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="BalanceTransactionsGetParams"></a>

`BalanceTransactionsGetParams(*args, **kwargs)`
:   Parameters for balance_transactions.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="BalanceTransactionsListParams"></a>

`BalanceTransactionsListParams(*args, **kwargs)`
:   Parameters for balance_transactions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: airbyte_agent_sdk.connectors.stripe.types.BalanceTransactionsListParamsCreated`
    :   The type of the None singleton.

    `currency: str`
    :   The type of the None singleton.

    `ending_before: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `payout: str`
    :   The type of the None singleton.

    `source: str`
    :   The type of the None singleton.

    `starting_after: str`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="BalanceTransactionsListParamsCreated"></a>

`BalanceTransactionsListParamsCreated(*args, **kwargs)`
:   Nested schema for BalanceTransactionsListParams.created

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: int`
    :   The type of the None singleton.

    `gte: int`
    :   The type of the None singleton.

    `lt: int`
    :   The type of the None singleton.

    `lte: int`
    :   The type of the None singleton.

<a id="ChargesAndCondition"></a>

`ChargesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.stripe.types.ChargesEqCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesNeqCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesGtCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesGteCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesLtCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesLteCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesInCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesLikeCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesContainsCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesNotCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesAndCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesOrCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesAnyCondition]`
    :   The type of the None singleton.

<a id="ChargesAnyCondition"></a>

`ChargesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.stripe.types.ChargesAnyValueFilter`
    :   The type of the None singleton.

<a id="ChargesAnyValueFilter"></a>

`ChargesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Any`
    :   Amount intended to be collected by this payment in the smallest currency unit (e.g., 100 cents for $1.00), supporting up to eight digits.

    `amount_captured: Any`
    :   Amount that was actually captured from this charge.

    `amount_refunded: Any`
    :   Amount that has been refunded back to the customer.

    `amount_updates: Any`
    :   Updates to the amount that have been made during the charge lifecycle.

    `application: Any`
    :   ID of the application that created this charge (Connect only).

    `application_fee: Any`
    :   ID of the application fee associated with this charge (Connect only).

    `application_fee_amount: Any`
    :   The amount of the application fee deducted from this charge (Connect only).

    `balance_transaction: Any`
    :   ID of the balance transaction that describes the impact of this charge on your account balance (excluding refunds or disputes).

    `billing_details: Any`
    :   Billing information associated with the payment method at the time of the transaction, including name, email, phone, and address.

    `calculated_statement_descriptor: Any`
    :   The full statement descriptor that appears on the customer's credit card statement, combining prefix and suffix.

    `captured: Any`
    :   Whether the charge has been captured and funds transferred to your account.

    `card: Any`
    :   Deprecated card object containing payment card details if a card was used.

    `created: Any`
    :   Timestamp indicating when the charge was created.

    `currency: Any`
    :   Three-letter ISO currency code in lowercase (e.g., 'usd', 'eur') for the charge amount.

    `customer: Any`
    :   ID of the customer this charge is for, if one exists.

    `description: Any`
    :   An arbitrary string attached to the charge, often useful for displaying to users or internal reference.

    `destination: Any`
    :   ID of the destination account where funds are transferred (Connect only).

    `dispute: Any`
    :   ID of the dispute object if the charge has been disputed.

    `disputed: Any`
    :   Whether the charge has been disputed by the customer with their card issuer.

    `failure_balance_transaction: Any`
    :   ID of the balance transaction that describes the reversal of funds if the charge failed.

    `failure_code: Any`
    :   Error code explaining the reason for charge failure, if applicable.

    `failure_message: Any`
    :   Human-readable message providing more details about why the charge failed.

    `fraud_details: Any`
    :   Information about fraud assessments and user reports related to this charge.

    `id: Any`
    :   Unique identifier for the charge, used to link transactions across other records.

    `invoice: Any`
    :   ID of the invoice this charge is for, if the charge was created by invoicing.

    `livemode: Any`
    :   Whether the charge occurred in live mode (true) or test mode (false).

    `metadata: Any`
    :   Key-value pairs for storing additional structured information about the charge, useful for internal tracking.

    `object_: Any`
    :   String representing the object type, always 'charge' for charge objects.

    `on_behalf_of: Any`
    :   ID of the account on whose behalf the charge was made (Connect only).

    `order: Any`
    :   Deprecated field for order information associated with this charge.

    `outcome: Any`
    :   Details about the outcome of the charge, including network status, risk assessment, and reason codes.

    `paid: Any`
    :   Whether the charge succeeded and funds were successfully collected.

    `payment_intent: Any`
    :   ID of the PaymentIntent associated with this charge, if one exists.

    `payment_method: Any`
    :   ID of the payment method used for this charge.

    `payment_method_details: Any`
    :   Details about the payment method at the time of the transaction, including card brand, network, and authentication results.

    `receipt_email: Any`
    :   Email address to which the receipt for this charge was sent.

    `receipt_number: Any`
    :   Receipt number that appears on email receipts sent for this charge.

    `receipt_url: Any`
    :   URL to a hosted receipt page for this charge, viewable by the customer.

    `refunded: Any`
    :   Whether the charge has been fully refunded (partial refunds will still show as false).

    `refunds: Any`
    :   List of refunds that have been applied to this charge.

    `review: Any`
    :   ID of the review object associated with this charge, if it was flagged for manual review.

    `shipping: Any`
    :   Shipping information for the charge, including recipient name, address, and tracking details.

    `source: Any`
    :   Deprecated payment source object used to create this charge.

    `source_transfer: Any`
    :   ID of the transfer from a source account if funds came from another Stripe account (Connect only).

    `statement_description: Any`
    :   Deprecated alias for statement_descriptor.

    `statement_descriptor: Any`
    :   Statement descriptor that overrides the account default for card charges, appearing on the customer's statement.

    `statement_descriptor_suffix: Any`
    :   Suffix concatenated to the account's statement descriptor prefix to form the complete descriptor on customer statements.

    `status: Any`
    :   Current status of the payment: 'succeeded' (completed), 'pending' (processing), or 'failed' (unsuccessful).

    `transfer_data: Any`
    :   Object containing destination and amount for transfers to connected accounts (Connect only).

    `transfer_group: Any`
    :   String identifier for grouping related charges and transfers together (Connect only).

    `updated: Any`
    :   Timestamp of the last update to this charge object.

<a id="ChargesApiSearchParams"></a>

`ChargesApiSearchParams(*args, **kwargs)`
:   Parameters for charges.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `page: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="ChargesContainsCondition"></a>

`ChargesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.stripe.types.ChargesAnyValueFilter`
    :   The type of the None singleton.

<a id="ChargesEqCondition"></a>

`ChargesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.stripe.types.ChargesSearchFilter`
    :   The type of the None singleton.

<a id="ChargesFuzzyCondition"></a>

`ChargesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.stripe.types.ChargesStringFilter`
    :   The type of the None singleton.

<a id="ChargesGetParams"></a>

`ChargesGetParams(*args, **kwargs)`
:   Parameters for charges.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ChargesGtCondition"></a>

`ChargesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.stripe.types.ChargesSearchFilter`
    :   The type of the None singleton.

<a id="ChargesGteCondition"></a>

`ChargesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.stripe.types.ChargesSearchFilter`
    :   The type of the None singleton.

<a id="ChargesInCondition"></a>

`ChargesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.stripe.types.ChargesInFilter`
    :   The type of the None singleton.

<a id="ChargesInFilter"></a>

`ChargesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: list[int]`
    :   Amount intended to be collected by this payment in the smallest currency unit (e.g., 100 cents for $1.00), supporting up to eight digits.

    `amount_captured: list[int]`
    :   Amount that was actually captured from this charge.

    `amount_refunded: list[int]`
    :   Amount that has been refunded back to the customer.

    `amount_updates: list[list[typing.Any]]`
    :   Updates to the amount that have been made during the charge lifecycle.

    `application: list[str]`
    :   ID of the application that created this charge (Connect only).

    `application_fee: list[str]`
    :   ID of the application fee associated with this charge (Connect only).

    `application_fee_amount: list[int]`
    :   The amount of the application fee deducted from this charge (Connect only).

    `balance_transaction: list[str]`
    :   ID of the balance transaction that describes the impact of this charge on your account balance (excluding refunds or disputes).

    `billing_details: list[dict[str, typing.Any]]`
    :   Billing information associated with the payment method at the time of the transaction, including name, email, phone, and address.

    `calculated_statement_descriptor: list[str]`
    :   The full statement descriptor that appears on the customer's credit card statement, combining prefix and suffix.

    `captured: list[bool]`
    :   Whether the charge has been captured and funds transferred to your account.

    `card: list[dict[str, typing.Any]]`
    :   Deprecated card object containing payment card details if a card was used.

    `created: list[int]`
    :   Timestamp indicating when the charge was created.

    `currency: list[str]`
    :   Three-letter ISO currency code in lowercase (e.g., 'usd', 'eur') for the charge amount.

    `customer: list[str]`
    :   ID of the customer this charge is for, if one exists.

    `description: list[str]`
    :   An arbitrary string attached to the charge, often useful for displaying to users or internal reference.

    `destination: list[str]`
    :   ID of the destination account where funds are transferred (Connect only).

    `dispute: list[str]`
    :   ID of the dispute object if the charge has been disputed.

    `disputed: list[bool]`
    :   Whether the charge has been disputed by the customer with their card issuer.

    `failure_balance_transaction: list[str]`
    :   ID of the balance transaction that describes the reversal of funds if the charge failed.

    `failure_code: list[str]`
    :   Error code explaining the reason for charge failure, if applicable.

    `failure_message: list[str]`
    :   Human-readable message providing more details about why the charge failed.

    `fraud_details: list[dict[str, typing.Any]]`
    :   Information about fraud assessments and user reports related to this charge.

    `id: list[str]`
    :   Unique identifier for the charge, used to link transactions across other records.

    `invoice: list[str]`
    :   ID of the invoice this charge is for, if the charge was created by invoicing.

    `livemode: list[bool]`
    :   Whether the charge occurred in live mode (true) or test mode (false).

    `metadata: list[dict[str, typing.Any]]`
    :   Key-value pairs for storing additional structured information about the charge, useful for internal tracking.

    `object_: list[str]`
    :   String representing the object type, always 'charge' for charge objects.

    `on_behalf_of: list[str]`
    :   ID of the account on whose behalf the charge was made (Connect only).

    `order: list[str]`
    :   Deprecated field for order information associated with this charge.

    `outcome: list[dict[str, typing.Any]]`
    :   Details about the outcome of the charge, including network status, risk assessment, and reason codes.

    `paid: list[bool]`
    :   Whether the charge succeeded and funds were successfully collected.

    `payment_intent: list[str]`
    :   ID of the PaymentIntent associated with this charge, if one exists.

    `payment_method: list[str]`
    :   ID of the payment method used for this charge.

    `payment_method_details: list[dict[str, typing.Any]]`
    :   Details about the payment method at the time of the transaction, including card brand, network, and authentication results.

    `receipt_email: list[str]`
    :   Email address to which the receipt for this charge was sent.

    `receipt_number: list[str]`
    :   Receipt number that appears on email receipts sent for this charge.

    `receipt_url: list[str]`
    :   URL to a hosted receipt page for this charge, viewable by the customer.

    `refunded: list[bool]`
    :   Whether the charge has been fully refunded (partial refunds will still show as false).

    `refunds: list[dict[str, typing.Any]]`
    :   List of refunds that have been applied to this charge.

    `review: list[str]`
    :   ID of the review object associated with this charge, if it was flagged for manual review.

    `shipping: list[dict[str, typing.Any]]`
    :   Shipping information for the charge, including recipient name, address, and tracking details.

    `source: list[dict[str, typing.Any]]`
    :   Deprecated payment source object used to create this charge.

    `source_transfer: list[str]`
    :   ID of the transfer from a source account if funds came from another Stripe account (Connect only).

    `statement_description: list[str]`
    :   Deprecated alias for statement_descriptor.

    `statement_descriptor: list[str]`
    :   Statement descriptor that overrides the account default for card charges, appearing on the customer's statement.

    `statement_descriptor_suffix: list[str]`
    :   Suffix concatenated to the account's statement descriptor prefix to form the complete descriptor on customer statements.

    `status: list[str]`
    :   Current status of the payment: 'succeeded' (completed), 'pending' (processing), or 'failed' (unsuccessful).

    `transfer_data: list[dict[str, typing.Any]]`
    :   Object containing destination and amount for transfers to connected accounts (Connect only).

    `transfer_group: list[str]`
    :   String identifier for grouping related charges and transfers together (Connect only).

    `updated: list[int]`
    :   Timestamp of the last update to this charge object.

<a id="ChargesKeywordCondition"></a>

`ChargesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.stripe.types.ChargesStringFilter`
    :   The type of the None singleton.

<a id="ChargesLikeCondition"></a>

`ChargesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.stripe.types.ChargesStringFilter`
    :   The type of the None singleton.

<a id="ChargesListParams"></a>

`ChargesListParams(*args, **kwargs)`
:   Parameters for charges.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: airbyte_agent_sdk.connectors.stripe.types.ChargesListParamsCreated`
    :   The type of the None singleton.

    `customer: str`
    :   The type of the None singleton.

    `ending_before: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `payment_intent: str`
    :   The type of the None singleton.

    `starting_after: str`
    :   The type of the None singleton.

<a id="ChargesListParamsCreated"></a>

`ChargesListParamsCreated(*args, **kwargs)`
:   Nested schema for ChargesListParams.created

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: int`
    :   The type of the None singleton.

    `gte: int`
    :   The type of the None singleton.

    `lt: int`
    :   The type of the None singleton.

    `lte: int`
    :   The type of the None singleton.

<a id="ChargesLtCondition"></a>

`ChargesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.stripe.types.ChargesSearchFilter`
    :   The type of the None singleton.

<a id="ChargesLteCondition"></a>

`ChargesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.stripe.types.ChargesSearchFilter`
    :   The type of the None singleton.

<a id="ChargesNeqCondition"></a>

`ChargesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.stripe.types.ChargesSearchFilter`
    :   The type of the None singleton.

<a id="ChargesNotCondition"></a>

`ChargesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.stripe.types.ChargesEqCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesNeqCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesGtCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesGteCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesLtCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesLteCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesInCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesLikeCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesContainsCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesNotCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesAndCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesOrCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesAnyCondition`
    :   The type of the None singleton.

<a id="ChargesOrCondition"></a>

`ChargesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.stripe.types.ChargesEqCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesNeqCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesGtCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesGteCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesLtCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesLteCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesInCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesLikeCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesContainsCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesNotCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesAndCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesOrCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesAnyCondition]`
    :   The type of the None singleton.

<a id="ChargesSearchFilter"></a>

`ChargesSearchFilter(*args, **kwargs)`
:   Available fields for filtering charges search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="ChargesSearchQuery"></a>

`ChargesSearchQuery(*args, **kwargs)`
:   Search query for charges entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.stripe.types.ChargesEqCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesNeqCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesGtCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesGteCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesLtCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesLteCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesInCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesLikeCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesContainsCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesNotCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesAndCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesOrCondition | airbyte_agent_sdk.connectors.stripe.types.ChargesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.stripe.types.ChargesSortFilter]`
    :   The type of the None singleton.

<a id="ChargesSortFilter"></a>

`ChargesSortFilter(*args, **kwargs)`
:   Available fields for sorting charges search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Literal['asc', 'desc']`
    :   Amount intended to be collected by this payment in the smallest currency unit (e.g., 100 cents for $1.00), supporting up to eight digits.

    `amount_captured: Literal['asc', 'desc']`
    :   Amount that was actually captured from this charge.

    `amount_refunded: Literal['asc', 'desc']`
    :   Amount that has been refunded back to the customer.

    `amount_updates: Literal['asc', 'desc']`
    :   Updates to the amount that have been made during the charge lifecycle.

    `application: Literal['asc', 'desc']`
    :   ID of the application that created this charge (Connect only).

    `application_fee: Literal['asc', 'desc']`
    :   ID of the application fee associated with this charge (Connect only).

    `application_fee_amount: Literal['asc', 'desc']`
    :   The amount of the application fee deducted from this charge (Connect only).

    `balance_transaction: Literal['asc', 'desc']`
    :   ID of the balance transaction that describes the impact of this charge on your account balance (excluding refunds or disputes).

    `billing_details: Literal['asc', 'desc']`
    :   Billing information associated with the payment method at the time of the transaction, including name, email, phone, and address.

    `calculated_statement_descriptor: Literal['asc', 'desc']`
    :   The full statement descriptor that appears on the customer's credit card statement, combining prefix and suffix.

    `captured: Literal['asc', 'desc']`
    :   Whether the charge has been captured and funds transferred to your account.

    `card: Literal['asc', 'desc']`
    :   Deprecated card object containing payment card details if a card was used.

    `created: Literal['asc', 'desc']`
    :   Timestamp indicating when the charge was created.

    `currency: Literal['asc', 'desc']`
    :   Three-letter ISO currency code in lowercase (e.g., 'usd', 'eur') for the charge amount.

    `customer: Literal['asc', 'desc']`
    :   ID of the customer this charge is for, if one exists.

    `description: Literal['asc', 'desc']`
    :   An arbitrary string attached to the charge, often useful for displaying to users or internal reference.

    `destination: Literal['asc', 'desc']`
    :   ID of the destination account where funds are transferred (Connect only).

    `dispute: Literal['asc', 'desc']`
    :   ID of the dispute object if the charge has been disputed.

    `disputed: Literal['asc', 'desc']`
    :   Whether the charge has been disputed by the customer with their card issuer.

    `failure_balance_transaction: Literal['asc', 'desc']`
    :   ID of the balance transaction that describes the reversal of funds if the charge failed.

    `failure_code: Literal['asc', 'desc']`
    :   Error code explaining the reason for charge failure, if applicable.

    `failure_message: Literal['asc', 'desc']`
    :   Human-readable message providing more details about why the charge failed.

    `fraud_details: Literal['asc', 'desc']`
    :   Information about fraud assessments and user reports related to this charge.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the charge, used to link transactions across other records.

    `invoice: Literal['asc', 'desc']`
    :   ID of the invoice this charge is for, if the charge was created by invoicing.

    `livemode: Literal['asc', 'desc']`
    :   Whether the charge occurred in live mode (true) or test mode (false).

    `metadata: Literal['asc', 'desc']`
    :   Key-value pairs for storing additional structured information about the charge, useful for internal tracking.

    `object_: Literal['asc', 'desc']`
    :   String representing the object type, always 'charge' for charge objects.

    `on_behalf_of: Literal['asc', 'desc']`
    :   ID of the account on whose behalf the charge was made (Connect only).

    `order: Literal['asc', 'desc']`
    :   Deprecated field for order information associated with this charge.

    `outcome: Literal['asc', 'desc']`
    :   Details about the outcome of the charge, including network status, risk assessment, and reason codes.

    `paid: Literal['asc', 'desc']`
    :   Whether the charge succeeded and funds were successfully collected.

    `payment_intent: Literal['asc', 'desc']`
    :   ID of the PaymentIntent associated with this charge, if one exists.

    `payment_method: Literal['asc', 'desc']`
    :   ID of the payment method used for this charge.

    `payment_method_details: Literal['asc', 'desc']`
    :   Details about the payment method at the time of the transaction, including card brand, network, and authentication results.

    `receipt_email: Literal['asc', 'desc']`
    :   Email address to which the receipt for this charge was sent.

    `receipt_number: Literal['asc', 'desc']`
    :   Receipt number that appears on email receipts sent for this charge.

    `receipt_url: Literal['asc', 'desc']`
    :   URL to a hosted receipt page for this charge, viewable by the customer.

    `refunded: Literal['asc', 'desc']`
    :   Whether the charge has been fully refunded (partial refunds will still show as false).

    `refunds: Literal['asc', 'desc']`
    :   List of refunds that have been applied to this charge.

    `review: Literal['asc', 'desc']`
    :   ID of the review object associated with this charge, if it was flagged for manual review.

    `shipping: Literal['asc', 'desc']`
    :   Shipping information for the charge, including recipient name, address, and tracking details.

    `source: Literal['asc', 'desc']`
    :   Deprecated payment source object used to create this charge.

    `source_transfer: Literal['asc', 'desc']`
    :   ID of the transfer from a source account if funds came from another Stripe account (Connect only).

    `statement_description: Literal['asc', 'desc']`
    :   Deprecated alias for statement_descriptor.

    `statement_descriptor: Literal['asc', 'desc']`
    :   Statement descriptor that overrides the account default for card charges, appearing on the customer's statement.

    `statement_descriptor_suffix: Literal['asc', 'desc']`
    :   Suffix concatenated to the account's statement descriptor prefix to form the complete descriptor on customer statements.

    `status: Literal['asc', 'desc']`
    :   Current status of the payment: 'succeeded' (completed), 'pending' (processing), or 'failed' (unsuccessful).

    `transfer_data: Literal['asc', 'desc']`
    :   Object containing destination and amount for transfers to connected accounts (Connect only).

    `transfer_group: Literal['asc', 'desc']`
    :   String identifier for grouping related charges and transfers together (Connect only).

    `updated: Literal['asc', 'desc']`
    :   Timestamp of the last update to this charge object.

<a id="ChargesStringFilter"></a>

`ChargesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: str`
    :   Amount intended to be collected by this payment in the smallest currency unit (e.g., 100 cents for $1.00), supporting up to eight digits.

    `amount_captured: str`
    :   Amount that was actually captured from this charge.

    `amount_refunded: str`
    :   Amount that has been refunded back to the customer.

    `amount_updates: str`
    :   Updates to the amount that have been made during the charge lifecycle.

    `application: str`
    :   ID of the application that created this charge (Connect only).

    `application_fee: str`
    :   ID of the application fee associated with this charge (Connect only).

    `application_fee_amount: str`
    :   The amount of the application fee deducted from this charge (Connect only).

    `balance_transaction: str`
    :   ID of the balance transaction that describes the impact of this charge on your account balance (excluding refunds or disputes).

    `billing_details: str`
    :   Billing information associated with the payment method at the time of the transaction, including name, email, phone, and address.

    `calculated_statement_descriptor: str`
    :   The full statement descriptor that appears on the customer's credit card statement, combining prefix and suffix.

    `captured: str`
    :   Whether the charge has been captured and funds transferred to your account.

    `card: str`
    :   Deprecated card object containing payment card details if a card was used.

    `created: str`
    :   Timestamp indicating when the charge was created.

    `currency: str`
    :   Three-letter ISO currency code in lowercase (e.g., 'usd', 'eur') for the charge amount.

    `customer: str`
    :   ID of the customer this charge is for, if one exists.

    `description: str`
    :   An arbitrary string attached to the charge, often useful for displaying to users or internal reference.

    `destination: str`
    :   ID of the destination account where funds are transferred (Connect only).

    `dispute: str`
    :   ID of the dispute object if the charge has been disputed.

    `disputed: str`
    :   Whether the charge has been disputed by the customer with their card issuer.

    `failure_balance_transaction: str`
    :   ID of the balance transaction that describes the reversal of funds if the charge failed.

    `failure_code: str`
    :   Error code explaining the reason for charge failure, if applicable.

    `failure_message: str`
    :   Human-readable message providing more details about why the charge failed.

    `fraud_details: str`
    :   Information about fraud assessments and user reports related to this charge.

    `id: str`
    :   Unique identifier for the charge, used to link transactions across other records.

    `invoice: str`
    :   ID of the invoice this charge is for, if the charge was created by invoicing.

    `livemode: str`
    :   Whether the charge occurred in live mode (true) or test mode (false).

    `metadata: str`
    :   Key-value pairs for storing additional structured information about the charge, useful for internal tracking.

    `object_: str`
    :   String representing the object type, always 'charge' for charge objects.

    `on_behalf_of: str`
    :   ID of the account on whose behalf the charge was made (Connect only).

    `order: str`
    :   Deprecated field for order information associated with this charge.

    `outcome: str`
    :   Details about the outcome of the charge, including network status, risk assessment, and reason codes.

    `paid: str`
    :   Whether the charge succeeded and funds were successfully collected.

    `payment_intent: str`
    :   ID of the PaymentIntent associated with this charge, if one exists.

    `payment_method: str`
    :   ID of the payment method used for this charge.

    `payment_method_details: str`
    :   Details about the payment method at the time of the transaction, including card brand, network, and authentication results.

    `receipt_email: str`
    :   Email address to which the receipt for this charge was sent.

    `receipt_number: str`
    :   Receipt number that appears on email receipts sent for this charge.

    `receipt_url: str`
    :   URL to a hosted receipt page for this charge, viewable by the customer.

    `refunded: str`
    :   Whether the charge has been fully refunded (partial refunds will still show as false).

    `refunds: str`
    :   List of refunds that have been applied to this charge.

    `review: str`
    :   ID of the review object associated with this charge, if it was flagged for manual review.

    `shipping: str`
    :   Shipping information for the charge, including recipient name, address, and tracking details.

    `source: str`
    :   Deprecated payment source object used to create this charge.

    `source_transfer: str`
    :   ID of the transfer from a source account if funds came from another Stripe account (Connect only).

    `statement_description: str`
    :   Deprecated alias for statement_descriptor.

    `statement_descriptor: str`
    :   Statement descriptor that overrides the account default for card charges, appearing on the customer's statement.

    `statement_descriptor_suffix: str`
    :   Suffix concatenated to the account's statement descriptor prefix to form the complete descriptor on customer statements.

    `status: str`
    :   Current status of the payment: 'succeeded' (completed), 'pending' (processing), or 'failed' (unsuccessful).

    `transfer_data: str`
    :   Object containing destination and amount for transfers to connected accounts (Connect only).

    `transfer_group: str`
    :   String identifier for grouping related charges and transfers together (Connect only).

    `updated: str`
    :   Timestamp of the last update to this charge object.

<a id="CustomersAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.stripe.types.CustomersEqCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersNeqCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersGtCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersGteCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersLtCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersLteCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersInCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersLikeCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersContainsCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersNotCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersAndCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersOrCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersAnyCondition]`
    :   The type of the None singleton.

<a id="CustomersAnyCondition"></a>

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

    `any: airbyte_agent_sdk.connectors.stripe.types.CustomersAnyValueFilter`
    :   The type of the None singleton.

<a id="CustomersAnyValueFilter"></a>

`CustomersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_balance: Any`
    :   Current balance value representing funds owed by or to the customer.

    `address: Any`
    :   The customer's address information including line1, line2, city, state, postal code, and country.

    `balance: Any`
    :   Current balance (positive or negative) that is automatically applied to the customer's next invoice.

    `cards: Any`
    :   Card payment methods associated with the customer account.

    `created: Any`
    :   Timestamp indicating when the customer object was created.

    `currency: Any`
    :   Three-letter ISO currency code representing the customer's default currency.

    `default_card: Any`
    :   The default card to be used for charges when no specific payment method is provided.

    `default_source: Any`
    :   The default payment source (card or bank account) for the customer.

    `delinquent: Any`
    :   Boolean indicating whether the customer is currently delinquent on payments.

    `description: Any`
    :   An arbitrary string attached to the customer, often useful for displaying to users.

    `discount: Any`
    :   Discount object describing any active discount applied to the customer.

    `email: Any`
    :   The customer's email address for communication and tracking purposes.

    `id: Any`
    :   Unique identifier for the customer object.

    `invoice_prefix: Any`
    :   The prefix for invoice numbers generated for this customer.

    `invoice_settings: Any`
    :   Customer's invoice-related settings including default payment method and custom fields.

    `is_deleted: Any`
    :   Boolean indicating whether the customer has been deleted.

    `livemode: Any`
    :   Boolean indicating whether the object exists in live mode or test mode.

    `metadata: Any`
    :   Set of key-value pairs for storing additional structured information about the customer.

    `name: Any`
    :   The customer's full name or business name.

    `next_invoice_sequence: Any`
    :   The sequence number for the next invoice generated for this customer.

    `object_: Any`
    :   String representing the object type, always 'customer'.

    `phone: Any`
    :   The customer's phone number.

    `preferred_locales: Any`
    :   Array of preferred locales for the customer, used for invoice and receipt localization.

    `shipping: Any`
    :   Mailing and shipping address for the customer, appears on invoices emailed to the customer.

    `sources: Any`
    :   Payment sources (cards, bank accounts) attached to the customer for making payments.

    `subscriptions: Any`
    :   List of active subscriptions associated with the customer.

    `tax_exempt: Any`
    :   Describes the customer's tax exemption status (none, exempt, or reverse).

    `tax_info: Any`
    :   Tax identification information for the customer.

    `tax_info_verification: Any`
    :   Verification status of the customer's tax information.

    `test_clock: Any`
    :   ID of the test clock associated with this customer for testing time-dependent scenarios.

    `updated: Any`
    :   Timestamp indicating when the customer object was last updated.

<a id="CustomersApiSearchParams"></a>

`CustomersApiSearchParams(*args, **kwargs)`
:   Parameters for customers.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `page: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="CustomersContainsCondition"></a>

`CustomersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.stripe.types.CustomersAnyValueFilter`
    :   The type of the None singleton.

<a id="CustomersCreateParams"></a>

`CustomersCreateParams(*args, **kwargs)`
:   Parameters for customers.create operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="CustomersDeleteParams"></a>

`CustomersDeleteParams(*args, **kwargs)`
:   Parameters for customers.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CustomersEqCondition"></a>

`CustomersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.stripe.types.CustomersSearchFilter`
    :   The type of the None singleton.

<a id="CustomersFuzzyCondition"></a>

`CustomersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.stripe.types.CustomersStringFilter`
    :   The type of the None singleton.

<a id="CustomersGetParams"></a>

`CustomersGetParams(*args, **kwargs)`
:   Parameters for customers.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CustomersGtCondition"></a>

`CustomersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.stripe.types.CustomersSearchFilter`
    :   The type of the None singleton.

<a id="CustomersGteCondition"></a>

`CustomersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.stripe.types.CustomersSearchFilter`
    :   The type of the None singleton.

<a id="CustomersInCondition"></a>

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

    `in: airbyte_agent_sdk.connectors.stripe.types.CustomersInFilter`
    :   The type of the None singleton.

<a id="CustomersInFilter"></a>

`CustomersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_balance: list[int]`
    :   Current balance value representing funds owed by or to the customer.

    `address: list[dict[str, typing.Any]]`
    :   The customer's address information including line1, line2, city, state, postal code, and country.

    `balance: list[int]`
    :   Current balance (positive or negative) that is automatically applied to the customer's next invoice.

    `cards: list[list[typing.Any]]`
    :   Card payment methods associated with the customer account.

    `created: list[int]`
    :   Timestamp indicating when the customer object was created.

    `currency: list[str]`
    :   Three-letter ISO currency code representing the customer's default currency.

    `default_card: list[str]`
    :   The default card to be used for charges when no specific payment method is provided.

    `default_source: list[str]`
    :   The default payment source (card or bank account) for the customer.

    `delinquent: list[bool]`
    :   Boolean indicating whether the customer is currently delinquent on payments.

    `description: list[str]`
    :   An arbitrary string attached to the customer, often useful for displaying to users.

    `discount: list[dict[str, typing.Any]]`
    :   Discount object describing any active discount applied to the customer.

    `email: list[str]`
    :   The customer's email address for communication and tracking purposes.

    `id: list[str]`
    :   Unique identifier for the customer object.

    `invoice_prefix: list[str]`
    :   The prefix for invoice numbers generated for this customer.

    `invoice_settings: list[dict[str, typing.Any]]`
    :   Customer's invoice-related settings including default payment method and custom fields.

    `is_deleted: list[bool]`
    :   Boolean indicating whether the customer has been deleted.

    `livemode: list[bool]`
    :   Boolean indicating whether the object exists in live mode or test mode.

    `metadata: list[dict[str, typing.Any]]`
    :   Set of key-value pairs for storing additional structured information about the customer.

    `name: list[str]`
    :   The customer's full name or business name.

    `next_invoice_sequence: list[int]`
    :   The sequence number for the next invoice generated for this customer.

    `object_: list[str]`
    :   String representing the object type, always 'customer'.

    `phone: list[str]`
    :   The customer's phone number.

    `preferred_locales: list[list[typing.Any]]`
    :   Array of preferred locales for the customer, used for invoice and receipt localization.

    `shipping: list[dict[str, typing.Any]]`
    :   Mailing and shipping address for the customer, appears on invoices emailed to the customer.

    `sources: list[str]`
    :   Payment sources (cards, bank accounts) attached to the customer for making payments.

    `subscriptions: list[dict[str, typing.Any]]`
    :   List of active subscriptions associated with the customer.

    `tax_exempt: list[str]`
    :   Describes the customer's tax exemption status (none, exempt, or reverse).

    `tax_info: list[str]`
    :   Tax identification information for the customer.

    `tax_info_verification: list[str]`
    :   Verification status of the customer's tax information.

    `test_clock: list[str]`
    :   ID of the test clock associated with this customer for testing time-dependent scenarios.

    `updated: list[int]`
    :   Timestamp indicating when the customer object was last updated.

<a id="CustomersKeywordCondition"></a>

`CustomersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.stripe.types.CustomersStringFilter`
    :   The type of the None singleton.

<a id="CustomersLikeCondition"></a>

`CustomersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.stripe.types.CustomersStringFilter`
    :   The type of the None singleton.

<a id="CustomersListParams"></a>

`CustomersListParams(*args, **kwargs)`
:   Parameters for customers.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: airbyte_agent_sdk.connectors.stripe.types.CustomersListParamsCreated`
    :   The type of the None singleton.

    `email: str`
    :   The type of the None singleton.

    `ending_before: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `starting_after: str`
    :   The type of the None singleton.

<a id="CustomersListParamsCreated"></a>

`CustomersListParamsCreated(*args, **kwargs)`
:   Nested schema for CustomersListParams.created

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: int`
    :   The type of the None singleton.

    `gte: int`
    :   The type of the None singleton.

    `lt: int`
    :   The type of the None singleton.

    `lte: int`
    :   The type of the None singleton.

<a id="CustomersLtCondition"></a>

`CustomersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.stripe.types.CustomersSearchFilter`
    :   The type of the None singleton.

<a id="CustomersLteCondition"></a>

`CustomersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.stripe.types.CustomersSearchFilter`
    :   The type of the None singleton.

<a id="CustomersNeqCondition"></a>

`CustomersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.stripe.types.CustomersSearchFilter`
    :   The type of the None singleton.

<a id="CustomersNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.stripe.types.CustomersEqCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersNeqCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersGtCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersGteCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersLtCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersLteCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersInCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersLikeCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersContainsCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersNotCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersAndCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersOrCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersAnyCondition`
    :   The type of the None singleton.

<a id="CustomersOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.stripe.types.CustomersEqCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersNeqCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersGtCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersGteCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersLtCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersLteCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersInCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersLikeCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersContainsCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersNotCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersAndCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersOrCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersAnyCondition]`
    :   The type of the None singleton.

<a id="CustomersSearchFilter"></a>

`CustomersSearchFilter(*args, **kwargs)`
:   Available fields for filtering customers search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="CustomersSearchQuery"></a>

`CustomersSearchQuery(*args, **kwargs)`
:   Search query for customers entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.stripe.types.CustomersEqCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersNeqCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersGtCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersGteCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersLtCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersLteCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersInCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersLikeCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersContainsCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersNotCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersAndCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersOrCondition | airbyte_agent_sdk.connectors.stripe.types.CustomersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.stripe.types.CustomersSortFilter]`
    :   The type of the None singleton.

<a id="CustomersSortFilter"></a>

`CustomersSortFilter(*args, **kwargs)`
:   Available fields for sorting customers search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_balance: Literal['asc', 'desc']`
    :   Current balance value representing funds owed by or to the customer.

    `address: Literal['asc', 'desc']`
    :   The customer's address information including line1, line2, city, state, postal code, and country.

    `balance: Literal['asc', 'desc']`
    :   Current balance (positive or negative) that is automatically applied to the customer's next invoice.

    `cards: Literal['asc', 'desc']`
    :   Card payment methods associated with the customer account.

    `created: Literal['asc', 'desc']`
    :   Timestamp indicating when the customer object was created.

    `currency: Literal['asc', 'desc']`
    :   Three-letter ISO currency code representing the customer's default currency.

    `default_card: Literal['asc', 'desc']`
    :   The default card to be used for charges when no specific payment method is provided.

    `default_source: Literal['asc', 'desc']`
    :   The default payment source (card or bank account) for the customer.

    `delinquent: Literal['asc', 'desc']`
    :   Boolean indicating whether the customer is currently delinquent on payments.

    `description: Literal['asc', 'desc']`
    :   An arbitrary string attached to the customer, often useful for displaying to users.

    `discount: Literal['asc', 'desc']`
    :   Discount object describing any active discount applied to the customer.

    `email: Literal['asc', 'desc']`
    :   The customer's email address for communication and tracking purposes.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the customer object.

    `invoice_prefix: Literal['asc', 'desc']`
    :   The prefix for invoice numbers generated for this customer.

    `invoice_settings: Literal['asc', 'desc']`
    :   Customer's invoice-related settings including default payment method and custom fields.

    `is_deleted: Literal['asc', 'desc']`
    :   Boolean indicating whether the customer has been deleted.

    `livemode: Literal['asc', 'desc']`
    :   Boolean indicating whether the object exists in live mode or test mode.

    `metadata: Literal['asc', 'desc']`
    :   Set of key-value pairs for storing additional structured information about the customer.

    `name: Literal['asc', 'desc']`
    :   The customer's full name or business name.

    `next_invoice_sequence: Literal['asc', 'desc']`
    :   The sequence number for the next invoice generated for this customer.

    `object_: Literal['asc', 'desc']`
    :   String representing the object type, always 'customer'.

    `phone: Literal['asc', 'desc']`
    :   The customer's phone number.

    `preferred_locales: Literal['asc', 'desc']`
    :   Array of preferred locales for the customer, used for invoice and receipt localization.

    `shipping: Literal['asc', 'desc']`
    :   Mailing and shipping address for the customer, appears on invoices emailed to the customer.

    `sources: Literal['asc', 'desc']`
    :   Payment sources (cards, bank accounts) attached to the customer for making payments.

    `subscriptions: Literal['asc', 'desc']`
    :   List of active subscriptions associated with the customer.

    `tax_exempt: Literal['asc', 'desc']`
    :   Describes the customer's tax exemption status (none, exempt, or reverse).

    `tax_info: Literal['asc', 'desc']`
    :   Tax identification information for the customer.

    `tax_info_verification: Literal['asc', 'desc']`
    :   Verification status of the customer's tax information.

    `test_clock: Literal['asc', 'desc']`
    :   ID of the test clock associated with this customer for testing time-dependent scenarios.

    `updated: Literal['asc', 'desc']`
    :   Timestamp indicating when the customer object was last updated.

<a id="CustomersStringFilter"></a>

`CustomersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_balance: str`
    :   Current balance value representing funds owed by or to the customer.

    `address: str`
    :   The customer's address information including line1, line2, city, state, postal code, and country.

    `balance: str`
    :   Current balance (positive or negative) that is automatically applied to the customer's next invoice.

    `cards: str`
    :   Card payment methods associated with the customer account.

    `created: str`
    :   Timestamp indicating when the customer object was created.

    `currency: str`
    :   Three-letter ISO currency code representing the customer's default currency.

    `default_card: str`
    :   The default card to be used for charges when no specific payment method is provided.

    `default_source: str`
    :   The default payment source (card or bank account) for the customer.

    `delinquent: str`
    :   Boolean indicating whether the customer is currently delinquent on payments.

    `description: str`
    :   An arbitrary string attached to the customer, often useful for displaying to users.

    `discount: str`
    :   Discount object describing any active discount applied to the customer.

    `email: str`
    :   The customer's email address for communication and tracking purposes.

    `id: str`
    :   Unique identifier for the customer object.

    `invoice_prefix: str`
    :   The prefix for invoice numbers generated for this customer.

    `invoice_settings: str`
    :   Customer's invoice-related settings including default payment method and custom fields.

    `is_deleted: str`
    :   Boolean indicating whether the customer has been deleted.

    `livemode: str`
    :   Boolean indicating whether the object exists in live mode or test mode.

    `metadata: str`
    :   Set of key-value pairs for storing additional structured information about the customer.

    `name: str`
    :   The customer's full name or business name.

    `next_invoice_sequence: str`
    :   The sequence number for the next invoice generated for this customer.

    `object_: str`
    :   String representing the object type, always 'customer'.

    `phone: str`
    :   The customer's phone number.

    `preferred_locales: str`
    :   Array of preferred locales for the customer, used for invoice and receipt localization.

    `shipping: str`
    :   Mailing and shipping address for the customer, appears on invoices emailed to the customer.

    `sources: str`
    :   Payment sources (cards, bank accounts) attached to the customer for making payments.

    `subscriptions: str`
    :   List of active subscriptions associated with the customer.

    `tax_exempt: str`
    :   Describes the customer's tax exemption status (none, exempt, or reverse).

    `tax_info: str`
    :   Tax identification information for the customer.

    `tax_info_verification: str`
    :   Verification status of the customer's tax information.

    `test_clock: str`
    :   ID of the test clock associated with this customer for testing time-dependent scenarios.

    `updated: str`
    :   Timestamp indicating when the customer object was last updated.

<a id="CustomersUpdateParams"></a>

`CustomersUpdateParams(*args, **kwargs)`
:   Parameters for customers.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="DisputesGetParams"></a>

`DisputesGetParams(*args, **kwargs)`
:   Parameters for disputes.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="DisputesListParams"></a>

`DisputesListParams(*args, **kwargs)`
:   Parameters for disputes.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `charge: str`
    :   The type of the None singleton.

    `created: airbyte_agent_sdk.connectors.stripe.types.DisputesListParamsCreated`
    :   The type of the None singleton.

    `ending_before: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `payment_intent: str`
    :   The type of the None singleton.

    `starting_after: str`
    :   The type of the None singleton.

<a id="DisputesListParamsCreated"></a>

`DisputesListParamsCreated(*args, **kwargs)`
:   Nested schema for DisputesListParams.created

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: int`
    :   The type of the None singleton.

    `gte: int`
    :   The type of the None singleton.

    `lt: int`
    :   The type of the None singleton.

    `lte: int`
    :   The type of the None singleton.

<a id="InvoicesAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.stripe.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesInCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesLikeCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesAnyCondition]`
    :   The type of the None singleton.

<a id="InvoicesAnyCondition"></a>

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

    `any: airbyte_agent_sdk.connectors.stripe.types.InvoicesAnyValueFilter`
    :   The type of the None singleton.

<a id="InvoicesAnyValueFilter"></a>

`InvoicesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_country: Any`
    :   The country of the business associated with this invoice, commonly used to display localized content.

    `account_name: Any`
    :   The public name of the business associated with this invoice.

    `account_tax_ids: Any`
    :   Tax IDs of the account associated with this invoice.

    `amount_due: Any`
    :   Total amount, in smallest currency unit, that is due and owed by the customer.

    `amount_paid: Any`
    :   Total amount, in smallest currency unit, that has been paid by the customer.

    `amount_remaining: Any`
    :   The difference between amount_due and amount_paid, representing the outstanding balance.

    `amount_shipping: Any`
    :   Total amount of shipping costs on the invoice.

    `application: Any`
    :   ID of the Connect application that created this invoice.

    `application_fee: Any`
    :   Amount of application fee charged for this invoice in a Connect scenario.

    `application_fee_amount: Any`
    :   The fee in smallest currency unit that is collected by the application in a Connect scenario.

    `attempt_count: Any`
    :   Number of payment attempts made for this invoice.

    `attempted: Any`
    :   Whether an attempt has been made to pay the invoice.

    `auto_advance: Any`
    :   Controls whether Stripe performs automatic collection of the invoice.

    `automatic_tax: Any`
    :   Settings and status for automatic tax calculation on this invoice.

    `billing: Any`
    :   Billing method used for the invoice (charge_automatically or send_invoice).

    `billing_reason: Any`
    :   Indicates the reason why the invoice was created (subscription_cycle, manual, etc.).

    `charge: Any`
    :   ID of the latest charge generated for this invoice, if any.

    `closed: Any`
    :   Whether the invoice has been marked as closed and no longer open for collection.

    `collection_method: Any`
    :   Method by which the invoice is collected: charge_automatically or send_invoice.

    `created: Any`
    :   Timestamp indicating when the invoice was created.

    `currency: Any`
    :   Three-letter ISO currency code in which the invoice is denominated.

    `custom_fields: Any`
    :   Custom fields displayed on the invoice as specified by the account.

    `customer: Any`
    :   The customer object or ID associated with this invoice.

    `customer_address: Any`
    :   The customer's address at the time the invoice was finalized.

    `customer_email: Any`
    :   The customer's email address at the time the invoice was finalized.

    `customer_name: Any`
    :   The customer's name at the time the invoice was finalized.

    `customer_phone: Any`
    :   The customer's phone number at the time the invoice was finalized.

    `customer_shipping: Any`
    :   The customer's shipping information at the time the invoice was finalized.

    `customer_tax_exempt: Any`
    :   The customer's tax exempt status at the time the invoice was finalized.

    `customer_tax_ids: Any`
    :   The customer's tax IDs at the time the invoice was finalized.

    `default_payment_method: Any`
    :   Default payment method for the invoice, used if no other method is specified.

    `default_source: Any`
    :   Default payment source for the invoice if no payment method is set.

    `default_tax_rates: Any`
    :   The tax rates applied to the invoice by default.

    `description: Any`
    :   An arbitrary string attached to the invoice, often displayed to customers.

    `discount: Any`
    :   The discount object applied to the invoice, if any.

    `discounts: Any`
    :   Array of discount IDs or objects currently applied to this invoice.

    `due_date: Any`
    :   The date by which payment on this invoice is due, if the invoice is not auto-collected.

    `effective_at: Any`
    :   Timestamp when the invoice becomes effective and finalized for payment.

    `ending_balance: Any`
    :   The customer's ending account balance after this invoice is finalized.

    `footer: Any`
    :   Footer text displayed on the invoice.

    `forgiven: Any`
    :   Whether the invoice has been forgiven and is considered paid without actual payment.

    `from_invoice: Any`
    :   Details about the invoice this invoice was created from, if applicable.

    `hosted_invoice_url: Any`
    :   URL for the hosted invoice page where customers can view and pay the invoice.

    `id: Any`
    :   Unique identifier for the invoice object.

    `invoice_pdf: Any`
    :   URL for the PDF version of the invoice.

    `is_deleted: Any`
    :   Indicates whether this invoice has been deleted.

    `issuer: Any`
    :   Details about the entity issuing the invoice.

    `last_finalization_error: Any`
    :   The error encountered during the last finalization attempt, if any.

    `latest_revision: Any`
    :   The latest revision of the invoice, if revisions are enabled.

    `lines: Any`
    :   The individual line items that make up the invoice, representing products, services, or fees.

    `livemode: Any`
    :   Indicates whether the invoice exists in live mode (true) or test mode (false).

    `metadata: Any`
    :   Key-value pairs for storing additional structured information about the invoice.

    `next_payment_attempt: Any`
    :   Timestamp of the next automatic payment attempt for this invoice, if applicable.

    `number: Any`
    :   A unique, human-readable identifier for this invoice, often shown to customers.

    `object_: Any`
    :   String representing the object type, always 'invoice'.

    `on_behalf_of: Any`
    :   The account on behalf of which the invoice is being created, used in Connect scenarios.

    `paid: Any`
    :   Whether the invoice has been paid in full.

    `paid_out_of_band: Any`
    :   Whether payment was made outside of Stripe and manually marked as paid.

    `payment: Any`
    :   ID of the payment associated with this invoice, if any.

    `payment_intent: Any`
    :   The PaymentIntent associated with this invoice for processing payment.

    `payment_settings: Any`
    :   Configuration settings for how payment should be collected on this invoice.

    `period_end: Any`
    :   End date of the billing period covered by this invoice.

    `period_start: Any`
    :   Start date of the billing period covered by this invoice.

    `post_payment_credit_notes_amount: Any`
    :   Total amount of credit notes issued after the invoice was paid.

    `pre_payment_credit_notes_amount: Any`
    :   Total amount of credit notes applied before payment was attempted.

    `quote: Any`
    :   The quote from which this invoice was generated, if applicable.

    `receipt_number: Any`
    :   The receipt number displayed on the invoice, if available.

    `rendering: Any`
    :   Settings that control how the invoice is rendered for display.

    `rendering_options: Any`
    :   Options for customizing the visual rendering of the invoice.

    `shipping_cost: Any`
    :   Total cost of shipping charges included in the invoice.

    `shipping_details: Any`
    :   Detailed shipping information for the invoice, including address and carrier.

    `starting_balance: Any`
    :   The customer's starting account balance at the beginning of the billing period.

    `statement_description: Any`
    :   Extra information about the invoice that appears on the customer's credit card statement.

    `statement_descriptor: Any`
    :   A dynamic descriptor that appears on the customer's credit card statement for this invoice.

    `status: Any`
    :   The status of the invoice: draft, open, paid, void, or uncollectible.

    `status_transitions: Any`
    :   Timestamps tracking when the invoice transitioned between different statuses.

    `subscription: Any`
    :   The subscription this invoice was generated for, if applicable.

    `subscription_details: Any`
    :   Additional details about the subscription associated with this invoice.

    `subtotal: Any`
    :   Total of all line items before discounts or tax are applied.

    `subtotal_excluding_tax: Any`
    :   The subtotal amount excluding any tax calculations.

    `tax: Any`
    :   Total tax amount applied to the invoice.

    `tax_percent: Any`
    :   The percentage of tax applied to the invoice (deprecated, use total_tax_amounts instead).

    `test_clock: Any`
    :   ID of the test clock this invoice belongs to, used for testing time-dependent billing.

    `total: Any`
    :   Total amount of the invoice after all line items, discounts, and taxes are calculated.

    `total_discount_amounts: Any`
    :   Array of the total discount amounts applied, broken down by discount.

    `total_excluding_tax: Any`
    :   Total amount of the invoice excluding all tax calculations.

    `total_tax_amounts: Any`
    :   Array of tax amounts applied to the invoice, broken down by tax rate.

    `transfer_data: Any`
    :   Information about the transfer of funds associated with this invoice in Connect scenarios.

    `updated: Any`
    :   Timestamp indicating when the invoice was last updated.

    `webhooks_delivered_at: Any`
    :   Timestamp indicating when webhooks for this invoice were successfully delivered.

<a id="InvoicesApiSearchParams"></a>

`InvoicesApiSearchParams(*args, **kwargs)`
:   Parameters for invoices.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `page: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="InvoicesContainsCondition"></a>

`InvoicesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.stripe.types.InvoicesAnyValueFilter`
    :   The type of the None singleton.

<a id="InvoicesEqCondition"></a>

`InvoicesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.stripe.types.InvoicesSearchFilter`
    :   The type of the None singleton.

<a id="InvoicesFuzzyCondition"></a>

`InvoicesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.stripe.types.InvoicesStringFilter`
    :   The type of the None singleton.

<a id="InvoicesGetParams"></a>

`InvoicesGetParams(*args, **kwargs)`
:   Parameters for invoices.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="InvoicesGtCondition"></a>

`InvoicesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.stripe.types.InvoicesSearchFilter`
    :   The type of the None singleton.

<a id="InvoicesGteCondition"></a>

`InvoicesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.stripe.types.InvoicesSearchFilter`
    :   The type of the None singleton.

<a id="InvoicesInCondition"></a>

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

    `in: airbyte_agent_sdk.connectors.stripe.types.InvoicesInFilter`
    :   The type of the None singleton.

<a id="InvoicesInFilter"></a>

`InvoicesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_country: list[str]`
    :   The country of the business associated with this invoice, commonly used to display localized content.

    `account_name: list[str]`
    :   The public name of the business associated with this invoice.

    `account_tax_ids: list[list[typing.Any]]`
    :   Tax IDs of the account associated with this invoice.

    `amount_due: list[int]`
    :   Total amount, in smallest currency unit, that is due and owed by the customer.

    `amount_paid: list[int]`
    :   Total amount, in smallest currency unit, that has been paid by the customer.

    `amount_remaining: list[int]`
    :   The difference between amount_due and amount_paid, representing the outstanding balance.

    `amount_shipping: list[int]`
    :   Total amount of shipping costs on the invoice.

    `application: list[str]`
    :   ID of the Connect application that created this invoice.

    `application_fee: list[int]`
    :   Amount of application fee charged for this invoice in a Connect scenario.

    `application_fee_amount: list[int]`
    :   The fee in smallest currency unit that is collected by the application in a Connect scenario.

    `attempt_count: list[int]`
    :   Number of payment attempts made for this invoice.

    `attempted: list[bool]`
    :   Whether an attempt has been made to pay the invoice.

    `auto_advance: list[bool]`
    :   Controls whether Stripe performs automatic collection of the invoice.

    `automatic_tax: list[dict[str, typing.Any]]`
    :   Settings and status for automatic tax calculation on this invoice.

    `billing: list[str]`
    :   Billing method used for the invoice (charge_automatically or send_invoice).

    `billing_reason: list[str]`
    :   Indicates the reason why the invoice was created (subscription_cycle, manual, etc.).

    `charge: list[str]`
    :   ID of the latest charge generated for this invoice, if any.

    `closed: list[bool]`
    :   Whether the invoice has been marked as closed and no longer open for collection.

    `collection_method: list[str]`
    :   Method by which the invoice is collected: charge_automatically or send_invoice.

    `created: list[int]`
    :   Timestamp indicating when the invoice was created.

    `currency: list[str]`
    :   Three-letter ISO currency code in which the invoice is denominated.

    `custom_fields: list[list[typing.Any]]`
    :   Custom fields displayed on the invoice as specified by the account.

    `customer: list[str]`
    :   The customer object or ID associated with this invoice.

    `customer_address: list[dict[str, typing.Any]]`
    :   The customer's address at the time the invoice was finalized.

    `customer_email: list[str]`
    :   The customer's email address at the time the invoice was finalized.

    `customer_name: list[str]`
    :   The customer's name at the time the invoice was finalized.

    `customer_phone: list[str]`
    :   The customer's phone number at the time the invoice was finalized.

    `customer_shipping: list[dict[str, typing.Any]]`
    :   The customer's shipping information at the time the invoice was finalized.

    `customer_tax_exempt: list[str]`
    :   The customer's tax exempt status at the time the invoice was finalized.

    `customer_tax_ids: list[list[typing.Any]]`
    :   The customer's tax IDs at the time the invoice was finalized.

    `default_payment_method: list[str]`
    :   Default payment method for the invoice, used if no other method is specified.

    `default_source: list[str]`
    :   Default payment source for the invoice if no payment method is set.

    `default_tax_rates: list[list[typing.Any]]`
    :   The tax rates applied to the invoice by default.

    `description: list[str]`
    :   An arbitrary string attached to the invoice, often displayed to customers.

    `discount: list[dict[str, typing.Any]]`
    :   The discount object applied to the invoice, if any.

    `discounts: list[list[typing.Any]]`
    :   Array of discount IDs or objects currently applied to this invoice.

    `due_date: list[float]`
    :   The date by which payment on this invoice is due, if the invoice is not auto-collected.

    `effective_at: list[int]`
    :   Timestamp when the invoice becomes effective and finalized for payment.

    `ending_balance: list[int]`
    :   The customer's ending account balance after this invoice is finalized.

    `footer: list[str]`
    :   Footer text displayed on the invoice.

    `forgiven: list[bool]`
    :   Whether the invoice has been forgiven and is considered paid without actual payment.

    `from_invoice: list[dict[str, typing.Any]]`
    :   Details about the invoice this invoice was created from, if applicable.

    `hosted_invoice_url: list[str]`
    :   URL for the hosted invoice page where customers can view and pay the invoice.

    `id: list[str]`
    :   Unique identifier for the invoice object.

    `invoice_pdf: list[str]`
    :   URL for the PDF version of the invoice.

    `is_deleted: list[bool]`
    :   Indicates whether this invoice has been deleted.

    `issuer: list[dict[str, typing.Any]]`
    :   Details about the entity issuing the invoice.

    `last_finalization_error: list[dict[str, typing.Any]]`
    :   The error encountered during the last finalization attempt, if any.

    `latest_revision: list[str]`
    :   The latest revision of the invoice, if revisions are enabled.

    `lines: list[dict[str, typing.Any]]`
    :   The individual line items that make up the invoice, representing products, services, or fees.

    `livemode: list[bool]`
    :   Indicates whether the invoice exists in live mode (true) or test mode (false).

    `metadata: list[dict[str, typing.Any]]`
    :   Key-value pairs for storing additional structured information about the invoice.

    `next_payment_attempt: list[float]`
    :   Timestamp of the next automatic payment attempt for this invoice, if applicable.

    `number: list[str]`
    :   A unique, human-readable identifier for this invoice, often shown to customers.

    `object_: list[str]`
    :   String representing the object type, always 'invoice'.

    `on_behalf_of: list[str]`
    :   The account on behalf of which the invoice is being created, used in Connect scenarios.

    `paid: list[bool]`
    :   Whether the invoice has been paid in full.

    `paid_out_of_band: list[bool]`
    :   Whether payment was made outside of Stripe and manually marked as paid.

    `payment: list[str]`
    :   ID of the payment associated with this invoice, if any.

    `payment_intent: list[str]`
    :   The PaymentIntent associated with this invoice for processing payment.

    `payment_settings: list[dict[str, typing.Any]]`
    :   Configuration settings for how payment should be collected on this invoice.

    `period_end: list[float]`
    :   End date of the billing period covered by this invoice.

    `period_start: list[float]`
    :   Start date of the billing period covered by this invoice.

    `post_payment_credit_notes_amount: list[int]`
    :   Total amount of credit notes issued after the invoice was paid.

    `pre_payment_credit_notes_amount: list[int]`
    :   Total amount of credit notes applied before payment was attempted.

    `quote: list[str]`
    :   The quote from which this invoice was generated, if applicable.

    `receipt_number: list[str]`
    :   The receipt number displayed on the invoice, if available.

    `rendering: list[dict[str, typing.Any]]`
    :   Settings that control how the invoice is rendered for display.

    `rendering_options: list[dict[str, typing.Any]]`
    :   Options for customizing the visual rendering of the invoice.

    `shipping_cost: list[dict[str, typing.Any]]`
    :   Total cost of shipping charges included in the invoice.

    `shipping_details: list[dict[str, typing.Any]]`
    :   Detailed shipping information for the invoice, including address and carrier.

    `starting_balance: list[int]`
    :   The customer's starting account balance at the beginning of the billing period.

    `statement_description: list[str]`
    :   Extra information about the invoice that appears on the customer's credit card statement.

    `statement_descriptor: list[str]`
    :   A dynamic descriptor that appears on the customer's credit card statement for this invoice.

    `status: list[str]`
    :   The status of the invoice: draft, open, paid, void, or uncollectible.

    `status_transitions: list[dict[str, typing.Any]]`
    :   Timestamps tracking when the invoice transitioned between different statuses.

    `subscription: list[str]`
    :   The subscription this invoice was generated for, if applicable.

    `subscription_details: list[dict[str, typing.Any]]`
    :   Additional details about the subscription associated with this invoice.

    `subtotal: list[int]`
    :   Total of all line items before discounts or tax are applied.

    `subtotal_excluding_tax: list[int]`
    :   The subtotal amount excluding any tax calculations.

    `tax: list[int]`
    :   Total tax amount applied to the invoice.

    `tax_percent: list[float]`
    :   The percentage of tax applied to the invoice (deprecated, use total_tax_amounts instead).

    `test_clock: list[str]`
    :   ID of the test clock this invoice belongs to, used for testing time-dependent billing.

    `total: list[int]`
    :   Total amount of the invoice after all line items, discounts, and taxes are calculated.

    `total_discount_amounts: list[list[typing.Any]]`
    :   Array of the total discount amounts applied, broken down by discount.

    `total_excluding_tax: list[int]`
    :   Total amount of the invoice excluding all tax calculations.

    `total_tax_amounts: list[list[typing.Any]]`
    :   Array of tax amounts applied to the invoice, broken down by tax rate.

    `transfer_data: list[dict[str, typing.Any]]`
    :   Information about the transfer of funds associated with this invoice in Connect scenarios.

    `updated: list[int]`
    :   Timestamp indicating when the invoice was last updated.

    `webhooks_delivered_at: list[float]`
    :   Timestamp indicating when webhooks for this invoice were successfully delivered.

<a id="InvoicesKeywordCondition"></a>

`InvoicesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.stripe.types.InvoicesStringFilter`
    :   The type of the None singleton.

<a id="InvoicesLikeCondition"></a>

`InvoicesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.stripe.types.InvoicesStringFilter`
    :   The type of the None singleton.

<a id="InvoicesListParams"></a>

`InvoicesListParams(*args, **kwargs)`
:   Parameters for invoices.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `collection_method: str`
    :   The type of the None singleton.

    `created: airbyte_agent_sdk.connectors.stripe.types.InvoicesListParamsCreated`
    :   The type of the None singleton.

    `customer: str`
    :   The type of the None singleton.

    `customer_account: str`
    :   The type of the None singleton.

    `ending_before: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `starting_after: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `subscription: str`
    :   The type of the None singleton.

<a id="InvoicesListParamsCreated"></a>

`InvoicesListParamsCreated(*args, **kwargs)`
:   Nested schema for InvoicesListParams.created

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: int`
    :   The type of the None singleton.

    `gte: int`
    :   The type of the None singleton.

    `lt: int`
    :   The type of the None singleton.

    `lte: int`
    :   The type of the None singleton.

<a id="InvoicesLtCondition"></a>

`InvoicesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.stripe.types.InvoicesSearchFilter`
    :   The type of the None singleton.

<a id="InvoicesLteCondition"></a>

`InvoicesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.stripe.types.InvoicesSearchFilter`
    :   The type of the None singleton.

<a id="InvoicesNeqCondition"></a>

`InvoicesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.stripe.types.InvoicesSearchFilter`
    :   The type of the None singleton.

<a id="InvoicesNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.stripe.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesInCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesLikeCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesAnyCondition`
    :   The type of the None singleton.

<a id="InvoicesOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.stripe.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesInCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesLikeCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesAnyCondition]`
    :   The type of the None singleton.

<a id="InvoicesSearchFilter"></a>

`InvoicesSearchFilter(*args, **kwargs)`
:   Available fields for filtering invoices search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="InvoicesSearchQuery"></a>

`InvoicesSearchQuery(*args, **kwargs)`
:   Search query for invoices entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.stripe.types.InvoicesEqCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesNeqCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesGtCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesGteCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesLtCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesLteCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesInCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesLikeCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesContainsCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesNotCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesAndCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesOrCondition | airbyte_agent_sdk.connectors.stripe.types.InvoicesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.stripe.types.InvoicesSortFilter]`
    :   The type of the None singleton.

<a id="InvoicesSortFilter"></a>

`InvoicesSortFilter(*args, **kwargs)`
:   Available fields for sorting invoices search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_country: Literal['asc', 'desc']`
    :   The country of the business associated with this invoice, commonly used to display localized content.

    `account_name: Literal['asc', 'desc']`
    :   The public name of the business associated with this invoice.

    `account_tax_ids: Literal['asc', 'desc']`
    :   Tax IDs of the account associated with this invoice.

    `amount_due: Literal['asc', 'desc']`
    :   Total amount, in smallest currency unit, that is due and owed by the customer.

    `amount_paid: Literal['asc', 'desc']`
    :   Total amount, in smallest currency unit, that has been paid by the customer.

    `amount_remaining: Literal['asc', 'desc']`
    :   The difference between amount_due and amount_paid, representing the outstanding balance.

    `amount_shipping: Literal['asc', 'desc']`
    :   Total amount of shipping costs on the invoice.

    `application: Literal['asc', 'desc']`
    :   ID of the Connect application that created this invoice.

    `application_fee: Literal['asc', 'desc']`
    :   Amount of application fee charged for this invoice in a Connect scenario.

    `application_fee_amount: Literal['asc', 'desc']`
    :   The fee in smallest currency unit that is collected by the application in a Connect scenario.

    `attempt_count: Literal['asc', 'desc']`
    :   Number of payment attempts made for this invoice.

    `attempted: Literal['asc', 'desc']`
    :   Whether an attempt has been made to pay the invoice.

    `auto_advance: Literal['asc', 'desc']`
    :   Controls whether Stripe performs automatic collection of the invoice.

    `automatic_tax: Literal['asc', 'desc']`
    :   Settings and status for automatic tax calculation on this invoice.

    `billing: Literal['asc', 'desc']`
    :   Billing method used for the invoice (charge_automatically or send_invoice).

    `billing_reason: Literal['asc', 'desc']`
    :   Indicates the reason why the invoice was created (subscription_cycle, manual, etc.).

    `charge: Literal['asc', 'desc']`
    :   ID of the latest charge generated for this invoice, if any.

    `closed: Literal['asc', 'desc']`
    :   Whether the invoice has been marked as closed and no longer open for collection.

    `collection_method: Literal['asc', 'desc']`
    :   Method by which the invoice is collected: charge_automatically or send_invoice.

    `created: Literal['asc', 'desc']`
    :   Timestamp indicating when the invoice was created.

    `currency: Literal['asc', 'desc']`
    :   Three-letter ISO currency code in which the invoice is denominated.

    `custom_fields: Literal['asc', 'desc']`
    :   Custom fields displayed on the invoice as specified by the account.

    `customer: Literal['asc', 'desc']`
    :   The customer object or ID associated with this invoice.

    `customer_address: Literal['asc', 'desc']`
    :   The customer's address at the time the invoice was finalized.

    `customer_email: Literal['asc', 'desc']`
    :   The customer's email address at the time the invoice was finalized.

    `customer_name: Literal['asc', 'desc']`
    :   The customer's name at the time the invoice was finalized.

    `customer_phone: Literal['asc', 'desc']`
    :   The customer's phone number at the time the invoice was finalized.

    `customer_shipping: Literal['asc', 'desc']`
    :   The customer's shipping information at the time the invoice was finalized.

    `customer_tax_exempt: Literal['asc', 'desc']`
    :   The customer's tax exempt status at the time the invoice was finalized.

    `customer_tax_ids: Literal['asc', 'desc']`
    :   The customer's tax IDs at the time the invoice was finalized.

    `default_payment_method: Literal['asc', 'desc']`
    :   Default payment method for the invoice, used if no other method is specified.

    `default_source: Literal['asc', 'desc']`
    :   Default payment source for the invoice if no payment method is set.

    `default_tax_rates: Literal['asc', 'desc']`
    :   The tax rates applied to the invoice by default.

    `description: Literal['asc', 'desc']`
    :   An arbitrary string attached to the invoice, often displayed to customers.

    `discount: Literal['asc', 'desc']`
    :   The discount object applied to the invoice, if any.

    `discounts: Literal['asc', 'desc']`
    :   Array of discount IDs or objects currently applied to this invoice.

    `due_date: Literal['asc', 'desc']`
    :   The date by which payment on this invoice is due, if the invoice is not auto-collected.

    `effective_at: Literal['asc', 'desc']`
    :   Timestamp when the invoice becomes effective and finalized for payment.

    `ending_balance: Literal['asc', 'desc']`
    :   The customer's ending account balance after this invoice is finalized.

    `footer: Literal['asc', 'desc']`
    :   Footer text displayed on the invoice.

    `forgiven: Literal['asc', 'desc']`
    :   Whether the invoice has been forgiven and is considered paid without actual payment.

    `from_invoice: Literal['asc', 'desc']`
    :   Details about the invoice this invoice was created from, if applicable.

    `hosted_invoice_url: Literal['asc', 'desc']`
    :   URL for the hosted invoice page where customers can view and pay the invoice.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the invoice object.

    `invoice_pdf: Literal['asc', 'desc']`
    :   URL for the PDF version of the invoice.

    `is_deleted: Literal['asc', 'desc']`
    :   Indicates whether this invoice has been deleted.

    `issuer: Literal['asc', 'desc']`
    :   Details about the entity issuing the invoice.

    `last_finalization_error: Literal['asc', 'desc']`
    :   The error encountered during the last finalization attempt, if any.

    `latest_revision: Literal['asc', 'desc']`
    :   The latest revision of the invoice, if revisions are enabled.

    `lines: Literal['asc', 'desc']`
    :   The individual line items that make up the invoice, representing products, services, or fees.

    `livemode: Literal['asc', 'desc']`
    :   Indicates whether the invoice exists in live mode (true) or test mode (false).

    `metadata: Literal['asc', 'desc']`
    :   Key-value pairs for storing additional structured information about the invoice.

    `next_payment_attempt: Literal['asc', 'desc']`
    :   Timestamp of the next automatic payment attempt for this invoice, if applicable.

    `number: Literal['asc', 'desc']`
    :   A unique, human-readable identifier for this invoice, often shown to customers.

    `object_: Literal['asc', 'desc']`
    :   String representing the object type, always 'invoice'.

    `on_behalf_of: Literal['asc', 'desc']`
    :   The account on behalf of which the invoice is being created, used in Connect scenarios.

    `paid: Literal['asc', 'desc']`
    :   Whether the invoice has been paid in full.

    `paid_out_of_band: Literal['asc', 'desc']`
    :   Whether payment was made outside of Stripe and manually marked as paid.

    `payment: Literal['asc', 'desc']`
    :   ID of the payment associated with this invoice, if any.

    `payment_intent: Literal['asc', 'desc']`
    :   The PaymentIntent associated with this invoice for processing payment.

    `payment_settings: Literal['asc', 'desc']`
    :   Configuration settings for how payment should be collected on this invoice.

    `period_end: Literal['asc', 'desc']`
    :   End date of the billing period covered by this invoice.

    `period_start: Literal['asc', 'desc']`
    :   Start date of the billing period covered by this invoice.

    `post_payment_credit_notes_amount: Literal['asc', 'desc']`
    :   Total amount of credit notes issued after the invoice was paid.

    `pre_payment_credit_notes_amount: Literal['asc', 'desc']`
    :   Total amount of credit notes applied before payment was attempted.

    `quote: Literal['asc', 'desc']`
    :   The quote from which this invoice was generated, if applicable.

    `receipt_number: Literal['asc', 'desc']`
    :   The receipt number displayed on the invoice, if available.

    `rendering: Literal['asc', 'desc']`
    :   Settings that control how the invoice is rendered for display.

    `rendering_options: Literal['asc', 'desc']`
    :   Options for customizing the visual rendering of the invoice.

    `shipping_cost: Literal['asc', 'desc']`
    :   Total cost of shipping charges included in the invoice.

    `shipping_details: Literal['asc', 'desc']`
    :   Detailed shipping information for the invoice, including address and carrier.

    `starting_balance: Literal['asc', 'desc']`
    :   The customer's starting account balance at the beginning of the billing period.

    `statement_description: Literal['asc', 'desc']`
    :   Extra information about the invoice that appears on the customer's credit card statement.

    `statement_descriptor: Literal['asc', 'desc']`
    :   A dynamic descriptor that appears on the customer's credit card statement for this invoice.

    `status: Literal['asc', 'desc']`
    :   The status of the invoice: draft, open, paid, void, or uncollectible.

    `status_transitions: Literal['asc', 'desc']`
    :   Timestamps tracking when the invoice transitioned between different statuses.

    `subscription: Literal['asc', 'desc']`
    :   The subscription this invoice was generated for, if applicable.

    `subscription_details: Literal['asc', 'desc']`
    :   Additional details about the subscription associated with this invoice.

    `subtotal: Literal['asc', 'desc']`
    :   Total of all line items before discounts or tax are applied.

    `subtotal_excluding_tax: Literal['asc', 'desc']`
    :   The subtotal amount excluding any tax calculations.

    `tax: Literal['asc', 'desc']`
    :   Total tax amount applied to the invoice.

    `tax_percent: Literal['asc', 'desc']`
    :   The percentage of tax applied to the invoice (deprecated, use total_tax_amounts instead).

    `test_clock: Literal['asc', 'desc']`
    :   ID of the test clock this invoice belongs to, used for testing time-dependent billing.

    `total: Literal['asc', 'desc']`
    :   Total amount of the invoice after all line items, discounts, and taxes are calculated.

    `total_discount_amounts: Literal['asc', 'desc']`
    :   Array of the total discount amounts applied, broken down by discount.

    `total_excluding_tax: Literal['asc', 'desc']`
    :   Total amount of the invoice excluding all tax calculations.

    `total_tax_amounts: Literal['asc', 'desc']`
    :   Array of tax amounts applied to the invoice, broken down by tax rate.

    `transfer_data: Literal['asc', 'desc']`
    :   Information about the transfer of funds associated with this invoice in Connect scenarios.

    `updated: Literal['asc', 'desc']`
    :   Timestamp indicating when the invoice was last updated.

    `webhooks_delivered_at: Literal['asc', 'desc']`
    :   Timestamp indicating when webhooks for this invoice were successfully delivered.

<a id="InvoicesStringFilter"></a>

`InvoicesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `account_country: str`
    :   The country of the business associated with this invoice, commonly used to display localized content.

    `account_name: str`
    :   The public name of the business associated with this invoice.

    `account_tax_ids: str`
    :   Tax IDs of the account associated with this invoice.

    `amount_due: str`
    :   Total amount, in smallest currency unit, that is due and owed by the customer.

    `amount_paid: str`
    :   Total amount, in smallest currency unit, that has been paid by the customer.

    `amount_remaining: str`
    :   The difference between amount_due and amount_paid, representing the outstanding balance.

    `amount_shipping: str`
    :   Total amount of shipping costs on the invoice.

    `application: str`
    :   ID of the Connect application that created this invoice.

    `application_fee: str`
    :   Amount of application fee charged for this invoice in a Connect scenario.

    `application_fee_amount: str`
    :   The fee in smallest currency unit that is collected by the application in a Connect scenario.

    `attempt_count: str`
    :   Number of payment attempts made for this invoice.

    `attempted: str`
    :   Whether an attempt has been made to pay the invoice.

    `auto_advance: str`
    :   Controls whether Stripe performs automatic collection of the invoice.

    `automatic_tax: str`
    :   Settings and status for automatic tax calculation on this invoice.

    `billing: str`
    :   Billing method used for the invoice (charge_automatically or send_invoice).

    `billing_reason: str`
    :   Indicates the reason why the invoice was created (subscription_cycle, manual, etc.).

    `charge: str`
    :   ID of the latest charge generated for this invoice, if any.

    `closed: str`
    :   Whether the invoice has been marked as closed and no longer open for collection.

    `collection_method: str`
    :   Method by which the invoice is collected: charge_automatically or send_invoice.

    `created: str`
    :   Timestamp indicating when the invoice was created.

    `currency: str`
    :   Three-letter ISO currency code in which the invoice is denominated.

    `custom_fields: str`
    :   Custom fields displayed on the invoice as specified by the account.

    `customer: str`
    :   The customer object or ID associated with this invoice.

    `customer_address: str`
    :   The customer's address at the time the invoice was finalized.

    `customer_email: str`
    :   The customer's email address at the time the invoice was finalized.

    `customer_name: str`
    :   The customer's name at the time the invoice was finalized.

    `customer_phone: str`
    :   The customer's phone number at the time the invoice was finalized.

    `customer_shipping: str`
    :   The customer's shipping information at the time the invoice was finalized.

    `customer_tax_exempt: str`
    :   The customer's tax exempt status at the time the invoice was finalized.

    `customer_tax_ids: str`
    :   The customer's tax IDs at the time the invoice was finalized.

    `default_payment_method: str`
    :   Default payment method for the invoice, used if no other method is specified.

    `default_source: str`
    :   Default payment source for the invoice if no payment method is set.

    `default_tax_rates: str`
    :   The tax rates applied to the invoice by default.

    `description: str`
    :   An arbitrary string attached to the invoice, often displayed to customers.

    `discount: str`
    :   The discount object applied to the invoice, if any.

    `discounts: str`
    :   Array of discount IDs or objects currently applied to this invoice.

    `due_date: str`
    :   The date by which payment on this invoice is due, if the invoice is not auto-collected.

    `effective_at: str`
    :   Timestamp when the invoice becomes effective and finalized for payment.

    `ending_balance: str`
    :   The customer's ending account balance after this invoice is finalized.

    `footer: str`
    :   Footer text displayed on the invoice.

    `forgiven: str`
    :   Whether the invoice has been forgiven and is considered paid without actual payment.

    `from_invoice: str`
    :   Details about the invoice this invoice was created from, if applicable.

    `hosted_invoice_url: str`
    :   URL for the hosted invoice page where customers can view and pay the invoice.

    `id: str`
    :   Unique identifier for the invoice object.

    `invoice_pdf: str`
    :   URL for the PDF version of the invoice.

    `is_deleted: str`
    :   Indicates whether this invoice has been deleted.

    `issuer: str`
    :   Details about the entity issuing the invoice.

    `last_finalization_error: str`
    :   The error encountered during the last finalization attempt, if any.

    `latest_revision: str`
    :   The latest revision of the invoice, if revisions are enabled.

    `lines: str`
    :   The individual line items that make up the invoice, representing products, services, or fees.

    `livemode: str`
    :   Indicates whether the invoice exists in live mode (true) or test mode (false).

    `metadata: str`
    :   Key-value pairs for storing additional structured information about the invoice.

    `next_payment_attempt: str`
    :   Timestamp of the next automatic payment attempt for this invoice, if applicable.

    `number: str`
    :   A unique, human-readable identifier for this invoice, often shown to customers.

    `object_: str`
    :   String representing the object type, always 'invoice'.

    `on_behalf_of: str`
    :   The account on behalf of which the invoice is being created, used in Connect scenarios.

    `paid: str`
    :   Whether the invoice has been paid in full.

    `paid_out_of_band: str`
    :   Whether payment was made outside of Stripe and manually marked as paid.

    `payment: str`
    :   ID of the payment associated with this invoice, if any.

    `payment_intent: str`
    :   The PaymentIntent associated with this invoice for processing payment.

    `payment_settings: str`
    :   Configuration settings for how payment should be collected on this invoice.

    `period_end: str`
    :   End date of the billing period covered by this invoice.

    `period_start: str`
    :   Start date of the billing period covered by this invoice.

    `post_payment_credit_notes_amount: str`
    :   Total amount of credit notes issued after the invoice was paid.

    `pre_payment_credit_notes_amount: str`
    :   Total amount of credit notes applied before payment was attempted.

    `quote: str`
    :   The quote from which this invoice was generated, if applicable.

    `receipt_number: str`
    :   The receipt number displayed on the invoice, if available.

    `rendering: str`
    :   Settings that control how the invoice is rendered for display.

    `rendering_options: str`
    :   Options for customizing the visual rendering of the invoice.

    `shipping_cost: str`
    :   Total cost of shipping charges included in the invoice.

    `shipping_details: str`
    :   Detailed shipping information for the invoice, including address and carrier.

    `starting_balance: str`
    :   The customer's starting account balance at the beginning of the billing period.

    `statement_description: str`
    :   Extra information about the invoice that appears on the customer's credit card statement.

    `statement_descriptor: str`
    :   A dynamic descriptor that appears on the customer's credit card statement for this invoice.

    `status: str`
    :   The status of the invoice: draft, open, paid, void, or uncollectible.

    `status_transitions: str`
    :   Timestamps tracking when the invoice transitioned between different statuses.

    `subscription: str`
    :   The subscription this invoice was generated for, if applicable.

    `subscription_details: str`
    :   Additional details about the subscription associated with this invoice.

    `subtotal: str`
    :   Total of all line items before discounts or tax are applied.

    `subtotal_excluding_tax: str`
    :   The subtotal amount excluding any tax calculations.

    `tax: str`
    :   Total tax amount applied to the invoice.

    `tax_percent: str`
    :   The percentage of tax applied to the invoice (deprecated, use total_tax_amounts instead).

    `test_clock: str`
    :   ID of the test clock this invoice belongs to, used for testing time-dependent billing.

    `total: str`
    :   Total amount of the invoice after all line items, discounts, and taxes are calculated.

    `total_discount_amounts: str`
    :   Array of the total discount amounts applied, broken down by discount.

    `total_excluding_tax: str`
    :   Total amount of the invoice excluding all tax calculations.

    `total_tax_amounts: str`
    :   Array of tax amounts applied to the invoice, broken down by tax rate.

    `transfer_data: str`
    :   Information about the transfer of funds associated with this invoice in Connect scenarios.

    `updated: str`
    :   Timestamp indicating when the invoice was last updated.

    `webhooks_delivered_at: str`
    :   Timestamp indicating when webhooks for this invoice were successfully delivered.

<a id="PaymentIntentsApiSearchParams"></a>

`PaymentIntentsApiSearchParams(*args, **kwargs)`
:   Parameters for payment_intents.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `page: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="PaymentIntentsGetParams"></a>

`PaymentIntentsGetParams(*args, **kwargs)`
:   Parameters for payment_intents.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="PaymentIntentsListParams"></a>

`PaymentIntentsListParams(*args, **kwargs)`
:   Parameters for payment_intents.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created: airbyte_agent_sdk.connectors.stripe.types.PaymentIntentsListParamsCreated`
    :   The type of the None singleton.

    `customer: str`
    :   The type of the None singleton.

    `customer_account: str`
    :   The type of the None singleton.

    `ending_before: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `starting_after: str`
    :   The type of the None singleton.

<a id="PaymentIntentsListParamsCreated"></a>

`PaymentIntentsListParamsCreated(*args, **kwargs)`
:   Nested schema for PaymentIntentsListParams.created

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: int`
    :   The type of the None singleton.

    `gte: int`
    :   The type of the None singleton.

    `lt: int`
    :   The type of the None singleton.

    `lte: int`
    :   The type of the None singleton.

<a id="PayoutsGetParams"></a>

`PayoutsGetParams(*args, **kwargs)`
:   Parameters for payouts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="PayoutsListParams"></a>

`PayoutsListParams(*args, **kwargs)`
:   Parameters for payouts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `arrival_date: airbyte_agent_sdk.connectors.stripe.types.PayoutsListParamsArrivalDate`
    :   The type of the None singleton.

    `created: airbyte_agent_sdk.connectors.stripe.types.PayoutsListParamsCreated`
    :   The type of the None singleton.

    `destination: str`
    :   The type of the None singleton.

    `ending_before: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `starting_after: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

<a id="PayoutsListParamsArrivalDate"></a>

`PayoutsListParamsArrivalDate(*args, **kwargs)`
:   Nested schema for PayoutsListParams.arrival_date

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: int`
    :   The type of the None singleton.

    `gte: int`
    :   The type of the None singleton.

    `lt: int`
    :   The type of the None singleton.

    `lte: int`
    :   The type of the None singleton.

<a id="PayoutsListParamsCreated"></a>

`PayoutsListParamsCreated(*args, **kwargs)`
:   Nested schema for PayoutsListParams.created

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: int`
    :   The type of the None singleton.

    `gte: int`
    :   The type of the None singleton.

    `lt: int`
    :   The type of the None singleton.

    `lte: int`
    :   The type of the None singleton.

<a id="ProductsApiSearchParams"></a>

`ProductsApiSearchParams(*args, **kwargs)`
:   Parameters for products.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `page: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="ProductsCreateParams"></a>

`ProductsCreateParams(*args, **kwargs)`
:   Parameters for products.create operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="ProductsDeleteParams"></a>

`ProductsDeleteParams(*args, **kwargs)`
:   Parameters for products.delete operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ProductsGetParams"></a>

`ProductsGetParams(*args, **kwargs)`
:   Parameters for products.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="ProductsListParams"></a>

`ProductsListParams(*args, **kwargs)`
:   Parameters for products.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `active: bool`
    :   The type of the None singleton.

    `created: airbyte_agent_sdk.connectors.stripe.types.ProductsListParamsCreated`
    :   The type of the None singleton.

    `ending_before: str`
    :   The type of the None singleton.

    `ids: list[str]`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `shippable: bool`
    :   The type of the None singleton.

    `starting_after: str`
    :   The type of the None singleton.

    `url: str`
    :   The type of the None singleton.

<a id="ProductsListParamsCreated"></a>

`ProductsListParamsCreated(*args, **kwargs)`
:   Nested schema for ProductsListParams.created

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: int`
    :   The type of the None singleton.

    `gte: int`
    :   The type of the None singleton.

    `lt: int`
    :   The type of the None singleton.

    `lte: int`
    :   The type of the None singleton.

<a id="ProductsUpdateParams"></a>

`ProductsUpdateParams(*args, **kwargs)`
:   Parameters for products.update operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="RefundsAndCondition"></a>

`RefundsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.stripe.types.RefundsEqCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsNeqCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsGtCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsGteCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsLtCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsLteCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsInCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsLikeCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsContainsCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsNotCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsAndCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsOrCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsAnyCondition]`
    :   The type of the None singleton.

<a id="RefundsAnyCondition"></a>

`RefundsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.stripe.types.RefundsAnyValueFilter`
    :   The type of the None singleton.

<a id="RefundsAnyValueFilter"></a>

`RefundsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Any`
    :   Amount refunded, in cents (the smallest currency unit).

    `balance_transaction: Any`
    :   ID of the balance transaction that describes the impact of this refund on your account balance.

    `charge: Any`
    :   ID of the charge that was refunded.

    `created: Any`
    :   Timestamp indicating when the refund was created.

    `currency: Any`
    :   Three-letter ISO currency code in lowercase representing the currency of the refund.

    `destination_details: Any`
    :   Details about the destination where the refunded funds should be sent.

    `id: Any`
    :   Unique identifier for the refund object.

    `metadata: Any`
    :   Set of key-value pairs that you can attach to an object for storing additional structured information.

    `object_: Any`
    :   String representing the object type, always 'refund'.

    `payment_intent: Any`
    :   ID of the PaymentIntent that was refunded.

    `reason: Any`
    :   Reason for the refund, either user-provided (duplicate, fraudulent, or requested_by_customer) or generated by Stripe internally (expired_uncaptured_charge).

    `receipt_number: Any`
    :   The transaction number that appears on email receipts sent for this refund.

    `source_transfer_reversal: Any`
    :   ID of the transfer reversal that was created as a result of refunding a transfer (Connect only).

    `status: Any`
    :   Status of the refund (pending, requires_action, succeeded, failed, or canceled).

    `transfer_reversal: Any`
    :   ID of the reversal of the transfer that funded the charge being refunded (Connect only).

    `updated: Any`
    :   Timestamp indicating when the refund was last updated.

<a id="RefundsContainsCondition"></a>

`RefundsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.stripe.types.RefundsAnyValueFilter`
    :   The type of the None singleton.

<a id="RefundsCreateParams"></a>

`RefundsCreateParams(*args, **kwargs)`
:   Parameters for refunds.create operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="RefundsEqCondition"></a>

`RefundsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.stripe.types.RefundsSearchFilter`
    :   The type of the None singleton.

<a id="RefundsFuzzyCondition"></a>

`RefundsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.stripe.types.RefundsStringFilter`
    :   The type of the None singleton.

<a id="RefundsGetParams"></a>

`RefundsGetParams(*args, **kwargs)`
:   Parameters for refunds.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="RefundsGtCondition"></a>

`RefundsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.stripe.types.RefundsSearchFilter`
    :   The type of the None singleton.

<a id="RefundsGteCondition"></a>

`RefundsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.stripe.types.RefundsSearchFilter`
    :   The type of the None singleton.

<a id="RefundsInCondition"></a>

`RefundsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.stripe.types.RefundsInFilter`
    :   The type of the None singleton.

<a id="RefundsInFilter"></a>

`RefundsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: list[int]`
    :   Amount refunded, in cents (the smallest currency unit).

    `balance_transaction: list[str]`
    :   ID of the balance transaction that describes the impact of this refund on your account balance.

    `charge: list[str]`
    :   ID of the charge that was refunded.

    `created: list[int]`
    :   Timestamp indicating when the refund was created.

    `currency: list[str]`
    :   Three-letter ISO currency code in lowercase representing the currency of the refund.

    `destination_details: list[dict[str, typing.Any]]`
    :   Details about the destination where the refunded funds should be sent.

    `id: list[str]`
    :   Unique identifier for the refund object.

    `metadata: list[dict[str, typing.Any]]`
    :   Set of key-value pairs that you can attach to an object for storing additional structured information.

    `object_: list[str]`
    :   String representing the object type, always 'refund'.

    `payment_intent: list[str]`
    :   ID of the PaymentIntent that was refunded.

    `reason: list[str]`
    :   Reason for the refund, either user-provided (duplicate, fraudulent, or requested_by_customer) or generated by Stripe internally (expired_uncaptured_charge).

    `receipt_number: list[str]`
    :   The transaction number that appears on email receipts sent for this refund.

    `source_transfer_reversal: list[str]`
    :   ID of the transfer reversal that was created as a result of refunding a transfer (Connect only).

    `status: list[str]`
    :   Status of the refund (pending, requires_action, succeeded, failed, or canceled).

    `transfer_reversal: list[str]`
    :   ID of the reversal of the transfer that funded the charge being refunded (Connect only).

    `updated: list[int]`
    :   Timestamp indicating when the refund was last updated.

<a id="RefundsKeywordCondition"></a>

`RefundsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.stripe.types.RefundsStringFilter`
    :   The type of the None singleton.

<a id="RefundsLikeCondition"></a>

`RefundsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.stripe.types.RefundsStringFilter`
    :   The type of the None singleton.

<a id="RefundsListParams"></a>

`RefundsListParams(*args, **kwargs)`
:   Parameters for refunds.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `charge: str`
    :   The type of the None singleton.

    `created: airbyte_agent_sdk.connectors.stripe.types.RefundsListParamsCreated`
    :   The type of the None singleton.

    `ending_before: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `payment_intent: str`
    :   The type of the None singleton.

    `starting_after: str`
    :   The type of the None singleton.

<a id="RefundsListParamsCreated"></a>

`RefundsListParamsCreated(*args, **kwargs)`
:   Nested schema for RefundsListParams.created

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: int`
    :   The type of the None singleton.

    `gte: int`
    :   The type of the None singleton.

    `lt: int`
    :   The type of the None singleton.

    `lte: int`
    :   The type of the None singleton.

<a id="RefundsLtCondition"></a>

`RefundsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.stripe.types.RefundsSearchFilter`
    :   The type of the None singleton.

<a id="RefundsLteCondition"></a>

`RefundsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.stripe.types.RefundsSearchFilter`
    :   The type of the None singleton.

<a id="RefundsNeqCondition"></a>

`RefundsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.stripe.types.RefundsSearchFilter`
    :   The type of the None singleton.

<a id="RefundsNotCondition"></a>

`RefundsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.stripe.types.RefundsEqCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsNeqCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsGtCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsGteCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsLtCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsLteCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsInCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsLikeCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsContainsCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsNotCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsAndCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsOrCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsAnyCondition`
    :   The type of the None singleton.

<a id="RefundsOrCondition"></a>

`RefundsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.stripe.types.RefundsEqCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsNeqCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsGtCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsGteCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsLtCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsLteCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsInCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsLikeCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsContainsCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsNotCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsAndCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsOrCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsAnyCondition]`
    :   The type of the None singleton.

<a id="RefundsSearchFilter"></a>

`RefundsSearchFilter(*args, **kwargs)`
:   Available fields for filtering refunds search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="RefundsSearchQuery"></a>

`RefundsSearchQuery(*args, **kwargs)`
:   Search query for refunds entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.stripe.types.RefundsEqCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsNeqCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsGtCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsGteCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsLtCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsLteCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsInCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsLikeCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsContainsCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsNotCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsAndCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsOrCondition | airbyte_agent_sdk.connectors.stripe.types.RefundsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.stripe.types.RefundsSortFilter]`
    :   The type of the None singleton.

<a id="RefundsSortFilter"></a>

`RefundsSortFilter(*args, **kwargs)`
:   Available fields for sorting refunds search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: Literal['asc', 'desc']`
    :   Amount refunded, in cents (the smallest currency unit).

    `balance_transaction: Literal['asc', 'desc']`
    :   ID of the balance transaction that describes the impact of this refund on your account balance.

    `charge: Literal['asc', 'desc']`
    :   ID of the charge that was refunded.

    `created: Literal['asc', 'desc']`
    :   Timestamp indicating when the refund was created.

    `currency: Literal['asc', 'desc']`
    :   Three-letter ISO currency code in lowercase representing the currency of the refund.

    `destination_details: Literal['asc', 'desc']`
    :   Details about the destination where the refunded funds should be sent.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the refund object.

    `metadata: Literal['asc', 'desc']`
    :   Set of key-value pairs that you can attach to an object for storing additional structured information.

    `object_: Literal['asc', 'desc']`
    :   String representing the object type, always 'refund'.

    `payment_intent: Literal['asc', 'desc']`
    :   ID of the PaymentIntent that was refunded.

    `reason: Literal['asc', 'desc']`
    :   Reason for the refund, either user-provided (duplicate, fraudulent, or requested_by_customer) or generated by Stripe internally (expired_uncaptured_charge).

    `receipt_number: Literal['asc', 'desc']`
    :   The transaction number that appears on email receipts sent for this refund.

    `source_transfer_reversal: Literal['asc', 'desc']`
    :   ID of the transfer reversal that was created as a result of refunding a transfer (Connect only).

    `status: Literal['asc', 'desc']`
    :   Status of the refund (pending, requires_action, succeeded, failed, or canceled).

    `transfer_reversal: Literal['asc', 'desc']`
    :   ID of the reversal of the transfer that funded the charge being refunded (Connect only).

    `updated: Literal['asc', 'desc']`
    :   Timestamp indicating when the refund was last updated.

<a id="RefundsStringFilter"></a>

`RefundsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `amount: str`
    :   Amount refunded, in cents (the smallest currency unit).

    `balance_transaction: str`
    :   ID of the balance transaction that describes the impact of this refund on your account balance.

    `charge: str`
    :   ID of the charge that was refunded.

    `created: str`
    :   Timestamp indicating when the refund was created.

    `currency: str`
    :   Three-letter ISO currency code in lowercase representing the currency of the refund.

    `destination_details: str`
    :   Details about the destination where the refunded funds should be sent.

    `id: str`
    :   Unique identifier for the refund object.

    `metadata: str`
    :   Set of key-value pairs that you can attach to an object for storing additional structured information.

    `object_: str`
    :   String representing the object type, always 'refund'.

    `payment_intent: str`
    :   ID of the PaymentIntent that was refunded.

    `reason: str`
    :   Reason for the refund, either user-provided (duplicate, fraudulent, or requested_by_customer) or generated by Stripe internally (expired_uncaptured_charge).

    `receipt_number: str`
    :   The transaction number that appears on email receipts sent for this refund.

    `source_transfer_reversal: str`
    :   ID of the transfer reversal that was created as a result of refunding a transfer (Connect only).

    `status: str`
    :   Status of the refund (pending, requires_action, succeeded, failed, or canceled).

    `transfer_reversal: str`
    :   ID of the reversal of the transfer that funded the charge being refunded (Connect only).

    `updated: str`
    :   Timestamp indicating when the refund was last updated.

<a id="SubscriptionsAndCondition"></a>

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

    `and: list[airbyte_agent_sdk.connectors.stripe.types.SubscriptionsEqCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsNeqCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsGtCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsGteCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsLtCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsLteCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsInCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsLikeCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsContainsCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsNotCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsAndCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsOrCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsAnyCondition]`
    :   The type of the None singleton.

<a id="SubscriptionsAnyCondition"></a>

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

    `any: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsAnyValueFilter`
    :   The type of the None singleton.

<a id="SubscriptionsAnyValueFilter"></a>

`SubscriptionsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `application: Any`
    :   For Connect platforms, the application associated with the subscription.

    `application_fee_percent: Any`
    :   For Connect platforms, the percentage of the subscription amount taken as an application fee.

    `automatic_tax: Any`
    :   Automatic tax calculation settings for the subscription.

    `billing: Any`
    :   Billing mode configuration for the subscription.

    `billing_cycle_anchor: Any`
    :   Timestamp determining when the billing cycle for the subscription starts.

    `billing_cycle_anchor_config: Any`
    :   Configuration for the subscription's billing cycle anchor behavior.

    `billing_thresholds: Any`
    :   Defines thresholds at which an invoice will be sent, controlling billing timing based on usage.

    `cancel_at: Any`
    :   Timestamp indicating when the subscription is scheduled to be canceled.

    `cancel_at_period_end: Any`
    :   Boolean indicating whether the subscription will be canceled at the end of the current billing period.

    `canceled_at: Any`
    :   Timestamp indicating when the subscription was canceled, if applicable.

    `cancellation_details: Any`
    :   Details about why and how the subscription was canceled.

    `collection_method: Any`
    :   How invoices are collected (charge_automatically or send_invoice).

    `created: Any`
    :   Timestamp indicating when the subscription was created.

    `currency: Any`
    :   Three-letter ISO currency code in lowercase indicating the currency for the subscription.

    `current_period_end: Any`
    :   Timestamp marking the end of the current billing period.

    `current_period_start: Any`
    :   Timestamp marking the start of the current billing period.

    `customer: Any`
    :   ID of the customer who owns the subscription, expandable to full customer object.

    `days_until_due: Any`
    :   Number of days until the invoice is due for subscriptions using send_invoice collection method.

    `default_payment_method: Any`
    :   ID of the default payment method for the subscription, taking precedence over default_source.

    `default_source: Any`
    :   ID of the default payment source for the subscription.

    `default_tax_rates: Any`
    :   Tax rates that apply to the subscription by default.

    `description: Any`
    :   Human-readable description of the subscription, displayable to the customer.

    `discount: Any`
    :   Describes any discount currently applied to the subscription.

    `ended_at: Any`
    :   Timestamp indicating when the subscription ended, if applicable.

    `id: Any`
    :   Unique identifier for the subscription object.

    `invoice_settings: Any`
    :   Settings for invoices generated by this subscription, such as custom fields and footer.

    `is_deleted: Any`
    :   Indicates whether the subscription has been deleted.

    `latest_invoice: Any`
    :   The most recent invoice this subscription has generated, expandable to full invoice object.

    `livemode: Any`
    :   Indicates whether the subscription exists in live mode (true) or test mode (false).

    `metadata: Any`
    :   Set of key-value pairs that you can attach to the subscription for storing additional structured information.

    `next_pending_invoice_item_invoice: Any`
    :   Timestamp when the next invoice for pending invoice items will be created.

    `object_: Any`
    :   String representing the object type, always 'subscription'.

    `on_behalf_of: Any`
    :   For Connect platforms, the account for which the subscription is being created or managed.

    `pause_collection: Any`
    :   Configuration for pausing collection on the subscription while retaining the subscription structure.

    `payment_settings: Any`
    :   Payment settings for invoices generated by this subscription.

    `pending_invoice_item_interval: Any`
    :   Specifies an interval for aggregating usage records into pending invoice items.

    `pending_setup_intent: Any`
    :   SetupIntent used for collecting user authentication when updating payment methods without immediate payment.

    `pending_update: Any`
    :   If specified, pending updates that will be applied to the subscription once the latest_invoice has been paid.

    `plan: Any`
    :   The plan associated with the subscription (deprecated, use items instead).

    `quantity: Any`
    :   Quantity of the plan subscribed to (deprecated, use items instead).

    `schedule: Any`
    :   ID of the subscription schedule managing this subscription's lifecycle, if applicable.

    `start_date: Any`
    :   Timestamp indicating when the subscription started.

    `status: Any`
    :   Current status of the subscription (incomplete, incomplete_expired, trialing, active, past_due, canceled, unpaid, or paused).

    `tax_percent: Any`
    :   The percentage of tax applied to the subscription (deprecated, use default_tax_rates instead).

    `test_clock: Any`
    :   ID of the test clock associated with this subscription for simulating time-based scenarios.

    `transfer_data: Any`
    :   For Connect platforms, the account receiving funds from the subscription and optional percentage transferred.

    `trial_end: Any`
    :   Timestamp indicating when the trial period ends, if applicable.

    `trial_settings: Any`
    :   Settings related to trial periods, including conditions for ending trials.

    `trial_start: Any`
    :   Timestamp indicating when the trial period began, if applicable.

    `updated: Any`
    :   Timestamp indicating when the subscription was last updated.

    ### Methods

    `items(self, /) ‑> Any`
    :   Return a set-like object providing a view on the dict's items.

<a id="SubscriptionsApiSearchParams"></a>

`SubscriptionsApiSearchParams(*args, **kwargs)`
:   Parameters for subscriptions.api_search operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `limit: int`
    :   The type of the None singleton.

    `page: str`
    :   The type of the None singleton.

    `query: str`
    :   The type of the None singleton.

<a id="SubscriptionsContainsCondition"></a>

`SubscriptionsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsAnyValueFilter`
    :   The type of the None singleton.

<a id="SubscriptionsEqCondition"></a>

`SubscriptionsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsSearchFilter`
    :   The type of the None singleton.

<a id="SubscriptionsFuzzyCondition"></a>

`SubscriptionsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsStringFilter`
    :   The type of the None singleton.

<a id="SubscriptionsGetParams"></a>

`SubscriptionsGetParams(*args, **kwargs)`
:   Parameters for subscriptions.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="SubscriptionsGtCondition"></a>

`SubscriptionsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsSearchFilter`
    :   The type of the None singleton.

<a id="SubscriptionsGteCondition"></a>

`SubscriptionsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsSearchFilter`
    :   The type of the None singleton.

<a id="SubscriptionsInCondition"></a>

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

    `in: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsInFilter`
    :   The type of the None singleton.

<a id="SubscriptionsInFilter"></a>

`SubscriptionsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `application: list[str]`
    :   For Connect platforms, the application associated with the subscription.

    `application_fee_percent: list[float]`
    :   For Connect platforms, the percentage of the subscription amount taken as an application fee.

    `automatic_tax: list[dict[str, typing.Any]]`
    :   Automatic tax calculation settings for the subscription.

    `billing: list[str]`
    :   Billing mode configuration for the subscription.

    `billing_cycle_anchor: list[float]`
    :   Timestamp determining when the billing cycle for the subscription starts.

    `billing_cycle_anchor_config: list[dict[str, typing.Any]]`
    :   Configuration for the subscription's billing cycle anchor behavior.

    `billing_thresholds: list[dict[str, typing.Any]]`
    :   Defines thresholds at which an invoice will be sent, controlling billing timing based on usage.

    `cancel_at: list[float]`
    :   Timestamp indicating when the subscription is scheduled to be canceled.

    `cancel_at_period_end: list[bool]`
    :   Boolean indicating whether the subscription will be canceled at the end of the current billing period.

    `canceled_at: list[float]`
    :   Timestamp indicating when the subscription was canceled, if applicable.

    `cancellation_details: list[dict[str, typing.Any]]`
    :   Details about why and how the subscription was canceled.

    `collection_method: list[str]`
    :   How invoices are collected (charge_automatically or send_invoice).

    `created: list[int]`
    :   Timestamp indicating when the subscription was created.

    `currency: list[str]`
    :   Three-letter ISO currency code in lowercase indicating the currency for the subscription.

    `current_period_end: list[float]`
    :   Timestamp marking the end of the current billing period.

    `current_period_start: list[int]`
    :   Timestamp marking the start of the current billing period.

    `customer: list[str]`
    :   ID of the customer who owns the subscription, expandable to full customer object.

    `days_until_due: list[int]`
    :   Number of days until the invoice is due for subscriptions using send_invoice collection method.

    `default_payment_method: list[str]`
    :   ID of the default payment method for the subscription, taking precedence over default_source.

    `default_source: list[str]`
    :   ID of the default payment source for the subscription.

    `default_tax_rates: list[list[typing.Any]]`
    :   Tax rates that apply to the subscription by default.

    `description: list[str]`
    :   Human-readable description of the subscription, displayable to the customer.

    `discount: list[dict[str, typing.Any]]`
    :   Describes any discount currently applied to the subscription.

    `ended_at: list[float]`
    :   Timestamp indicating when the subscription ended, if applicable.

    `id: list[str]`
    :   Unique identifier for the subscription object.

    `invoice_settings: list[dict[str, typing.Any]]`
    :   Settings for invoices generated by this subscription, such as custom fields and footer.

    `is_deleted: list[bool]`
    :   Indicates whether the subscription has been deleted.

    `latest_invoice: list[str]`
    :   The most recent invoice this subscription has generated, expandable to full invoice object.

    `livemode: list[bool]`
    :   Indicates whether the subscription exists in live mode (true) or test mode (false).

    `metadata: list[dict[str, typing.Any]]`
    :   Set of key-value pairs that you can attach to the subscription for storing additional structured information.

    `next_pending_invoice_item_invoice: list[int]`
    :   Timestamp when the next invoice for pending invoice items will be created.

    `object_: list[str]`
    :   String representing the object type, always 'subscription'.

    `on_behalf_of: list[str]`
    :   For Connect platforms, the account for which the subscription is being created or managed.

    `pause_collection: list[dict[str, typing.Any]]`
    :   Configuration for pausing collection on the subscription while retaining the subscription structure.

    `payment_settings: list[dict[str, typing.Any]]`
    :   Payment settings for invoices generated by this subscription.

    `pending_invoice_item_interval: list[dict[str, typing.Any]]`
    :   Specifies an interval for aggregating usage records into pending invoice items.

    `pending_setup_intent: list[str]`
    :   SetupIntent used for collecting user authentication when updating payment methods without immediate payment.

    `pending_update: list[dict[str, typing.Any]]`
    :   If specified, pending updates that will be applied to the subscription once the latest_invoice has been paid.

    `plan: list[dict[str, typing.Any]]`
    :   The plan associated with the subscription (deprecated, use items instead).

    `quantity: list[int]`
    :   Quantity of the plan subscribed to (deprecated, use items instead).

    `schedule: list[str]`
    :   ID of the subscription schedule managing this subscription's lifecycle, if applicable.

    `start_date: list[int]`
    :   Timestamp indicating when the subscription started.

    `status: list[str]`
    :   Current status of the subscription (incomplete, incomplete_expired, trialing, active, past_due, canceled, unpaid, or paused).

    `tax_percent: list[float]`
    :   The percentage of tax applied to the subscription (deprecated, use default_tax_rates instead).

    `test_clock: list[str]`
    :   ID of the test clock associated with this subscription for simulating time-based scenarios.

    `transfer_data: list[dict[str, typing.Any]]`
    :   For Connect platforms, the account receiving funds from the subscription and optional percentage transferred.

    `trial_end: list[float]`
    :   Timestamp indicating when the trial period ends, if applicable.

    `trial_settings: list[dict[str, typing.Any]]`
    :   Settings related to trial periods, including conditions for ending trials.

    `trial_start: list[int]`
    :   Timestamp indicating when the trial period began, if applicable.

    `updated: list[int]`
    :   Timestamp indicating when the subscription was last updated.

    ### Methods

    `items(self, /) ‑> list[dict[str, typing.Any]]`
    :   Return a set-like object providing a view on the dict's items.

<a id="SubscriptionsKeywordCondition"></a>

`SubscriptionsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsStringFilter`
    :   The type of the None singleton.

<a id="SubscriptionsLikeCondition"></a>

`SubscriptionsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsStringFilter`
    :   The type of the None singleton.

<a id="SubscriptionsListParams"></a>

`SubscriptionsListParams(*args, **kwargs)`
:   Parameters for subscriptions.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `automatic_tax: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsListParamsAutomaticTax`
    :   The type of the None singleton.

    `collection_method: str`
    :   The type of the None singleton.

    `created: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsListParamsCreated`
    :   The type of the None singleton.

    `current_period_end: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsListParamsCurrentPeriodEnd`
    :   The type of the None singleton.

    `current_period_start: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsListParamsCurrentPeriodStart`
    :   The type of the None singleton.

    `customer: str`
    :   The type of the None singleton.

    `customer_account: str`
    :   The type of the None singleton.

    `ending_before: str`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `price: str`
    :   The type of the None singleton.

    `starting_after: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

<a id="SubscriptionsListParamsAutomaticTax"></a>

`SubscriptionsListParamsAutomaticTax(*args, **kwargs)`
:   Nested schema for SubscriptionsListParams.automatic_tax

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `enabled: bool`
    :   The type of the None singleton.

<a id="SubscriptionsListParamsCreated"></a>

`SubscriptionsListParamsCreated(*args, **kwargs)`
:   Nested schema for SubscriptionsListParams.created

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: int`
    :   The type of the None singleton.

    `gte: int`
    :   The type of the None singleton.

    `lt: int`
    :   The type of the None singleton.

    `lte: int`
    :   The type of the None singleton.

<a id="SubscriptionsListParamsCurrentPeriodEnd"></a>

`SubscriptionsListParamsCurrentPeriodEnd(*args, **kwargs)`
:   Nested schema for SubscriptionsListParams.current_period_end

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: int`
    :   The type of the None singleton.

    `gte: int`
    :   The type of the None singleton.

    `lt: int`
    :   The type of the None singleton.

    `lte: int`
    :   The type of the None singleton.

<a id="SubscriptionsListParamsCurrentPeriodStart"></a>

`SubscriptionsListParamsCurrentPeriodStart(*args, **kwargs)`
:   Nested schema for SubscriptionsListParams.current_period_start

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: int`
    :   The type of the None singleton.

    `gte: int`
    :   The type of the None singleton.

    `lt: int`
    :   The type of the None singleton.

    `lte: int`
    :   The type of the None singleton.

<a id="SubscriptionsLtCondition"></a>

`SubscriptionsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsSearchFilter`
    :   The type of the None singleton.

<a id="SubscriptionsLteCondition"></a>

`SubscriptionsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsSearchFilter`
    :   The type of the None singleton.

<a id="SubscriptionsNeqCondition"></a>

`SubscriptionsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsSearchFilter`
    :   The type of the None singleton.

<a id="SubscriptionsNotCondition"></a>

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

    `not: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsEqCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsNeqCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsGtCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsGteCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsLtCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsLteCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsInCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsLikeCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsContainsCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsNotCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsAndCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsOrCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsAnyCondition`
    :   The type of the None singleton.

<a id="SubscriptionsOrCondition"></a>

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

    `or: list[airbyte_agent_sdk.connectors.stripe.types.SubscriptionsEqCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsNeqCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsGtCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsGteCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsLtCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsLteCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsInCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsLikeCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsContainsCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsNotCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsAndCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsOrCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsAnyCondition]`
    :   The type of the None singleton.

<a id="SubscriptionsSearchFilter"></a>

`SubscriptionsSearchFilter(*args, **kwargs)`
:   Available fields for filtering subscriptions search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

    `latest_invoice: str | None`
    :   The most recent invoice this subscription has generated, expandable to full invoice object.

    `livemode: bool | None`
    :   Indicates whether the subscription exists in live mode (true) or test mode (false).

    `metadata: dict[str, typing.Any] | None`
    :   Set of key-value pairs that you can attach to the subscription for storing additional structured information.

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

    ### Methods

    `items(self, /) ‑> dict[str, typing.Any] | None`
    :   Return a set-like object providing a view on the dict's items.

<a id="SubscriptionsSearchQuery"></a>

`SubscriptionsSearchQuery(*args, **kwargs)`
:   Search query for subscriptions entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.stripe.types.SubscriptionsEqCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsNeqCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsGtCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsGteCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsLtCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsLteCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsInCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsLikeCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsFuzzyCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsKeywordCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsContainsCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsNotCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsAndCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsOrCondition | airbyte_agent_sdk.connectors.stripe.types.SubscriptionsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.stripe.types.SubscriptionsSortFilter]`
    :   The type of the None singleton.

<a id="SubscriptionsSortFilter"></a>

`SubscriptionsSortFilter(*args, **kwargs)`
:   Available fields for sorting subscriptions search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `application: Literal['asc', 'desc']`
    :   For Connect platforms, the application associated with the subscription.

    `application_fee_percent: Literal['asc', 'desc']`
    :   For Connect platforms, the percentage of the subscription amount taken as an application fee.

    `automatic_tax: Literal['asc', 'desc']`
    :   Automatic tax calculation settings for the subscription.

    `billing: Literal['asc', 'desc']`
    :   Billing mode configuration for the subscription.

    `billing_cycle_anchor: Literal['asc', 'desc']`
    :   Timestamp determining when the billing cycle for the subscription starts.

    `billing_cycle_anchor_config: Literal['asc', 'desc']`
    :   Configuration for the subscription's billing cycle anchor behavior.

    `billing_thresholds: Literal['asc', 'desc']`
    :   Defines thresholds at which an invoice will be sent, controlling billing timing based on usage.

    `cancel_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the subscription is scheduled to be canceled.

    `cancel_at_period_end: Literal['asc', 'desc']`
    :   Boolean indicating whether the subscription will be canceled at the end of the current billing period.

    `canceled_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the subscription was canceled, if applicable.

    `cancellation_details: Literal['asc', 'desc']`
    :   Details about why and how the subscription was canceled.

    `collection_method: Literal['asc', 'desc']`
    :   How invoices are collected (charge_automatically or send_invoice).

    `created: Literal['asc', 'desc']`
    :   Timestamp indicating when the subscription was created.

    `currency: Literal['asc', 'desc']`
    :   Three-letter ISO currency code in lowercase indicating the currency for the subscription.

    `current_period_end: Literal['asc', 'desc']`
    :   Timestamp marking the end of the current billing period.

    `current_period_start: Literal['asc', 'desc']`
    :   Timestamp marking the start of the current billing period.

    `customer: Literal['asc', 'desc']`
    :   ID of the customer who owns the subscription, expandable to full customer object.

    `days_until_due: Literal['asc', 'desc']`
    :   Number of days until the invoice is due for subscriptions using send_invoice collection method.

    `default_payment_method: Literal['asc', 'desc']`
    :   ID of the default payment method for the subscription, taking precedence over default_source.

    `default_source: Literal['asc', 'desc']`
    :   ID of the default payment source for the subscription.

    `default_tax_rates: Literal['asc', 'desc']`
    :   Tax rates that apply to the subscription by default.

    `description: Literal['asc', 'desc']`
    :   Human-readable description of the subscription, displayable to the customer.

    `discount: Literal['asc', 'desc']`
    :   Describes any discount currently applied to the subscription.

    `ended_at: Literal['asc', 'desc']`
    :   Timestamp indicating when the subscription ended, if applicable.

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the subscription object.

    `invoice_settings: Literal['asc', 'desc']`
    :   Settings for invoices generated by this subscription, such as custom fields and footer.

    `is_deleted: Literal['asc', 'desc']`
    :   Indicates whether the subscription has been deleted.

    `latest_invoice: Literal['asc', 'desc']`
    :   The most recent invoice this subscription has generated, expandable to full invoice object.

    `livemode: Literal['asc', 'desc']`
    :   Indicates whether the subscription exists in live mode (true) or test mode (false).

    `metadata: Literal['asc', 'desc']`
    :   Set of key-value pairs that you can attach to the subscription for storing additional structured information.

    `next_pending_invoice_item_invoice: Literal['asc', 'desc']`
    :   Timestamp when the next invoice for pending invoice items will be created.

    `object_: Literal['asc', 'desc']`
    :   String representing the object type, always 'subscription'.

    `on_behalf_of: Literal['asc', 'desc']`
    :   For Connect platforms, the account for which the subscription is being created or managed.

    `pause_collection: Literal['asc', 'desc']`
    :   Configuration for pausing collection on the subscription while retaining the subscription structure.

    `payment_settings: Literal['asc', 'desc']`
    :   Payment settings for invoices generated by this subscription.

    `pending_invoice_item_interval: Literal['asc', 'desc']`
    :   Specifies an interval for aggregating usage records into pending invoice items.

    `pending_setup_intent: Literal['asc', 'desc']`
    :   SetupIntent used for collecting user authentication when updating payment methods without immediate payment.

    `pending_update: Literal['asc', 'desc']`
    :   If specified, pending updates that will be applied to the subscription once the latest_invoice has been paid.

    `plan: Literal['asc', 'desc']`
    :   The plan associated with the subscription (deprecated, use items instead).

    `quantity: Literal['asc', 'desc']`
    :   Quantity of the plan subscribed to (deprecated, use items instead).

    `schedule: Literal['asc', 'desc']`
    :   ID of the subscription schedule managing this subscription's lifecycle, if applicable.

    `start_date: Literal['asc', 'desc']`
    :   Timestamp indicating when the subscription started.

    `status: Literal['asc', 'desc']`
    :   Current status of the subscription (incomplete, incomplete_expired, trialing, active, past_due, canceled, unpaid, or paused).

    `tax_percent: Literal['asc', 'desc']`
    :   The percentage of tax applied to the subscription (deprecated, use default_tax_rates instead).

    `test_clock: Literal['asc', 'desc']`
    :   ID of the test clock associated with this subscription for simulating time-based scenarios.

    `transfer_data: Literal['asc', 'desc']`
    :   For Connect platforms, the account receiving funds from the subscription and optional percentage transferred.

    `trial_end: Literal['asc', 'desc']`
    :   Timestamp indicating when the trial period ends, if applicable.

    `trial_settings: Literal['asc', 'desc']`
    :   Settings related to trial periods, including conditions for ending trials.

    `trial_start: Literal['asc', 'desc']`
    :   Timestamp indicating when the trial period began, if applicable.

    `updated: Literal['asc', 'desc']`
    :   Timestamp indicating when the subscription was last updated.

    ### Methods

    `items(self, /) ‑> Literal['asc', 'desc']`
    :   Return a set-like object providing a view on the dict's items.

<a id="SubscriptionsStringFilter"></a>

`SubscriptionsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `application: str`
    :   For Connect platforms, the application associated with the subscription.

    `application_fee_percent: str`
    :   For Connect platforms, the percentage of the subscription amount taken as an application fee.

    `automatic_tax: str`
    :   Automatic tax calculation settings for the subscription.

    `billing: str`
    :   Billing mode configuration for the subscription.

    `billing_cycle_anchor: str`
    :   Timestamp determining when the billing cycle for the subscription starts.

    `billing_cycle_anchor_config: str`
    :   Configuration for the subscription's billing cycle anchor behavior.

    `billing_thresholds: str`
    :   Defines thresholds at which an invoice will be sent, controlling billing timing based on usage.

    `cancel_at: str`
    :   Timestamp indicating when the subscription is scheduled to be canceled.

    `cancel_at_period_end: str`
    :   Boolean indicating whether the subscription will be canceled at the end of the current billing period.

    `canceled_at: str`
    :   Timestamp indicating when the subscription was canceled, if applicable.

    `cancellation_details: str`
    :   Details about why and how the subscription was canceled.

    `collection_method: str`
    :   How invoices are collected (charge_automatically or send_invoice).

    `created: str`
    :   Timestamp indicating when the subscription was created.

    `currency: str`
    :   Three-letter ISO currency code in lowercase indicating the currency for the subscription.

    `current_period_end: str`
    :   Timestamp marking the end of the current billing period.

    `current_period_start: str`
    :   Timestamp marking the start of the current billing period.

    `customer: str`
    :   ID of the customer who owns the subscription, expandable to full customer object.

    `days_until_due: str`
    :   Number of days until the invoice is due for subscriptions using send_invoice collection method.

    `default_payment_method: str`
    :   ID of the default payment method for the subscription, taking precedence over default_source.

    `default_source: str`
    :   ID of the default payment source for the subscription.

    `default_tax_rates: str`
    :   Tax rates that apply to the subscription by default.

    `description: str`
    :   Human-readable description of the subscription, displayable to the customer.

    `discount: str`
    :   Describes any discount currently applied to the subscription.

    `ended_at: str`
    :   Timestamp indicating when the subscription ended, if applicable.

    `id: str`
    :   Unique identifier for the subscription object.

    `invoice_settings: str`
    :   Settings for invoices generated by this subscription, such as custom fields and footer.

    `is_deleted: str`
    :   Indicates whether the subscription has been deleted.

    `latest_invoice: str`
    :   The most recent invoice this subscription has generated, expandable to full invoice object.

    `livemode: str`
    :   Indicates whether the subscription exists in live mode (true) or test mode (false).

    `metadata: str`
    :   Set of key-value pairs that you can attach to the subscription for storing additional structured information.

    `next_pending_invoice_item_invoice: str`
    :   Timestamp when the next invoice for pending invoice items will be created.

    `object_: str`
    :   String representing the object type, always 'subscription'.

    `on_behalf_of: str`
    :   For Connect platforms, the account for which the subscription is being created or managed.

    `pause_collection: str`
    :   Configuration for pausing collection on the subscription while retaining the subscription structure.

    `payment_settings: str`
    :   Payment settings for invoices generated by this subscription.

    `pending_invoice_item_interval: str`
    :   Specifies an interval for aggregating usage records into pending invoice items.

    `pending_setup_intent: str`
    :   SetupIntent used for collecting user authentication when updating payment methods without immediate payment.

    `pending_update: str`
    :   If specified, pending updates that will be applied to the subscription once the latest_invoice has been paid.

    `plan: str`
    :   The plan associated with the subscription (deprecated, use items instead).

    `quantity: str`
    :   Quantity of the plan subscribed to (deprecated, use items instead).

    `schedule: str`
    :   ID of the subscription schedule managing this subscription's lifecycle, if applicable.

    `start_date: str`
    :   Timestamp indicating when the subscription started.

    `status: str`
    :   Current status of the subscription (incomplete, incomplete_expired, trialing, active, past_due, canceled, unpaid, or paused).

    `tax_percent: str`
    :   The percentage of tax applied to the subscription (deprecated, use default_tax_rates instead).

    `test_clock: str`
    :   ID of the test clock associated with this subscription for simulating time-based scenarios.

    `transfer_data: str`
    :   For Connect platforms, the account receiving funds from the subscription and optional percentage transferred.

    `trial_end: str`
    :   Timestamp indicating when the trial period ends, if applicable.

    `trial_settings: str`
    :   Settings related to trial periods, including conditions for ending trials.

    `trial_start: str`
    :   Timestamp indicating when the trial period began, if applicable.

    `updated: str`
    :   Timestamp indicating when the subscription was last updated.

    ### Methods

    `items(self, /) ‑> str`
    :   Return a set-like object providing a view on the dict's items.