---
id: airbyte_agent_sdk-connectors-zoho_crm-models
title: airbyte_agent_sdk.connectors.zoho_crm.models
---

Module airbyte_agent_sdk.connectors.zoho_crm.models
===================================================
Pydantic models for zoho-crm connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="Account"></a>

`Account(**data: Any)`
:   Zoho CRM account (company) object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_name: str | Any | None`
    :   The type of the None singleton.

    `account_number: str | Any | None`
    :   The type of the None singleton.

    `account_type: str | Any | None`
    :   The type of the None singleton.

    `annual_revenue: float | Any | None`
    :   The type of the None singleton.

    `billing_city: str | Any | None`
    :   The type of the None singleton.

    `billing_code: str | Any | None`
    :   The type of the None singleton.

    `billing_country: str | Any | None`
    :   The type of the None singleton.

    `billing_state: str | Any | None`
    :   The type of the None singleton.

    `billing_street: str | Any | None`
    :   The type of the None singleton.

    `created_by: Any`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `employees: int | Any | None`
    :   The type of the None singleton.

    `fax: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `industry: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_by: Any`
    :   The type of the None singleton.

    `modified_time: str | Any | None`
    :   The type of the None singleton.

    `owner: Any`
    :   The type of the None singleton.

    `ownership: str | Any | None`
    :   The type of the None singleton.

    `parent_account: Any`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `rating: str | Any | None`
    :   The type of the None singleton.

    `record_status_s: str | Any | None`
    :   The type of the None singleton.

    `shipping_city: str | Any | None`
    :   The type of the None singleton.

    `shipping_code: str | Any | None`
    :   The type of the None singleton.

    `shipping_country: str | Any | None`
    :   The type of the None singleton.

    `shipping_state: str | Any | None`
    :   The type of the None singleton.

    `shipping_street: str | Any | None`
    :   The type of the None singleton.

    `sic_code: int | Any | None`
    :   The type of the None singleton.

    `ticker_symbol: str | Any | None`
    :   The type of the None singleton.

    `website: str | Any | None`
    :   The type of the None singleton.

<a id="AccountsList"></a>

`AccountsList(**data: Any)`
:   Paginated list of accounts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.zoho_crm.models.Account] | Any`
    :   The type of the None singleton.

    `info: airbyte_agent_sdk.connectors.zoho_crm.models.PaginationInfo | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AccountsListResultMeta"></a>

`AccountsListResultMeta(**data: Any)`
:   Metadata for accounts.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `more_records: bool | Any`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

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

