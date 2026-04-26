---
id: airbyte_agent_sdk-connectors-stripe-index
title: airbyte_agent_sdk.connectors.stripe.index
---

Module airbyte_agent_sdk.connectors.stripe
==========================================
Stripe connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.stripe.connector
* airbyte_agent_sdk.connectors.stripe.connector_model
* airbyte_agent_sdk.connectors.stripe.models
* airbyte_agent_sdk.connectors.stripe.types

Classes
-------

<a id="AirbyteAuthConfig"></a>

`AirbyteAuthConfig(**data: Any)`
:   Authentication configuration for Airbyte hosted mode execution.
    
    Pass this to the connector's `auth_config` parameter to use hosted mode,
    where API credentials are stored securely in Airbyte Cloud.
    
    For hosted mode execution, provide client credentials with either:
    - `connector_id`: Direct connector/source ID (skips lookup)
    - `workspace_name`: Workspace name for connector lookup
    
    Attributes:
        workspace_name: Workspace name for hosted mode connector lookup
        organization_id: Optional Airbyte organization ID for multi-org selection
        airbyte_client_id: Airbyte OAuth client ID (required for hosted mode)
        airbyte_client_secret: Airbyte OAuth client secret (required for hosted mode)
        connector_id: Specific connector/source ID (skips lookup if provided)
    
    Examples:
        # Hosted mode with connector_id (no lookup needed)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with workspace_name (lookup by workspace)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `airbyte_client_id: str | None`
    :   The type of the None singleton.

    `airbyte_client_secret: str | None`
    :   The type of the None singleton.

    `connector_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organization_id: str | None`
    :   The type of the None singleton.

    `workspace_name: str | None`
    :   The type of the None singleton.

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

<a id="StripeConnector"></a>

`StripeConnector(auth_config: StripeAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Stripe API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new stripe connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., StripeAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = StripeConnector(auth_config=StripeAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = StripeConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = StripeConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )

    ### Class variables

    `connector_name`
    :   The type of the None singleton.

    `connector_version`
    :   The type of the None singleton.

    `sdk_version`
    :   The type of the None singleton.

    ### Static methods

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'StripeAuthConfig'", name: str | None = None, replication_config: "'StripeReplicationConfig' | None" = None, source_template_id: str | None = None)`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config (same as local mode)
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Typed replication settings.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A StripeConnector instance configured in hosted mode
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await StripeConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=StripeAuthConfig(api_key="..."),
            )
        
            # With replication config (required for this connector):
            connector = await StripeConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=StripeAuthConfig(api_key="..."),
                replication_config=StripeReplicationConfig(account_id="..."),
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @StripeConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @StripeConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
        Args:
            update_docstring: When True, append connector capabilities to __doc__.
            max_output_chars: Max serialized output size before raising. Use None to disable.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.
        
        Example:
            connector = await StripeConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.stripe.models.StripeCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            StripeCheckResult with status ("healthy" or "unhealthy") and optional error message
        
        Example:
            result = await connector.check()
            if result.status == "healthy":
                print("Connection verified!")
            else:
                print(f"Check failed: \{result.error\}")

    `close(self)`
    :   Close the connector and release resources.

    `entity_schema(self, entity: str) ‑> dict[str, typing.Any] | None`
    :   Get the JSON schema for an entity.
        
        Args:
            entity: Entity name (e.g., "contacts", "companies")
        
        Returns:
            JSON schema dict describing the entity structure, or None if not found.
        
        Example:
            schema = connector.entity_schema("contacts")
            if schema:
                print(f"Contact properties: \{list(schema.get('properties', \{\}).keys())\}")

    `execute(self, entity: str, action: "Literal['list', 'create', 'get', 'update', 'delete', 'api_search', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
    :   Execute an entity operation with full type safety.
        
        This is the recommended interface for blessed connectors as it:
        - Uses the same signature as non-blessed connectors
        - Provides full IDE autocomplete for entity/action/params
        - Makes migration from generic to blessed connectors seamless
        
        Args:
            entity: Entity name (e.g., "customers")
            action: Operation action (e.g., "create", "get", "list")
            params: Operation parameters (typed based on entity+action)
        
        Returns:
            Typed response based on the operation
        
        Example:
            customer = await connector.execute(
                entity="customers",
                action="get",
                params=\{"id": "cus_123"\}
            )

    `list_entities(self) ‑> list[dict[str, typing.Any]]`
    :   Get structured data about available entities, actions, and parameters.
        
        Returns a list of entity descriptions with:
        - entity_name: Name of the entity (e.g., "contacts", "deals")
        - description: Entity description from the first endpoint
        - available_actions: List of actions (e.g., ["list", "get", "create"])
        - parameters: Dict mapping action -> list of parameter dicts
        
        Example:
            entities = connector.list_entities()
            for entity in entities:
                print(f"\{entity['entity_name']\}: \{entity['available_actions']\}")

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