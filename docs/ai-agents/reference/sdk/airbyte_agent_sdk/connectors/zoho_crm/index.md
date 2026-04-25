---
id: airbyte_agent_sdk-connectors-zoho_crm-index
title: airbyte_agent_sdk.connectors.zoho_crm.index
---

Module airbyte_agent_sdk.connectors.zoho_crm
============================================
Zoho-Crm connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.zoho_crm.connector
* airbyte_agent_sdk.connectors.zoho_crm.connector_model
* airbyte_agent_sdk.connectors.zoho_crm.models
* airbyte_agent_sdk.connectors.zoho_crm.types

Classes
-------

<a id="AccountsSearchData"></a>

`AccountsSearchData(**data: Any)`
:   Search result data for accounts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_name: str | None`
    :   Name of the account or company

    `account_number: str | None`
    :   Account number

    `account_type: str | None`
    :   Type of account (e.g., Analyst, Competitor, Customer)

    `annual_revenue: float | None`
    :   Annual revenue of the account

    `billing_city: str | None`
    :   Billing address city

    `billing_country: str | None`
    :   Billing address country

    `billing_state: str | None`
    :   Billing address state or province

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description or notes about the account

    `employees: int | None`
    :   Number of employees

    `id: str`
    :   Unique record identifier

    `industry: str | None`
    :   Industry the account belongs to

    `model_config`
    :   The type of the None singleton.

    `modified_time: str | None`
    :   Time the record was last modified

    `ownership: str | None`
    :   Ownership type (e.g., Public, Private)

    `phone: str | None`
    :   Account phone number

    `rating: str | None`
    :   Account rating

    `website: str | None`
    :   Account website URL

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

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[AccountsSearchData]
    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[CallsSearchData]
    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[CampaignsSearchData]
    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[ContactsSearchData]
    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[DealsSearchData]
    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[EventsSearchData]
    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[InvoicesSearchData]
    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[LeadsSearchData]
    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[ProductsSearchData]
    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[QuotesSearchData]
    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult[TasksSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="AccountsSearchResult"></a>

`AccountsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CallsSearchResult"></a>

`CallsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CampaignsSearchResult"></a>

`CampaignsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ContactsSearchResult"></a>

`ContactsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="DealsSearchResult"></a>

`DealsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="EventsSearchResult"></a>

`EventsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="LeadsSearchResult"></a>

`LeadsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ProductsSearchResult"></a>

`ProductsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="QuotesSearchResult"></a>

`QuotesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TasksSearchResult"></a>

`TasksSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CallsSearchData"></a>

`CallsSearchData(**data: Any)`
:   Search result data for calls entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `call_duration: str | None`
    :   Duration of the call as a formatted string

    `call_duration_in_seconds: float | None`
    :   Duration of the call in seconds

    `call_purpose: str | None`
    :   Purpose of the call

    `call_result: str | None`
    :   Result or outcome of the call

    `call_start_time: str | None`
    :   Start time of the call

    `call_type: str | None`
    :   Type of call (Inbound or Outbound)

    `caller_id: str | None`
    :   Caller ID number

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description or notes about the call

    `id: str`
    :   Unique record identifier

    `model_config`
    :   The type of the None singleton.

    `modified_time: str | None`
    :   Time the record was last modified

    `outgoing_call_status: str | None`
    :   Status of outgoing calls

    `subject: str | None`
    :   Subject of the call

<a id="CampaignsSearchData"></a>

`CampaignsSearchData(**data: Any)`
:   Search result data for campaigns entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actual_cost: float | None`
    :   Actual cost incurred

    `budgeted_cost: float | None`
    :   Budget allocated for the campaign

    `campaign_name: str | None`
    :   Name of the campaign

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description or notes about the campaign

    `end_date: str | None`
    :   Campaign end date

    `expected_response: int | None`
    :   Expected response count

    `expected_revenue: float | None`
    :   Expected revenue from the campaign

    `id: str`
    :   Unique record identifier

    `model_config`
    :   The type of the None singleton.

    `modified_time: str | None`
    :   Time the record was last modified

    `num_sent: str | None`
    :   Number of campaign messages sent

    `start_date: str | None`
    :   Campaign start date

    `status: str | None`
    :   Current status of the campaign

    `type_: str | None`
    :   Type of campaign (e.g., Email, Webinar, Conference)

