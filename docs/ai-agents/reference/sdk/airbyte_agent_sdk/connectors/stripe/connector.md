---
id: airbyte_agent_sdk-connectors-stripe-connector
title: airbyte_agent_sdk.connectors.stripe.connector
---

Module airbyte_agent_sdk.connectors.stripe.connector
====================================================
Stripe connector.

Classes
-------

<a id="BalanceQuery"></a>

`BalanceQuery(connector: StripeConnector)`
:   Query class for Balance entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.Balance`
    :   Retrieves the current account balance, based on the authentication that was used to make the request.
        
        Returns:
            Balance

<a id="BalanceTransactionsQuery"></a>

`BalanceTransactionsQuery(connector: StripeConnector)`
:   Query class for BalanceTransactions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.BalanceTransaction`
    :   Retrieves the balance transaction with the given ID.
        
        Args:
            id: The ID of the desired balance transaction
            **kwargs: Additional parameters
        
        Returns:
            BalanceTransaction

    `list(self, created: BalanceTransactionsListParamsCreated | None = None, currency: str | None = None, ending_before: str | None = None, limit: int | None = None, payout: str | None = None, source: str | None = None, starting_after: str | None = None, type: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[BalanceTransaction], BalanceTransactionsListResultMeta]`
    :   Returns a list of transactions that have contributed to the Stripe account balance (e.g., charges, transfers, and so forth). The transactions are returned in sorted order, with the most recent transactions appearing first.
        
        Args:
            created: Only return transactions that were created during the given date interval.
            currency: Only return transactions in a certain currency. Three-letter ISO currency code, in lowercase.
            ending_before: A cursor for use in pagination. ending_before is an object ID that defines your place in the list.
            limit: A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
            payout: For automatic Stripe payouts only, only returns transactions that were paid out on the specified payout ID.
            source: Only returns the original transaction.
            starting_after: A cursor for use in pagination. starting_after is an object ID that defines your place in the list.
            type: Only returns transactions of the given type.
            **kwargs: Additional parameters
        
        Returns:
            BalanceTransactionsListResult

<a id="ChargesQuery"></a>

