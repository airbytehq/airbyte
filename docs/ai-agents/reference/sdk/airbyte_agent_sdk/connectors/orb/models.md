---
id: airbyte_agent_sdk-connectors-orb-models
title: airbyte_agent_sdk.connectors.orb.models
---

Module airbyte_agent_sdk.connectors.orb.models
==============================================
Pydantic models for orb connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="Address"></a>

`Address(**data: Any)`
:   Address object
    
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

    * airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult[CustomersSearchData]
    * airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult[InvoicesSearchData]
    * airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult[PlansSearchData]
    * airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult[SubscriptionsSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.orb.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[CustomersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[InvoicesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[PlansSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PlansSearchResult"></a>

`PlansSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SubscriptionsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.orb.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Customer"></a>

`Customer(**data: Any)`
:   Customer object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auto_collection: bool | Any | None`
    :   The type of the None singleton.

    `balance: str | Any | None`
    :   The type of the None singleton.

    `billing_address: Any`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `external_customer_id: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `metadata: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `payment_provider: str | Any | None`
    :   The type of the None singleton.

    `payment_provider_id: str | Any | None`
    :   The type of the None singleton.

    `shipping_address: Any`
    :   The type of the None singleton.

    `tax_id: airbyte_agent_sdk.connectors.orb.models.CustomerTaxId | Any | None`
    :   The type of the None singleton.

    `timezone: str | Any | None`
    :   The type of the None singleton.

<a id="CustomerTaxId"></a>

`CustomerTaxId(**data: Any)`
:   Tax identification information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `country: str | Any | None`
    :   The country of the tax ID

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of tax ID

    `value: str | Any | None`
    :   The value of the tax ID

<a id="CustomersList"></a>

`CustomersList(**data: Any)`
:   Paginated list of customers
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.orb.models.Customer] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination_metadata: airbyte_agent_sdk.connectors.orb.models.PaginationMetadata | Any`
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

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
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

    `model_config`
    :   The type of the None singleton.

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

<a id="Invoice"></a>

`Invoice(**data: Any)`
:   Invoice object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount_due: str | Any | None`
    :   The type of the None singleton.

    `auto_collection: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `billing_address: Any`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `credit_notes: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `customer: airbyte_agent_sdk.connectors.orb.models.InvoiceCustomer | Any | None`
    :   The type of the None singleton.

    `customer_balance_transactions: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `discount: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `due_date: str | Any | None`
    :   The type of the None singleton.

    `eligible_to_issue_at: str | Any | None`
    :   The type of the None singleton.

    `hosted_invoice_url: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `invoice_date: str | Any | None`
    :   The type of the None singleton.

    `invoice_number: str | Any | None`
    :   The type of the None singleton.

    `invoice_pdf: str | Any | None`
    :   The type of the None singleton.

    `issue_failed_at: str | Any | None`
    :   The type of the None singleton.

    `issued_at: str | Any | None`
    :   The type of the None singleton.

    `line_items: list[airbyte_agent_sdk.connectors.orb.models.InvoiceLineItemsItem] | Any | None`
    :   The type of the None singleton.

    `maximum: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `memo: str | Any | None`
    :   The type of the None singleton.

    `metadata: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `minimum: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `paid_at: str | Any | None`
    :   The type of the None singleton.

    `payment_failed_at: str | Any | None`
    :   The type of the None singleton.

    `payment_started_at: str | Any | None`
    :   The type of the None singleton.

    `shipping_address: Any`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `subscription: airbyte_agent_sdk.connectors.orb.models.InvoiceSubscription | Any | None`
    :   The type of the None singleton.

    `subtotal: str | Any | None`
    :   The type of the None singleton.

    `sync_failed_at: str | Any | None`
    :   The type of the None singleton.

    `total: str | Any | None`
    :   The type of the None singleton.

    `voided_at: str | Any | None`
    :   The type of the None singleton.

    `will_auto_issue: bool | Any | None`
    :   The type of the None singleton.

<a id="InvoiceCustomer"></a>

`InvoiceCustomer(**data: Any)`
:   The customer associated with the invoice
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `external_customer_id: str | Any | None`
    :   The external customer ID

    `id: str | Any | None`
    :   The customer ID

    `model_config`
    :   The type of the None singleton.

<a id="InvoiceLineItemsItem"></a>

`InvoiceLineItemsItem(**data: Any)`
:   Nested schema for Invoice.line_items_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any | None`
    :   The amount of the line item

    `end_date: str | Any | None`
    :   The end date of the line item

    `id: str | Any | None`
    :   The unique identifier of the line item

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The name of the line item

    `quantity: float | Any | None`
    :   The quantity of the line item

    `start_date: str | Any | None`
    :   The start date of the line item

<a id="InvoiceSubscription"></a>

`InvoiceSubscription(**data: Any)`
:   The subscription associated with the invoice
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The subscription ID

    `model_config`
    :   The type of the None singleton.

<a id="InvoicesList"></a>

`InvoicesList(**data: Any)`
:   Paginated list of invoices
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.orb.models.Invoice] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination_metadata: airbyte_agent_sdk.connectors.orb.models.PaginationMetadata | Any`
    :   The type of the None singleton.

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

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
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

    `model_config`
    :   The type of the None singleton.

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

<a id="OrbAuthConfig"></a>

`OrbAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your Orb API key

    `model_config`
    :   The type of the None singleton.

<a id="OrbCheckResult"></a>

`OrbCheckResult(**data: Any)`
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

<a id="OrbExecuteResult"></a>

`OrbExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="OrbExecuteResultWithMeta"></a>

`OrbExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta[list[Customer], CustomersListResultMeta]
    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta[list[Invoice], InvoicesListResultMeta]
    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta[list[Plan], PlansListResultMeta]
    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta[list[Subscription], SubscriptionsListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`OrbExecuteResultWithMeta[list[Customer], CustomersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResult
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

    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OrbExecuteResultWithMeta[list[Invoice], InvoicesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResult
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

    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OrbExecuteResultWithMeta[list[Plan], PlansListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PlansListResult"></a>

`PlansListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`OrbExecuteResultWithMeta[list[Subscription], SubscriptionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResult
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

    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.orb.models.OrbExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="OrbReplicationConfig"></a>

`OrbReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Orb.
    
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
    :   UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data.

<a id="PaginationMetadata"></a>

`PaginationMetadata(**data: Any)`
:   Pagination metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_more: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
    :   The type of the None singleton.

<a id="Plan"></a>

`Plan(**data: Any)`
:   Plan object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `default_invoice_memo: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `discount: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `external_plan_id: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `invoicing_currency: str | Any | None`
    :   The type of the None singleton.

    `maximum: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `metadata: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `minimum: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `net_terms: int | Any | None`
    :   The type of the None singleton.

    `plan_phases: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `prices: list[airbyte_agent_sdk.connectors.orb.models.PlanPricesItem] | Any | None`
    :   The type of the None singleton.

    `product: airbyte_agent_sdk.connectors.orb.models.PlanProduct | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `trial_config: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="PlanPricesItem"></a>

`PlanPricesItem(**data: Any)`
:   Nested schema for Plan.prices_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currency: str | Any | None`
    :   The currency of the price

    `id: str | Any | None`
    :   The unique identifier of the price

    `model_config`
    :   The type of the None singleton.

    `model_type: str | Any | None`
    :   The model type of the price

    `name: str | Any | None`
    :   The name of the price

    `price_type: str | Any | None`
    :   The type of price

<a id="PlanProduct"></a>

`PlanProduct(**data: Any)`
:   The product associated with the plan
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The product ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The product name

<a id="PlansList"></a>

`PlansList(**data: Any)`
:   Paginated list of plans
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.orb.models.Plan] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination_metadata: airbyte_agent_sdk.connectors.orb.models.PaginationMetadata | Any`
    :   The type of the None singleton.

<a id="PlansListResultMeta"></a>

`PlansListResultMeta(**data: Any)`
:   Metadata for plans.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
    :   The type of the None singleton.

<a id="PlansSearchData"></a>

`PlansSearchData(**data: Any)`
:   Search result data for plans entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The date and time when the plan was created

    `description: str | None`
    :   A description of the plan

    `id: str`
    :   The unique identifier of the plan

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the plan

    `prices: list[typing.Any] | None`
    :   The pricing options for the plan

    `product: dict[str, typing.Any] | None`
    :   The product associated with the plan

<a id="Subscription"></a>

`Subscription(**data: Any)`
:   Subscription object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active_plan_phase_order: int | Any | None`
    :   The type of the None singleton.

    `auto_collection: bool | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `current_billing_period_end_date: str | Any | None`
    :   The type of the None singleton.

    `current_billing_period_start_date: str | Any | None`
    :   The type of the None singleton.

    `customer: airbyte_agent_sdk.connectors.orb.models.SubscriptionCustomer | Any | None`
    :   The type of the None singleton.

    `default_invoice_memo: str | Any | None`
    :   The type of the None singleton.

    `end_date: str | Any | None`
    :   The type of the None singleton.

    `fixed_fee_quantity_schedule: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `invoicing_threshold: str | Any | None`
    :   The type of the None singleton.

    `metadata: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `net_terms: int | Any | None`
    :   The type of the None singleton.

    `plan: airbyte_agent_sdk.connectors.orb.models.SubscriptionPlan | Any | None`
    :   The type of the None singleton.

    `price_intervals: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `redeemed_coupon: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `start_date: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

<a id="SubscriptionCustomer"></a>

`SubscriptionCustomer(**data: Any)`
:   The customer associated with the subscription
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `external_customer_id: str | Any | None`
    :   The external customer ID

    `id: str | Any | None`
    :   The customer ID

    `model_config`
    :   The type of the None singleton.

<a id="SubscriptionPlan"></a>

`SubscriptionPlan(**data: Any)`
:   The plan associated with the subscription
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The plan ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The plan name

<a id="SubscriptionsList"></a>

`SubscriptionsList(**data: Any)`
:   Paginated list of subscriptions
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.orb.models.Subscription] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination_metadata: airbyte_agent_sdk.connectors.orb.models.PaginationMetadata | Any`
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

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
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

    `created_at: str | None`
    :   The date and time when the subscription was created

    `end_date: str | None`
    :   The date and time when the subscription ends

    `id: str`
    :   The unique identifier of the subscription

    `model_config`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The date and time when the subscription starts

    `status: str | None`
    :   The current status of the subscription