<a id="ContactsSearchData"></a>

`ContactsSearchData(**data: Any)`
:   Search result data for contacts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_time: str | None`
    :   Time the record was created

    `date_of_birth: str | None`
    :   Contact's date of birth

    `department: str | None`
    :   Department the contact belongs to

    `description: str | None`
    :   Description or notes about the contact

    `email: str | None`
    :   Contact's email address

    `first_name: str | None`
    :   Contact's first name

    `full_name: str | None`
    :   Contact's full name

    `id: str`
    :   Unique record identifier

    `last_name: str | None`
    :   Contact's last name

    `lead_source: str | None`
    :   Source from which the contact was generated

    `mailing_city: str | None`
    :   Mailing address city

    `mailing_country: str | None`
    :   Mailing address country

    `mailing_state: str | None`
    :   Mailing address state or province

    `mobile: str | None`
    :   Contact's mobile number

    `model_config`
    :   The type of the None singleton.

    `modified_time: str | None`
    :   Time the record was last modified

    `phone: str | None`
    :   Contact's phone number

    `title: str | None`
    :   Contact's job title

<a id="DealsSearchData"></a>

`DealsSearchData(**data: Any)`
:   Search result data for deals entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: float | None`
    :   Monetary value of the deal

    `closing_date: str | None`
    :   Expected closing date

    `created_time: str | None`
    :   Time the record was created

    `deal_name: str | None`
    :   Name of the deal

    `description: str | None`
    :   Description or notes about the deal

    `id: str`
    :   Unique record identifier

    `lead_source: str | None`
    :   Source from which the deal originated

    `model_config`
    :   The type of the None singleton.

    `modified_time: str | None`
    :   Time the record was last modified

    `next_step: str | None`
    :   Next step in the deal process

    `probability: int | None`
    :   Probability of closing the deal (percentage)

    `stage: str | None`
    :   Current stage of the deal in the pipeline

    `type_: str | None`
    :   Type of deal (e.g., New Business, Existing Business)

<a id="EventsSearchData"></a>

`EventsSearchData(**data: Any)`
:   Search result data for events entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `all_day: bool | None`
    :   Whether this is an all-day event

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description or notes about the event

    `end_date_time: str | None`
    :   Event end date and time

    `event_title: str | None`
    :   Title of the event

    `id: str`
    :   Unique record identifier

    `location: str | None`
    :   Event location

    `model_config`
    :   The type of the None singleton.

    `modified_time: str | None`
    :   Time the record was last modified

    `start_date_time: str | None`
    :   Event start date and time

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

    `adjustment: float | None`
    :   Adjustment amount

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description or notes about the invoice

    `discount: float | None`
    :   Discount amount

    `due_date: str | None`
    :   Payment due date

    `excise_duty: float | None`
    :   Excise duty amount

    `grand_total: float | None`
    :   Total amount including tax and adjustments

    `id: str`
    :   Unique record identifier

    `invoice_date: str | None`
    :   Date the invoice was issued

    `invoice_number: str | None`
    :   Invoice number

    `model_config`
    :   The type of the None singleton.

    `modified_time: str | None`
    :   Time the record was last modified

    `purchase_order: str | None`
    :   Associated purchase order number

    `status: str | None`
    :   Current status of the invoice

    `sub_total: float | None`
    :   Subtotal before tax and adjustments

    `subject: str | None`
    :   Subject or title of the invoice

    `tax: float | None`
    :   Tax amount

    `terms_and_conditions: str | None`
    :   Terms and conditions text

<a id="LeadsSearchData"></a>

`LeadsSearchData(**data: Any)`
:   Search result data for leads entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annual_revenue: float | None`
    :   Annual revenue of the lead's company

    `city: str | None`
    :   Lead's city

    `company: str | None`
    :   Company the lead is associated with

    `country: str | None`
    :   Lead's country

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description or notes about the lead

    `email: str | None`
    :   Lead's email address

    `first_name: str | None`
    :   Lead's first name

    `full_name: str | None`
    :   Lead's full name

    `id: str`
    :   Unique record identifier

    `industry: str | None`
    :   Industry the lead belongs to

    `last_name: str | None`
    :   Lead's last name

    `lead_source: str | None`
    :   Source from which the lead was generated

    `lead_status: str | None`
    :   Current status of the lead

    `mobile: str | None`
    :   Lead's mobile number

    `model_config`
    :   The type of the None singleton.

    `modified_time: str | None`
    :   Time the record was last modified

    `no_of_employees: int | None`
    :   Number of employees in the lead's company

    `phone: str | None`
    :   Lead's phone number

    `rating: str | None`
    :   Lead rating

    `state: str | None`
    :   Lead's state or province

    `title: str | None`
    :   Lead's job title

    `website: str | None`
    :   Lead's website URL

<a id="ProductsSearchData"></a>

`ProductsSearchData(**data: Any)`
:   Search result data for products entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `commission_rate: float | None`
    :   Commission rate for the product

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description of the product

    `id: str`
    :   Unique record identifier

    `manufacturer: str | None`
    :   Product manufacturer

    `model_config`
    :   The type of the None singleton.

    `modified_time: str | None`
    :   Time the record was last modified

    `product_active: bool | None`
    :   Whether the product is active

    `product_category: str | None`
    :   Category of the product

    `product_code: str | None`
    :   Product code or SKU

    `product_name: str | None`
    :   Name of the product

    `qty_in_demand: float | None`
    :   Quantity in demand

    `qty_in_stock: float | None`
    :   Quantity currently in stock

    `qty_ordered: float | None`
    :   Quantity on order

    `sales_end_date: str | None`
    :   Date when sales end

    `sales_start_date: str | None`
    :   Date when sales begin

    `unit_price: float | None`
    :   Unit price of the product

<a id="QuotesSearchData"></a>

`QuotesSearchData(**data: Any)`
:   Search result data for quotes entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `adjustment: float | None`
    :   Adjustment amount

    `carrier: str | None`
    :   Shipping carrier

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description or notes about the quote

    `discount: float | None`
    :   Discount amount

    `grand_total: float | None`
    :   Total amount including tax and adjustments

    `id: str`
    :   Unique record identifier

    `model_config`
    :   The type of the None singleton.

    `modified_time: str | None`
    :   Time the record was last modified

    `quote_stage: str | None`
    :   Current stage of the quote

    `sub_total: float | None`
    :   Subtotal before tax and adjustments

    `subject: str | None`
    :   Subject or title of the quote

    `tax: float | None`
    :   Tax amount

    `terms_and_conditions: str | None`
    :   Terms and conditions text

    `valid_till: str | None`
    :   Date until which the quote is valid

<a id="TasksSearchData"></a>

`TasksSearchData(**data: Any)`
:   Search result data for tasks entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `closed_time: str | None`
    :   Time the task was closed

    `created_time: str | None`
    :   Time the record was created

    `description: str | None`
    :   Description or notes about the task

    `due_date: str | None`
    :   Due date for the task

    `id: str`
    :   Unique record identifier

    `model_config`
    :   The type of the None singleton.

    `modified_time: str | None`
    :   Time the record was last modified

    `priority: str | None`
    :   Priority level (e.g., High, Highest, Low, Lowest, Normal)

    `send_notification_email: bool | None`
    :   Whether to send a notification email

    `status: str | None`
    :   Current status (e.g., Not Started, In Progress, Completed)

    `subject: str | None`
    :   Subject or title of the task

<a id="ZohoCrmAuthConfig"></a>

`ZohoCrmAuthConfig(**data: Any)`
:   Zoho CRM OAuth 2.0
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str`
    :   OAuth 2.0 Client ID from Zoho Developer Console

    `client_secret: str`
    :   OAuth 2.0 Client Secret from Zoho Developer Console

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   OAuth 2.0 Refresh Token (does not expire)

<a id="ZohoCrmConnector"></a>

`ZohoCrmConnector(auth_config: ZohoCrmAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, dc_region: str | None = None)`
:   Type-safe Zoho-Crm API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new zoho-crm connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., ZohoCrmAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            dc_region: The Zoho data center region domain suffix: - com (US) - com.au (AU) - eu (EU) - in (IN) - com.cn (CN) - jp (JP)
    
    Examples:
        # Local mode (direct API calls)
        connector = ZohoCrmConnector(auth_config=ZohoCrmAuthConfig(client_id="...", client_secret="...", refresh_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = ZohoCrmConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = ZohoCrmConnector(
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

    `create(*, airbyte_config: AirbyteAuthConfig, auth_config: "'ZohoCrmAuthConfig' | None" = None, server_side_oauth_secret_id: str | None = None, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None)`
    :   Create a new hosted connector on Airbyte Cloud.
        
        This factory method:
        1. Creates a source on Airbyte Cloud with the provided credentials
        2. Returns a connector configured with the new connector_id
        
        Supports two authentication modes:
        1. Direct credentials: Provide `auth_config` with typed credentials
        2. Server-side OAuth: Provide `server_side_oauth_secret_id` from OAuth flow
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            auth_config: Typed auth config. Required unless using server_side_oauth_secret_id.
            server_side_oauth_secret_id: OAuth secret ID from get_consent_url redirect.
                When provided, auth_config is not required.
            name: Optional source name (defaults to connector name + workspace_name)
            replication_config: Optional replication settings dict.
                Required for connectors with x-airbyte-replication-config (REPLICATION mode sources).
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            A ZohoCrmConnector instance configured in hosted mode
        
        Raises:
            ValueError: If neither or both auth_config and server_side_oauth_secret_id provided
        
        Example:
            # Create a new hosted connector with API key auth
            connector = await ZohoCrmConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                auth_config=ZohoCrmAuthConfig(client_id="...", client_secret="...", refresh_token="..."),
            )
        
            # With server-side OAuth:
            connector = await ZohoCrmConnector.create(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                server_side_oauth_secret_id="airbyte_oauth_..._secret_...",
            )
        
            # Use the connector
            result = await connector.execute("entity", "list", \{\})

    `get_consent_url(*, airbyte_config: AirbyteAuthConfig, redirect_url: str, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> str`
    :   Initiate server-side OAuth flow with auto-source creation.
        
        Returns a consent URL where the end user should be redirected to grant access.
        After completing consent, the source is automatically created and the user is
        redirected to your redirect_url with a `connector_id` query parameter.
        
        Args:
            airbyte_config: Airbyte hosted auth config with client credentials and workspace_name.
                Optionally include organization_id for multi-org request routing.
            redirect_url: URL where users will be redirected after OAuth consent.
                After consent, user arrives at: redirect_url?connector_id=...
            name: Optional name for the source. Defaults to connector name + workspace_name.
            replication_config: Optional replication settings dict. Merged with OAuth credentials.
            source_template_id: Source template ID. Required when organization has
                multiple source templates for this connector type.
        
        Returns:
            The OAuth consent URL
        
        Example:
            consent_url = await ZohoCrmConnector.get_consent_url(
                airbyte_config=AirbyteAuthConfig(
                    workspace_name="my-workspace",
                    organization_id="00000000-0000-0000-0000-000000000123",
                    airbyte_client_id="client_abc",
                    airbyte_client_secret="secret_xyz",
                ),
                redirect_url="https://myapp.com/oauth/callback",
                name="My Zoho-Crm Source",
            )
            # Redirect user to: consent_url
            # After consent, user arrives at: https://myapp.com/oauth/callback?connector_id=...

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Usage:
            @mcp.tool()
            @ZohoCrmConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @ZohoCrmConnector.tool_utils(update_docstring=False, max_output_chars=None)
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
            connector = await ZohoCrmConnector.create(...)
            print(f"Created connector: \{connector.connector_id\}")

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            ZohoCrmCheckResult with status ("healthy" or "unhealthy") and optional error message
        
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

    `execute(self, entity: str, action: "Literal['list', 'get', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
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