`ChargesQuery(connector: StripeConnector)`
:   Query class for Charges entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, query: str, limit: int | None = None, page: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult[ChargeSearchResult]`
    :   Search for charges using Stripe's Search Query Language
        
        Args:
            query: The search query string using Stripe's Search Query Language
            limit: A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
            page: A cursor for pagination across multiple pages of results. Don’t include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results.
            **kwargs: Additional parameters
        
        Returns:
            ChargesApiSearchResult

    `context_store_search(self, query: ChargesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult[ChargesSearchData]`
    :   Search charges records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (ChargesSearchFilter):
        - amount: Amount intended to be collected by this payment in the smallest currency unit (e.g., 100 cents for $1.00), supporting up to eight digits.
        - amount_captured: Amount that was actually captured from this charge.
        - amount_refunded: Amount that has been refunded back to the customer.
        - amount_updates: Updates to the amount that have been made during the charge lifecycle.
        - application: ID of the application that created this charge (Connect only).
        - application_fee: ID of the application fee associated with this charge (Connect only).
        - application_fee_amount: The amount of the application fee deducted from this charge (Connect only).
        - balance_transaction: ID of the balance transaction that describes the impact of this charge on your account balance (excluding refunds or disputes).
        - billing_details: Billing information associated with the payment method at the time of the transaction, including name, email, phone, and address.
        - calculated_statement_descriptor: The full statement descriptor that appears on the customer's credit card statement, combining prefix and suffix.
        - captured: Whether the charge has been captured and funds transferred to your account.
        - card: Deprecated card object containing payment card details if a card was used.
        - created: Timestamp indicating when the charge was created.
        - currency: Three-letter ISO currency code in lowercase (e.g., 'usd', 'eur') for the charge amount.
        - customer: ID of the customer this charge is for, if one exists.
        - description: An arbitrary string attached to the charge, often useful for displaying to users or internal reference.
        - destination: ID of the destination account where funds are transferred (Connect only).
        - dispute: ID of the dispute object if the charge has been disputed.
        - disputed: Whether the charge has been disputed by the customer with their card issuer.
        - failure_balance_transaction: ID of the balance transaction that describes the reversal of funds if the charge failed.
        - failure_code: Error code explaining the reason for charge failure, if applicable.
        - failure_message: Human-readable message providing more details about why the charge failed.
        - fraud_details: Information about fraud assessments and user reports related to this charge.
        - id: Unique identifier for the charge, used to link transactions across other records.
        - invoice: ID of the invoice this charge is for, if the charge was created by invoicing.
        - livemode: Whether the charge occurred in live mode (true) or test mode (false).
        - metadata: Key-value pairs for storing additional structured information about the charge, useful for internal tracking.
        - object_: String representing the object type, always 'charge' for charge objects.
        - on_behalf_of: ID of the account on whose behalf the charge was made (Connect only).
        - order: Deprecated field for order information associated with this charge.
        - outcome: Details about the outcome of the charge, including network status, risk assessment, and reason codes.
        - paid: Whether the charge succeeded and funds were successfully collected.
        - payment_intent: ID of the PaymentIntent associated with this charge, if one exists.
        - payment_method: ID of the payment method used for this charge.
        - payment_method_details: Details about the payment method at the time of the transaction, including card brand, network, and authentication results.
        - receipt_email: Email address to which the receipt for this charge was sent.
        - receipt_number: Receipt number that appears on email receipts sent for this charge.
        - receipt_url: URL to a hosted receipt page for this charge, viewable by the customer.
        - refunded: Whether the charge has been fully refunded (partial refunds will still show as false).
        - refunds: List of refunds that have been applied to this charge.
        - review: ID of the review object associated with this charge, if it was flagged for manual review.
        - shipping: Shipping information for the charge, including recipient name, address, and tracking details.
        - source: Deprecated payment source object used to create this charge.
        - source_transfer: ID of the transfer from a source account if funds came from another Stripe account (Connect only).
        - statement_description: Deprecated alias for statement_descriptor.
        - statement_descriptor: Statement descriptor that overrides the account default for card charges, appearing on the customer's statement.
        - statement_descriptor_suffix: Suffix concatenated to the account's statement descriptor prefix to form the complete descriptor on customer statements.
        - status: Current status of the payment: 'succeeded' (completed), 'pending' (processing), or 'failed' (unsuccessful).
        - transfer_data: Object containing destination and amount for transfers to connected accounts (Connect only).
        - transfer_group: String identifier for grouping related charges and transfers together (Connect only).
        - updated: Timestamp of the last update to this charge object.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            ChargesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.Charge`
    :   Retrieves the details of a charge that has previously been created
        
        Args:
            id: The charge ID
            **kwargs: Additional parameters
        
        Returns:
            Charge

    `list(self, created: ChargesListParamsCreated | None = None, customer: str | None = None, ending_before: str | None = None, limit: int | None = None, payment_intent: str | None = None, starting_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Charge], ChargesListResultMeta]`
    :   Returns a list of charges you've previously created. The charges are returned in sorted order, with the most recent charges appearing first.
        
        Args:
            created: Only return customers that were created during the given date interval.
            customer: Only return charges for the customer specified by this customer ID
            ending_before: A cursor for use in pagination. ending_before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj_bar, your subsequent call can include ending_before=obj_bar in order to fetch the previous page of the list.
            limit: A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
            payment_intent: Only return charges that were created by the PaymentIntent specified by this ID
            starting_after: A cursor for use in pagination. starting_after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include starting_after=obj_foo in order to fetch the next page of the list.
            **kwargs: Additional parameters
        
        Returns:
            ChargesListResult

<a id="CustomersQuery"></a>

`CustomersQuery(connector: StripeConnector)`
:   Query class for Customers entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, query: str, limit: int | None = None, page: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Customer], CustomersApiSearchResultMeta]`
    :   Search for customers using Stripe's Search Query Language.
        
        Args:
            query: The search query string using Stripe's Search Query Language
            limit: A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
            page: A cursor for pagination across multiple pages of results. Don’t include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results.
            **kwargs: Additional parameters
        
        Returns:
            CustomersApiSearchResult

    `context_store_search(self, query: CustomersSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult[CustomersSearchData]`
    :   Search customers records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (CustomersSearchFilter):
        - account_balance: Current balance value representing funds owed by or to the customer.
        - address: The customer's address information including line1, line2, city, state, postal code, and country.
        - balance: Current balance (positive or negative) that is automatically applied to the customer's next invoice.
        - cards: Card payment methods associated with the customer account.
        - created: Timestamp indicating when the customer object was created.
        - currency: Three-letter ISO currency code representing the customer's default currency.
        - default_card: The default card to be used for charges when no specific payment method is provided.
        - default_source: The default payment source (card or bank account) for the customer.
        - delinquent: Boolean indicating whether the customer is currently delinquent on payments.
        - description: An arbitrary string attached to the customer, often useful for displaying to users.
        - discount: Discount object describing any active discount applied to the customer.
        - email: The customer's email address for communication and tracking purposes.
        - id: Unique identifier for the customer object.
        - invoice_prefix: The prefix for invoice numbers generated for this customer.
        - invoice_settings: Customer's invoice-related settings including default payment method and custom fields.
        - is_deleted: Boolean indicating whether the customer has been deleted.
        - livemode: Boolean indicating whether the object exists in live mode or test mode.
        - metadata: Set of key-value pairs for storing additional structured information about the customer.
        - name: The customer's full name or business name.
        - next_invoice_sequence: The sequence number for the next invoice generated for this customer.
        - object_: String representing the object type, always 'customer'.
        - phone: The customer's phone number.
        - preferred_locales: Array of preferred locales for the customer, used for invoice and receipt localization.
        - shipping: Mailing and shipping address for the customer, appears on invoices emailed to the customer.
        - sources: Payment sources (cards, bank accounts) attached to the customer for making payments.
        - subscriptions: List of active subscriptions associated with the customer.
        - tax_exempt: Describes the customer's tax exemption status (none, exempt, or reverse).
        - tax_info: Tax identification information for the customer.
        - tax_info_verification: Verification status of the customer's tax information.
        - test_clock: ID of the test clock associated with this customer for testing time-dependent scenarios.
        - updated: Timestamp indicating when the customer object was last updated.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            CustomersSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.Customer`
    :   Creates a new customer object.
        
        Returns:
            Customer

    `delete(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.CustomerDeletedResponse`
    :   Permanently deletes a customer. It cannot be undone.
        
        Args:
            id: The customer ID
            **kwargs: Additional parameters
        
        Returns:
            CustomerDeletedResponse

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.Customer`
    :   Retrieves a Customer object.
        
        Args:
            id: The customer ID
            **kwargs: Additional parameters
        
        Returns:
            Customer

    `list(self, limit: int | None = None, starting_after: str | None = None, ending_before: str | None = None, email: str | None = None, created: CustomersListParamsCreated | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Customer], CustomersListResultMeta]`
    :   Returns a list of your customers. The customers are returned sorted by creation date, with the most recent customers appearing first.
        
        Args:
            limit: A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
            starting_after: A cursor for use in pagination. starting_after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include starting_after=obj_foo in order to fetch the next page of the list.
            ending_before: A cursor for use in pagination. ending_before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj_bar, your subsequent call can include ending_before=obj_bar in order to fetch the previous page of the list.
            email: A case-sensitive filter on the list based on the customer's email field. The value must be a string.
            created: Only return customers that were created during the given date interval.
            **kwargs: Additional parameters
        
        Returns:
            CustomersListResult

    `update(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.Customer`
    :   Updates the specified customer by setting the values of the parameters passed.
        
        Args:
            id: The customer ID
            **kwargs: Additional parameters
        
        Returns:
            Customer

<a id="DisputesQuery"></a>

`DisputesQuery(connector: StripeConnector)`
:   Query class for Disputes entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.Dispute`
    :   Retrieves the dispute with the given ID.
        
        Args:
            id: The ID of the dispute
            **kwargs: Additional parameters
        
        Returns:
            Dispute

    `list(self, charge: str | None = None, created: DisputesListParamsCreated | None = None, ending_before: str | None = None, limit: int | None = None, payment_intent: str | None = None, starting_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Dispute], DisputesListResultMeta]`
    :   Returns a list of your disputes. The disputes are returned sorted by creation date, with the most recent disputes appearing first.
        
        Args:
            charge: Only return disputes associated to the charge specified by this charge ID
            created: Only return disputes that were created during the given date interval.
            ending_before: A cursor for use in pagination. ending_before is an object ID that defines your place in the list.
            limit: A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
            payment_intent: Only return disputes associated to the PaymentIntent specified by this PaymentIntent ID
            starting_after: A cursor for use in pagination. starting_after is an object ID that defines your place in the list.
            **kwargs: Additional parameters
        
        Returns:
            DisputesListResult

<a id="InvoicesQuery"></a>

`InvoicesQuery(connector: StripeConnector)`
:   Query class for Invoices entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, query: str, limit: int | None = None, page: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult[InvoiceSearchResult]`
    :   Search for invoices using Stripe's Search Query Language
        
        Args:
            query: The search query string using Stripe's Search Query Language
            limit: A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
            page: A cursor for pagination across multiple pages of results. Don’t include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results.
            **kwargs: Additional parameters
        
        Returns:
            InvoicesApiSearchResult

    `context_store_search(self, query: InvoicesSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult[InvoicesSearchData]`
    :   Search invoices records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (InvoicesSearchFilter):
        - account_country: The country of the business associated with this invoice, commonly used to display localized content.
        - account_name: The public name of the business associated with this invoice.
        - account_tax_ids: Tax IDs of the account associated with this invoice.
        - amount_due: Total amount, in smallest currency unit, that is due and owed by the customer.
        - amount_paid: Total amount, in smallest currency unit, that has been paid by the customer.
        - amount_remaining: The difference between amount_due and amount_paid, representing the outstanding balance.
        - amount_shipping: Total amount of shipping costs on the invoice.
        - application: ID of the Connect application that created this invoice.
        - application_fee: Amount of application fee charged for this invoice in a Connect scenario.
        - application_fee_amount: The fee in smallest currency unit that is collected by the application in a Connect scenario.
        - attempt_count: Number of payment attempts made for this invoice.
        - attempted: Whether an attempt has been made to pay the invoice.
        - auto_advance: Controls whether Stripe performs automatic collection of the invoice.
        - automatic_tax: Settings and status for automatic tax calculation on this invoice.
        - billing: Billing method used for the invoice (charge_automatically or send_invoice).
        - billing_reason: Indicates the reason why the invoice was created (subscription_cycle, manual, etc.).
        - charge: ID of the latest charge generated for this invoice, if any.
        - closed: Whether the invoice has been marked as closed and no longer open for collection.
        - collection_method: Method by which the invoice is collected: charge_automatically or send_invoice.
        - created: Timestamp indicating when the invoice was created.
        - currency: Three-letter ISO currency code in which the invoice is denominated.
        - custom_fields: Custom fields displayed on the invoice as specified by the account.
        - customer: The customer object or ID associated with this invoice.
        - customer_address: The customer's address at the time the invoice was finalized.
        - customer_email: The customer's email address at the time the invoice was finalized.
        - customer_name: The customer's name at the time the invoice was finalized.
        - customer_phone: The customer's phone number at the time the invoice was finalized.
        - customer_shipping: The customer's shipping information at the time the invoice was finalized.
        - customer_tax_exempt: The customer's tax exempt status at the time the invoice was finalized.
        - customer_tax_ids: The customer's tax IDs at the time the invoice was finalized.
        - default_payment_method: Default payment method for the invoice, used if no other method is specified.
        - default_source: Default payment source for the invoice if no payment method is set.
        - default_tax_rates: The tax rates applied to the invoice by default.
        - description: An arbitrary string attached to the invoice, often displayed to customers.
        - discount: The discount object applied to the invoice, if any.
        - discounts: Array of discount IDs or objects currently applied to this invoice.
        - due_date: The date by which payment on this invoice is due, if the invoice is not auto-collected.
        - effective_at: Timestamp when the invoice becomes effective and finalized for payment.
        - ending_balance: The customer's ending account balance after this invoice is finalized.
        - footer: Footer text displayed on the invoice.
        - forgiven: Whether the invoice has been forgiven and is considered paid without actual payment.
        - from_invoice: Details about the invoice this invoice was created from, if applicable.
        - hosted_invoice_url: URL for the hosted invoice page where customers can view and pay the invoice.
        - id: Unique identifier for the invoice object.
        - invoice_pdf: URL for the PDF version of the invoice.
        - is_deleted: Indicates whether this invoice has been deleted.
        - issuer: Details about the entity issuing the invoice.
        - last_finalization_error: The error encountered during the last finalization attempt, if any.
        - latest_revision: The latest revision of the invoice, if revisions are enabled.
        - lines: The individual line items that make up the invoice, representing products, services, or fees.
        - livemode: Indicates whether the invoice exists in live mode (true) or test mode (false).
        - metadata: Key-value pairs for storing additional structured information about the invoice.
        - next_payment_attempt: Timestamp of the next automatic payment attempt for this invoice, if applicable.
        - number: A unique, human-readable identifier for this invoice, often shown to customers.
        - object_: String representing the object type, always 'invoice'.
        - on_behalf_of: The account on behalf of which the invoice is being created, used in Connect scenarios.
        - paid: Whether the invoice has been paid in full.
        - paid_out_of_band: Whether payment was made outside of Stripe and manually marked as paid.
        - payment: ID of the payment associated with this invoice, if any.
        - payment_intent: The PaymentIntent associated with this invoice for processing payment.
        - payment_settings: Configuration settings for how payment should be collected on this invoice.
        - period_end: End date of the billing period covered by this invoice.
        - period_start: Start date of the billing period covered by this invoice.
        - post_payment_credit_notes_amount: Total amount of credit notes issued after the invoice was paid.
        - pre_payment_credit_notes_amount: Total amount of credit notes applied before payment was attempted.
        - quote: The quote from which this invoice was generated, if applicable.
        - receipt_number: The receipt number displayed on the invoice, if available.
        - rendering: Settings that control how the invoice is rendered for display.
        - rendering_options: Options for customizing the visual rendering of the invoice.
        - shipping_cost: Total cost of shipping charges included in the invoice.
        - shipping_details: Detailed shipping information for the invoice, including address and carrier.
        - starting_balance: The customer's starting account balance at the beginning of the billing period.
        - statement_description: Extra information about the invoice that appears on the customer's credit card statement.
        - statement_descriptor: A dynamic descriptor that appears on the customer's credit card statement for this invoice.
        - status: The status of the invoice: draft, open, paid, void, or uncollectible.
        - status_transitions: Timestamps tracking when the invoice transitioned between different statuses.
        - subscription: The subscription this invoice was generated for, if applicable.
        - subscription_details: Additional details about the subscription associated with this invoice.
        - subtotal: Total of all line items before discounts or tax are applied.
        - subtotal_excluding_tax: The subtotal amount excluding any tax calculations.
        - tax: Total tax amount applied to the invoice.
        - tax_percent: The percentage of tax applied to the invoice (deprecated, use total_tax_amounts instead).
        - test_clock: ID of the test clock this invoice belongs to, used for testing time-dependent billing.
        - total: Total amount of the invoice after all line items, discounts, and taxes are calculated.
        - total_discount_amounts: Array of the total discount amounts applied, broken down by discount.
        - total_excluding_tax: Total amount of the invoice excluding all tax calculations.
        - total_tax_amounts: Array of tax amounts applied to the invoice, broken down by tax rate.
        - transfer_data: Information about the transfer of funds associated with this invoice in Connect scenarios.
        - updated: Timestamp indicating when the invoice was last updated.
        - webhooks_delivered_at: Timestamp indicating when webhooks for this invoice were successfully delivered.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            InvoicesSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.Invoice`
    :   Retrieves the invoice with the given ID
        
        Args:
            id: The invoice ID
            **kwargs: Additional parameters
        
        Returns:
            Invoice

    `list(self, collection_method: str | None = None, created: InvoicesListParamsCreated | None = None, customer: str | None = None, customer_account: str | None = None, ending_before: str | None = None, limit: int | None = None, starting_after: str | None = None, status: str | None = None, subscription: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Invoice], InvoicesListResultMeta]`
    :   Returns a list of invoices
        
        Args:
            collection_method: The collection method of the invoices to retrieve
            created: Only return customers that were created during the given date interval.
            customer: Only return invoices for the customer specified by this customer ID.
            customer_account: Only return invoices for the account specified by this account ID
            ending_before: A cursor for use in pagination. ending_before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj_bar, your subsequent call can include ending_before=obj_bar in order to fetch the previous page of the list.
            limit: A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
            starting_after: A cursor for use in pagination. starting_after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include starting_after=obj_foo in order to fetch the next page of the list.
            status: The status of the invoices to retrieve
            subscription: Only return invoices for the subscription specified by this subscription ID.
            **kwargs: Additional parameters
        
        Returns:
            InvoicesListResult

<a id="PaymentIntentsQuery"></a>

`PaymentIntentsQuery(connector: StripeConnector)`
:   Query class for PaymentIntents entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, query: str, limit: int | None = None, page: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[PaymentIntent], PaymentIntentsApiSearchResultMeta]`
    :   Search for payment intents using Stripe's Search Query Language.
        
        Args:
            query: The search query string using Stripe's Search Query Language
            limit: A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
            page: A cursor for pagination across multiple pages of results. Don't include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results.
            **kwargs: Additional parameters
        
        Returns:
            PaymentIntentsApiSearchResult

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.PaymentIntent`
    :   Retrieves the details of a PaymentIntent that has previously been created.
        
        Args:
            id: The ID of the payment intent
            **kwargs: Additional parameters
        
        Returns:
            PaymentIntent

    `list(self, created: PaymentIntentsListParamsCreated | None = None, customer: str | None = None, customer_account: str | None = None, ending_before: str | None = None, limit: int | None = None, starting_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[PaymentIntent], PaymentIntentsListResultMeta]`
    :   Returns a list of PaymentIntents. The payment intents are returned sorted by creation date, with the most recent payment intents appearing first.
        
        Args:
            created: Only return payment intents that were created during the given date interval.
            customer: Only return payment intents for the customer specified by this customer ID
            customer_account: Only return payment intents for the account specified by this account ID
            ending_before: A cursor for use in pagination. ending_before is an object ID that defines your place in the list.
            limit: A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
            starting_after: A cursor for use in pagination. starting_after is an object ID that defines your place in the list.
            **kwargs: Additional parameters
        
        Returns:
            PaymentIntentsListResult

<a id="PayoutsQuery"></a>

`PayoutsQuery(connector: StripeConnector)`
:   Query class for Payouts entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.Payout`
    :   Retrieves the details of an existing payout. Supply the unique payout ID from either a payout creation request or the payout list, and Stripe will return the corresponding payout information.
        
        Args:
            id: The ID of the payout
            **kwargs: Additional parameters
        
        Returns:
            Payout

    `list(self, arrival_date: PayoutsListParamsArrivalDate | None = None, created: PayoutsListParamsCreated | None = None, destination: str | None = None, ending_before: str | None = None, limit: int | None = None, starting_after: str | None = None, status: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Payout], PayoutsListResultMeta]`
    :   Returns a list of existing payouts sent to third-party bank accounts or payouts that Stripe sent to you. The payouts return in sorted order, with the most recently created payouts appearing first.
        
        Args:
            arrival_date: Filter payouts by expected arrival date range.
            created: Only return payouts that were created during the given date interval.
            destination: The ID of the external account the payout was sent to.
            ending_before: A cursor for use in pagination. ending_before is an object ID that defines your place in the list.
            limit: A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
            starting_after: A cursor for use in pagination. starting_after is an object ID that defines your place in the list.
            status: Only return payouts that have the given status
            **kwargs: Additional parameters
        
        Returns:
            PayoutsListResult

<a id="ProductsQuery"></a>

`ProductsQuery(connector: StripeConnector)`
:   Query class for Products entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, query: str, limit: int | None = None, page: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Product], ProductsApiSearchResultMeta]`
    :   Search for products using Stripe's Search Query Language.
        
        Args:
            query: The search query string using Stripe's Search Query Language
            limit: A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
            page: A cursor for pagination across multiple pages of results. Don't include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results.
            **kwargs: Additional parameters
        
        Returns:
            ProductsApiSearchResult

    `create(self, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.Product`
    :   Creates a new product object. Your product's name, description, and other information will be displayed in all product and invoice displays.
        
        Returns:
            Product

    `delete(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.ProductDeletedResponse`
    :   Deletes a product. Deleting a product is only possible if it has no prices associated with it.
        
        Args:
            id: The product ID
            **kwargs: Additional parameters
        
        Returns:
            ProductDeletedResponse

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.Product`
    :   Retrieves the details of an existing product. Supply the unique product ID and Stripe will return the corresponding product information.
        
        Args:
            id: The product ID
            **kwargs: Additional parameters
        
        Returns:
            Product

    `list(self, active: bool | None = None, created: ProductsListParamsCreated | None = None, ending_before: str | None = None, ids: list[str] | None = None, limit: int | None = None, shippable: bool | None = None, starting_after: str | None = None, url: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Product], ProductsListResultMeta]`
    :   Returns a list of your products. The products are returned sorted by creation date, with the most recent products appearing first.
        
        Args:
            active: Only return products that are active or inactive
            created: Only return products that were created during the given date interval.
            ending_before: A cursor for use in pagination. ending_before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj_bar, your subsequent call can include ending_before=obj_bar in order to fetch the previous page of the list.
            ids: Only return products with the given IDs
            limit: A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
            shippable: Only return products that can be shipped
            starting_after: A cursor for use in pagination. starting_after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include starting_after=obj_foo in order to fetch the next page of the list.
            url: Only return products with the given url
            **kwargs: Additional parameters
        
        Returns:
            ProductsListResult

    `update(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.Product`
    :   Updates the specific product by setting the values of the parameters passed. Any parameters not provided will be left unchanged.
        
        Args:
            id: The product ID
            **kwargs: Additional parameters
        
        Returns:
            Product

<a id="RefundsQuery"></a>

`RefundsQuery(connector: StripeConnector)`
:   Query class for Refunds entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `context_store_search(self, query: RefundsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult[RefundsSearchData]`
    :   Search refunds records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (RefundsSearchFilter):
        - amount: Amount refunded, in cents (the smallest currency unit).
        - balance_transaction: ID of the balance transaction that describes the impact of this refund on your account balance.
        - charge: ID of the charge that was refunded.
        - created: Timestamp indicating when the refund was created.
        - currency: Three-letter ISO currency code in lowercase representing the currency of the refund.
        - destination_details: Details about the destination where the refunded funds should be sent.
        - id: Unique identifier for the refund object.
        - metadata: Set of key-value pairs that you can attach to an object for storing additional structured information.
        - object_: String representing the object type, always 'refund'.
        - payment_intent: ID of the PaymentIntent that was refunded.
        - reason: Reason for the refund, either user-provided (duplicate, fraudulent, or requested_by_customer) or generated by Stripe internally (expired_uncaptured_charge).
        - receipt_number: The transaction number that appears on email receipts sent for this refund.
        - source_transfer_reversal: ID of the transfer reversal that was created as a result of refunding a transfer (Connect only).
        - status: Status of the refund (pending, requires_action, succeeded, failed, or canceled).
        - transfer_reversal: ID of the reversal of the transfer that funded the charge being refunded (Connect only).
        - updated: Timestamp indicating when the refund was last updated.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            RefundsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `create(self, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.Refund`
    :   When you create a new refund, you must specify a Charge or a PaymentIntent object on which to create it. Creating a new refund will refund a charge that has previously been created but not yet refunded.
        
        Returns:
            Refund

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.Refund`
    :   Retrieves the details of an existing refund
        
        Args:
            id: The refund ID
            **kwargs: Additional parameters
        
        Returns:
            Refund

    `list(self, charge: str | None = None, created: RefundsListParamsCreated | None = None, ending_before: str | None = None, limit: int | None = None, payment_intent: str | None = None, starting_after: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Refund], RefundsListResultMeta]`
    :   Returns a list of all refunds you've previously created. The refunds are returned in sorted order, with the most recent refunds appearing first.
        
        Args:
            charge: Only return refunds for the charge specified by this charge ID
            created: Only return customers that were created during the given date interval.
            ending_before: A cursor for use in pagination. ending_before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj_bar, your subsequent call can include ending_before=obj_bar in order to fetch the previous page of the list.
            limit: A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
            payment_intent: Only return refunds for the PaymentIntent specified by this ID
            starting_after: A cursor for use in pagination. starting_after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include starting_after=obj_foo in order to fetch the next page of the list.
            **kwargs: Additional parameters
        
        Returns:
            RefundsListResult

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

<a id="SubscriptionsQuery"></a>

`SubscriptionsQuery(connector: StripeConnector)`
:   Query class for Subscriptions entity operations.
    
    Initialize query with connector reference.

    ### Methods

    `api_search(self, query: str, limit: int | None = None, page: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResult[SubscriptionSearchResult]`
    :   Search for subscriptions using Stripe's Search Query Language
        
        Args:
            query: The search query string using Stripe's Search Query Language
            limit: A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
            page: A cursor for pagination across multiple pages of results. Don't include this parameter on the first call. Use the next_page value returned in a previous response to request subsequent results.
            **kwargs: Additional parameters
        
        Returns:
            SubscriptionsApiSearchResult

    `context_store_search(self, query: SubscriptionsSearchQuery, limit: int | None = None, cursor: str | None = None, fields: list[list[str]] | None = None) ‑> airbyte_agent_sdk.connectors.stripe.models.AirbyteSearchResult[SubscriptionsSearchData]`
    :   Search subscriptions records from Airbyte cache.
        
        This operation searches cached data from Airbyte syncs.
        Only available in hosted execution mode.
        
        Available filter fields (SubscriptionsSearchFilter):
        - application: For Connect platforms, the application associated with the subscription.
        - application_fee_percent: For Connect platforms, the percentage of the subscription amount taken as an application fee.
        - automatic_tax: Automatic tax calculation settings for the subscription.
        - billing: Billing mode configuration for the subscription.
        - billing_cycle_anchor: Timestamp determining when the billing cycle for the subscription starts.
        - billing_cycle_anchor_config: Configuration for the subscription's billing cycle anchor behavior.
        - billing_thresholds: Defines thresholds at which an invoice will be sent, controlling billing timing based on usage.
        - cancel_at: Timestamp indicating when the subscription is scheduled to be canceled.
        - cancel_at_period_end: Boolean indicating whether the subscription will be canceled at the end of the current billing period.
        - canceled_at: Timestamp indicating when the subscription was canceled, if applicable.
        - cancellation_details: Details about why and how the subscription was canceled.
        - collection_method: How invoices are collected (charge_automatically or send_invoice).
        - created: Timestamp indicating when the subscription was created.
        - currency: Three-letter ISO currency code in lowercase indicating the currency for the subscription.
        - current_period_end: Timestamp marking the end of the current billing period.
        - current_period_start: Timestamp marking the start of the current billing period.
        - customer: ID of the customer who owns the subscription, expandable to full customer object.
        - days_until_due: Number of days until the invoice is due for subscriptions using send_invoice collection method.
        - default_payment_method: ID of the default payment method for the subscription, taking precedence over default_source.
        - default_source: ID of the default payment source for the subscription.
        - default_tax_rates: Tax rates that apply to the subscription by default.
        - description: Human-readable description of the subscription, displayable to the customer.
        - discount: Describes any discount currently applied to the subscription.
        - ended_at: Timestamp indicating when the subscription ended, if applicable.
        - id: Unique identifier for the subscription object.
        - invoice_settings: Settings for invoices generated by this subscription, such as custom fields and footer.
        - is_deleted: Indicates whether the subscription has been deleted.
        - items: List of subscription items, each with an attached price defining what the customer is subscribed to.
        - latest_invoice: The most recent invoice this subscription has generated, expandable to full invoice object.
        - livemode: Indicates whether the subscription exists in live mode (true) or test mode (false).
        - metadata: Set of key-value pairs that you can attach to the subscription for storing additional structured information.
        - next_pending_invoice_item_invoice: Timestamp when the next invoice for pending invoice items will be created.
        - object_: String representing the object type, always 'subscription'.
        - on_behalf_of: For Connect platforms, the account for which the subscription is being created or managed.
        - pause_collection: Configuration for pausing collection on the subscription while retaining the subscription structure.
        - payment_settings: Payment settings for invoices generated by this subscription.
        - pending_invoice_item_interval: Specifies an interval for aggregating usage records into pending invoice items.
        - pending_setup_intent: SetupIntent used for collecting user authentication when updating payment methods without immediate payment.
        - pending_update: If specified, pending updates that will be applied to the subscription once the latest_invoice has been paid.
        - plan: The plan associated with the subscription (deprecated, use items instead).
        - quantity: Quantity of the plan subscribed to (deprecated, use items instead).
        - schedule: ID of the subscription schedule managing this subscription's lifecycle, if applicable.
        - start_date: Timestamp indicating when the subscription started.
        - status: Current status of the subscription (incomplete, incomplete_expired, trialing, active, past_due, canceled, unpaid, or paused).
        - tax_percent: The percentage of tax applied to the subscription (deprecated, use default_tax_rates instead).
        - test_clock: ID of the test clock associated with this subscription for simulating time-based scenarios.
        - transfer_data: For Connect platforms, the account receiving funds from the subscription and optional percentage transferred.
        - trial_end: Timestamp indicating when the trial period ends, if applicable.
        - trial_settings: Settings related to trial periods, including conditions for ending trials.
        - trial_start: Timestamp indicating when the trial period began, if applicable.
        - updated: Timestamp indicating when the subscription was last updated.
        
        Args:
            query: Filter and sort conditions. Supports operators like eq, neq, gt, gte, lt, lte,
                   in, like, fuzzy, keyword, not, and, or. Example: \{"filter": \{"eq": \{"status": "active"\}\}\}
            limit: Maximum results to return (default 1000)
            cursor: Pagination cursor from previous response's meta.cursor
            fields: Field paths to include in results. Each path is a list of keys for nested access.
                    Example: [["id"], ["user", "name"]] returns id and user.name fields.
        
        Returns:
            SubscriptionsSearchResult with typed records, pagination metadata, and optional search metadata
        
        Raises:
            NotImplementedError: If called in local execution mode

    `get(self, id: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.Subscription`
    :   Retrieves the subscription with the given ID
        
        Args:
            id: The subscription ID
            **kwargs: Additional parameters
        
        Returns:
            Subscription

    `list(self, automatic_tax: SubscriptionsListParamsAutomaticTax | None = None, collection_method: str | None = None, created: SubscriptionsListParamsCreated | None = None, current_period_end: SubscriptionsListParamsCurrentPeriodEnd | None = None, current_period_start: SubscriptionsListParamsCurrentPeriodStart | None = None, customer: str | None = None, customer_account: str | None = None, ending_before: str | None = None, limit: int | None = None, price: str | None = None, starting_after: str | None = None, status: str | None = None, **kwargs) ‑> airbyte_agent_sdk.connectors.stripe.models.StripeExecuteResultWithMeta[list[Subscription], SubscriptionsListResultMeta]`
    :   By default, returns a list of subscriptions that have not been canceled
        
        Args:
            automatic_tax: Filter subscriptions by their automatic tax settings.
            collection_method: The collection method of the subscriptions to retrieve
            created: Only return customers that were created during the given date interval.
            current_period_end: Only return subscriptions whose minimum item current_period_end falls within the given date interval.
            current_period_start: Only return subscriptions whose maximum item current_period_start falls within the given date interval.
            customer: Only return subscriptions for the customer specified by this customer ID
            customer_account: The ID of the account whose subscriptions will be retrieved.
            ending_before: A cursor for use in pagination. ending_before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj_bar, your subsequent call can include ending_before=obj_bar in order to fetch the previous page of the list.
            limit: A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 10.
            price: Filter for subscriptions that contain this recurring price ID.
            starting_after: A cursor for use in pagination. starting_after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include starting_after=obj_foo in order to fetch the next page of the list.
            status: The status of the subscriptions to retrieve. Passing in a value of canceled will return all canceled subscriptions, including those belonging to deleted customers. Pass ended to find subscriptions that are canceled and subscriptions that are expired due to incomplete payment. Passing in a value of all will return subscriptions of all statuses. If no value is supplied, all subscriptions that have not been canceled are returned.
            **kwargs: Additional parameters
        
        Returns:
            SubscriptionsListResult