`AirbyteSearchResult[AccountsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

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

`AirbyteSearchResult[CallsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[CampaignsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[ContactsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[DealsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[EventsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[InvoicesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[LeadsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[ProductsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[QuotesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

`AirbyteSearchResult[TasksSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

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

<a id="Call"></a>

`Call(**data: Any)`
:   Zoho CRM call object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `call_duration: str | Any | None`
    :   The type of the None singleton.

    `call_duration_in_seconds: float | Any | None`
    :   The type of the None singleton.

    `call_purpose: str | Any | None`
    :   The type of the None singleton.

    `call_result: str | Any | None`
    :   The type of the None singleton.

    `call_start_time: str | Any | None`
    :   The type of the None singleton.

    `call_type: str | Any | None`
    :   The type of the None singleton.

    `caller_id: str | Any | None`
    :   The type of the None singleton.

    `created_by: Any`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_by: Any`
    :   The type of the None singleton.

    `modified_time: str | Any | None`
    :   The type of the None singleton.

    `outgoing_call_status: str | Any | None`
    :   The type of the None singleton.

    `owner: Any`
    :   The type of the None singleton.

    `record_status_s: str | Any | None`
    :   The type of the None singleton.

    `subject: str | Any | None`
    :   The type of the None singleton.

    `what_id: Any`
    :   The type of the None singleton.

    `who_id: Any`
    :   The type of the None singleton.

<a id="CallsList"></a>

`CallsList(**data: Any)`
:   Paginated list of calls
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.zoho_crm.models.Call] | Any`
    :   The type of the None singleton.

    `info: airbyte_agent_sdk.connectors.zoho_crm.models.PaginationInfo | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CallsListResultMeta"></a>

`CallsListResultMeta(**data: Any)`
:   Metadata for calls.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `more_records: bool | Any`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

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

<a id="Campaign"></a>

`Campaign(**data: Any)`
:   Zoho CRM campaign object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actual_cost: float | Any | None`
    :   The type of the None singleton.

    `budgeted_cost: float | Any | None`
    :   The type of the None singleton.

    `campaign_name: str | Any | None`
    :   The type of the None singleton.

    `created_by: Any`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `end_date: str | Any | None`
    :   The type of the None singleton.

    `expected_response: int | Any | None`
    :   The type of the None singleton.

    `expected_revenue: float | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_by: Any`
    :   The type of the None singleton.

    `modified_time: str | Any | None`
    :   The type of the None singleton.

    `num_sent: str | Any | None`
    :   The type of the None singleton.

    `owner: Any`
    :   The type of the None singleton.

    `record_status_s: str | Any | None`
    :   The type of the None singleton.

    `start_date: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="CampaignsList"></a>

`CampaignsList(**data: Any)`
:   Paginated list of campaigns
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.zoho_crm.models.Campaign] | Any`
    :   The type of the None singleton.

    `info: airbyte_agent_sdk.connectors.zoho_crm.models.PaginationInfo | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CampaignsListResultMeta"></a>

`CampaignsListResultMeta(**data: Any)`
:   Metadata for campaigns.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `more_records: bool | Any`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

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

<a id="Contact"></a>

`Contact(**data: Any)`
:   Zoho CRM contact object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_name: Any`
    :   The type of the None singleton.

    `created_by: Any`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `date_of_birth: str | Any | None`
    :   The type of the None singleton.

    `department: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `fax: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `full_name: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `lead_source: str | Any | None`
    :   The type of the None singleton.

    `mailing_city: str | Any | None`
    :   The type of the None singleton.

    `mailing_country: str | Any | None`
    :   The type of the None singleton.

    `mailing_state: str | Any | None`
    :   The type of the None singleton.

    `mailing_street: str | Any | None`
    :   The type of the None singleton.

    `mailing_zip: str | Any | None`
    :   The type of the None singleton.

    `mobile: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_by: Any`
    :   The type of the None singleton.

    `modified_time: str | Any | None`
    :   The type of the None singleton.

    `other_city: str | Any | None`
    :   The type of the None singleton.

    `other_country: str | Any | None`
    :   The type of the None singleton.

    `other_state: str | Any | None`
    :   The type of the None singleton.

    `other_street: str | Any | None`
    :   The type of the None singleton.

    `other_zip: str | Any | None`
    :   The type of the None singleton.

    `owner: Any`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `record_status_s: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

<a id="ContactsList"></a>

`ContactsList(**data: Any)`
:   Paginated list of contacts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.zoho_crm.models.Contact] | Any`
    :   The type of the None singleton.

    `info: airbyte_agent_sdk.connectors.zoho_crm.models.PaginationInfo | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ContactsListResultMeta"></a>

`ContactsListResultMeta(**data: Any)`
:   Metadata for contacts.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `more_records: bool | Any`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

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

<a id="CreatedBy"></a>

`CreatedBy(**data: Any)`
:   User who created the record
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

<a id="Deal"></a>

`Deal(**data: Any)`
:   Zoho CRM deal (opportunity) object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_name: Any`
    :   The type of the None singleton.

    `amount: float | Any | None`
    :   The type of the None singleton.

    `campaign_source: Any`
    :   The type of the None singleton.

    `closing_date: str | Any | None`
    :   The type of the None singleton.

    `contact_name: Any`
    :   The type of the None singleton.

    `created_by: Any`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `deal_name: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `lead_source: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_by: Any`
    :   The type of the None singleton.

    `modified_time: str | Any | None`
    :   The type of the None singleton.

    `next_step: str | Any | None`
    :   The type of the None singleton.

    `owner: Any`
    :   The type of the None singleton.

    `pipeline: airbyte_agent_sdk.connectors.zoho_crm.models.DealPipeline | Any | None`
    :   The type of the None singleton.

    `probability: int | Any | None`
    :   The type of the None singleton.

    `record_status_s: str | Any | None`
    :   The type of the None singleton.

    `stage: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="DealPipeline"></a>

`DealPipeline(**data: Any)`
:   Sales pipeline reference
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

<a id="DealsList"></a>

`DealsList(**data: Any)`
:   Paginated list of deals
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.zoho_crm.models.Deal] | Any`
    :   The type of the None singleton.

    `info: airbyte_agent_sdk.connectors.zoho_crm.models.PaginationInfo | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DealsListResultMeta"></a>

`DealsListResultMeta(**data: Any)`
:   Metadata for deals.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `more_records: bool | Any`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

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

<a id="Event"></a>

`Event(**data: Any)`
:   Zoho CRM event (meeting/calendar) object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `all_day: bool | Any | None`
    :   The type of the None singleton.

    `created_by: Any`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `end_date_time: str | Any | None`
    :   The type of the None singleton.

    `event_title: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `location: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_by: Any`
    :   The type of the None singleton.

    `modified_time: str | Any | None`
    :   The type of the None singleton.

    `owner: Any`
    :   The type of the None singleton.

    `participants: list[airbyte_agent_sdk.connectors.zoho_crm.models.EventParticipantsItem] | Any | None`
    :   The type of the None singleton.

    `record_status_s: str | Any | None`
    :   The type of the None singleton.

    `recurring_activity: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `remind_at: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `start_date_time: str | Any | None`
    :   The type of the None singleton.

    `what_id: Any`
    :   The type of the None singleton.

    `who_id: Any`
    :   The type of the None singleton.

<a id="EventParticipantsItem"></a>

`EventParticipantsItem(**data: Any)`
:   Nested schema for Event.Participants_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any`
    :   The type of the None singleton.

    `invited: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `participant: str | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

<a id="EventsList"></a>

`EventsList(**data: Any)`
:   Paginated list of events
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.zoho_crm.models.Event] | Any`
    :   The type of the None singleton.

    `info: airbyte_agent_sdk.connectors.zoho_crm.models.PaginationInfo | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="EventsListResultMeta"></a>

`EventsListResultMeta(**data: Any)`
:   Metadata for events.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `more_records: bool | Any`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

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

<a id="Invoice"></a>

`Invoice(**data: Any)`
:   Zoho CRM invoice object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_name: Any`
    :   The type of the None singleton.

    `adjustment: float | Any | None`
    :   The type of the None singleton.

    `billing_city: str | Any | None`
    :   The type of the None singleton.

    `billing_code: str | Any | None`
    :   The type of the None singleton.

    `billing_country: str | Any | None`
    :   The type of the None singleton.

    `billing_state: str | Any | None`
    :   The type of the None singleton.

    `billing_street: str | Any | None`
    :   The type of the None singleton.

    `contact_name: Any`
    :   The type of the None singleton.

    `created_by: Any`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `deal_name: Any`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `discount: float | Any | None`
    :   The type of the None singleton.

    `due_date: str | Any | None`
    :   The type of the None singleton.

    `excise_duty: float | Any | None`
    :   The type of the None singleton.

    `grand_total: float | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `invoice_date: str | Any | None`
    :   The type of the None singleton.

    `invoice_number: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_by: Any`
    :   The type of the None singleton.

    `modified_time: str | Any | None`
    :   The type of the None singleton.

    `owner: Any`
    :   The type of the None singleton.

    `purchase_order: str | Any | None`
    :   The type of the None singleton.

    `record_status_s: str | Any | None`
    :   The type of the None singleton.

    `sales_order: Any`
    :   The type of the None singleton.

    `shipping_city: str | Any | None`
    :   The type of the None singleton.

    `shipping_code: str | Any | None`
    :   The type of the None singleton.

    `shipping_country: str | Any | None`
    :   The type of the None singleton.

    `shipping_state: str | Any | None`
    :   The type of the None singleton.

    `shipping_street: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `sub_total: float | Any | None`
    :   The type of the None singleton.

    `subject: str | Any | None`
    :   The type of the None singleton.

    `tax: float | Any | None`
    :   The type of the None singleton.

    `terms_and_conditions: str | Any | None`
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

    `data: list[airbyte_agent_sdk.connectors.zoho_crm.models.Invoice] | Any`
    :   The type of the None singleton.

    `info: airbyte_agent_sdk.connectors.zoho_crm.models.PaginationInfo | Any`
    :   The type of the None singleton.

    `model_config`
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

    `more_records: bool | Any`
    :   The type of the None singleton.

    `page: int | Any`
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

<a id="Lead"></a>

`Lead(**data: Any)`
:   Zoho CRM lead object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annual_revenue: float | Any | None`
    :   The type of the None singleton.

    `city: str | Any | None`
    :   The type of the None singleton.

    `company: str | Any | None`
    :   The type of the None singleton.

    `converted_detail: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `country: str | Any | None`
    :   The type of the None singleton.

    `created_by: Any`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `fax: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `full_name: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `industry: str | Any | None`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `lead_source: str | Any | None`
    :   The type of the None singleton.

    `lead_status: str | Any | None`
    :   The type of the None singleton.

    `mobile: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_by: Any`
    :   The type of the None singleton.

    `modified_time: str | Any | None`
    :   The type of the None singleton.

    `no_of_employees: int | Any | None`
    :   The type of the None singleton.

    `owner: Any`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `rating: str | Any | None`
    :   The type of the None singleton.

    `record_status_s: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

    `street: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `website: str | Any | None`
    :   The type of the None singleton.

    `zip_code: str | Any | None`
    :   The type of the None singleton.

<a id="LeadsList"></a>

`LeadsList(**data: Any)`
:   Paginated list of leads
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.zoho_crm.models.Lead] | Any`
    :   The type of the None singleton.

    `info: airbyte_agent_sdk.connectors.zoho_crm.models.PaginationInfo | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="LeadsListResultMeta"></a>

`LeadsListResultMeta(**data: Any)`
:   Metadata for leads.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `more_records: bool | Any`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

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

<a id="LookupRef"></a>

`LookupRef(**data: Any)`
:   Lookup reference to another record
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

<a id="ModifiedBy"></a>

`ModifiedBy(**data: Any)`
:   User who last modified the record
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

<a id="Owner"></a>

`Owner(**data: Any)`
:   Record owner reference
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

<a id="PaginationInfo"></a>

`PaginationInfo(**data: Any)`
:   Pagination metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `more_records: bool | Any`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `sort_by: str | Any`
    :   The type of the None singleton.

    `sort_order: str | Any`
    :   The type of the None singleton.

<a id="Product"></a>

`Product(**data: Any)`
:   Zoho CRM product object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `commission_rate: float | Any | None`
    :   The type of the None singleton.

    `created_by: Any`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `handler: Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `manufacturer: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_by: Any`
    :   The type of the None singleton.

    `modified_time: str | Any | None`
    :   The type of the None singleton.

    `owner: Any`
    :   The type of the None singleton.

    `product_active: bool | Any | None`
    :   The type of the None singleton.

    `product_category: str | Any | None`
    :   The type of the None singleton.

    `product_code: str | Any | None`
    :   The type of the None singleton.

    `product_name: str | Any | None`
    :   The type of the None singleton.

    `qty_in_demand: float | Any | None`
    :   The type of the None singleton.

    `qty_in_stock: float | Any | None`
    :   The type of the None singleton.

    `qty_ordered: float | Any | None`
    :   The type of the None singleton.

    `record_status_s: str | Any | None`
    :   The type of the None singleton.

    `reorder_level: float | Any | None`
    :   The type of the None singleton.

    `sales_end_date: str | Any | None`
    :   The type of the None singleton.

    `sales_start_date: str | Any | None`
    :   The type of the None singleton.

    `support_expiry_date: str | Any | None`
    :   The type of the None singleton.

    `support_start_date: str | Any | None`
    :   The type of the None singleton.

    `tax: list[str] | Any | None`
    :   The type of the None singleton.

    `unit_price: float | Any | None`
    :   The type of the None singleton.

    `vendor_name: Any`
    :   The type of the None singleton.

<a id="ProductsList"></a>

`ProductsList(**data: Any)`
:   Paginated list of products
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.zoho_crm.models.Product] | Any`
    :   The type of the None singleton.

    `info: airbyte_agent_sdk.connectors.zoho_crm.models.PaginationInfo | Any`
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

    `model_config`
    :   The type of the None singleton.

    `more_records: bool | Any`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

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

<a id="Quote"></a>

`Quote(**data: Any)`
:   Zoho CRM quote object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_name: Any`
    :   The type of the None singleton.

    `adjustment: float | Any | None`
    :   The type of the None singleton.

    `billing_city: str | Any | None`
    :   The type of the None singleton.

    `billing_code: str | Any | None`
    :   The type of the None singleton.

    `billing_country: str | Any | None`
    :   The type of the None singleton.

    `billing_state: str | Any | None`
    :   The type of the None singleton.

    `billing_street: str | Any | None`
    :   The type of the None singleton.

    `carrier: str | Any | None`
    :   The type of the None singleton.

    `contact_name: Any`
    :   The type of the None singleton.

    `created_by: Any`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `deal_name: Any`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `discount: float | Any | None`
    :   The type of the None singleton.

    `grand_total: float | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_by: Any`
    :   The type of the None singleton.

    `modified_time: str | Any | None`
    :   The type of the None singleton.

    `owner: Any`
    :   The type of the None singleton.

    `quote_stage: str | Any | None`
    :   The type of the None singleton.

    `record_status_s: str | Any | None`
    :   The type of the None singleton.

    `shipping_city: str | Any | None`
    :   The type of the None singleton.

    `shipping_code: str | Any | None`
    :   The type of the None singleton.

    `shipping_country: str | Any | None`
    :   The type of the None singleton.

    `shipping_state: str | Any | None`
    :   The type of the None singleton.

    `shipping_street: str | Any | None`
    :   The type of the None singleton.

    `sub_total: float | Any | None`
    :   The type of the None singleton.

    `subject: str | Any | None`
    :   The type of the None singleton.

    `tax: float | Any | None`
    :   The type of the None singleton.

    `terms_and_conditions: str | Any | None`
    :   The type of the None singleton.

    `valid_till: str | Any | None`
    :   The type of the None singleton.

<a id="QuotesList"></a>

`QuotesList(**data: Any)`
:   Paginated list of quotes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.zoho_crm.models.Quote] | Any`
    :   The type of the None singleton.

    `info: airbyte_agent_sdk.connectors.zoho_crm.models.PaginationInfo | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="QuotesListResultMeta"></a>

`QuotesListResultMeta(**data: Any)`
:   Metadata for quotes.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `more_records: bool | Any`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

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

<a id="Task"></a>

`Task(**data: Any)`
:   Zoho CRM task object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `closed_time: str | Any | None`
    :   The type of the None singleton.

    `created_by: Any`
    :   The type of the None singleton.

    `created_time: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `due_date: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_by: Any`
    :   The type of the None singleton.

    `modified_time: str | Any | None`
    :   The type of the None singleton.

    `owner: Any`
    :   The type of the None singleton.

    `priority: str | Any | None`
    :   The type of the None singleton.

    `record_status_s: str | Any | None`
    :   The type of the None singleton.

    `recurring_activity: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `remind_at: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `send_notification_email: bool | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `subject: str | Any | None`
    :   The type of the None singleton.

    `what_id: Any`
    :   The type of the None singleton.

    `who_id: Any`
    :   The type of the None singleton.

<a id="TasksList"></a>

`TasksList(**data: Any)`
:   Paginated list of tasks
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.zoho_crm.models.Task] | Any`
    :   The type of the None singleton.

    `info: airbyte_agent_sdk.connectors.zoho_crm.models.PaginationInfo | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TasksListResultMeta"></a>

`TasksListResultMeta(**data: Any)`
:   Metadata for tasks.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `more_records: bool | Any`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

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

<a id="ZohoCrmCheckResult"></a>

`ZohoCrmCheckResult(**data: Any)`
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

<a id="ZohoCrmExecuteResult"></a>

`ZohoCrmExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="ZohoCrmExecuteResultWithMeta"></a>

`ZohoCrmExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Account], AccountsListResultMeta]
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Call], CallsListResultMeta]
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Contact], ContactsListResultMeta]
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Deal], DealsListResultMeta]
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Event], EventsListResultMeta]
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Invoice], InvoicesListResultMeta]
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Lead], LeadsListResultMeta]
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Product], ProductsListResultMeta]
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Quote], QuotesListResultMeta]
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta[list[Task], TasksListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`ZohoCrmExecuteResultWithMeta[list[Account], AccountsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AccountsListResult"></a>

`AccountsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZohoCrmExecuteResultWithMeta[list[Call], CallsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CallsListResult"></a>

`CallsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZohoCrmExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CampaignsListResult"></a>

`CampaignsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZohoCrmExecuteResultWithMeta[list[Contact], ContactsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ContactsListResult"></a>

`ContactsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZohoCrmExecuteResultWithMeta[list[Deal], DealsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DealsListResult"></a>

`DealsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZohoCrmExecuteResultWithMeta[list[Event], EventsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="EventsListResult"></a>

`EventsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZohoCrmExecuteResultWithMeta[list[Invoice], InvoicesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
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

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZohoCrmExecuteResultWithMeta[list[Lead], LeadsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="LeadsListResult"></a>

`LeadsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZohoCrmExecuteResultWithMeta[list[Product], ProductsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
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

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZohoCrmExecuteResultWithMeta[list[Quote], QuotesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="QuotesListResult"></a>

`QuotesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZohoCrmExecuteResultWithMeta[list[Task], TasksListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TasksListResult"></a>

`TasksListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zoho_crm.models.ZohoCrmExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic