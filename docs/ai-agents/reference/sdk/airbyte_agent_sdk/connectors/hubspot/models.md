---
id: airbyte_agent_sdk-connectors-hubspot-models
title: airbyte_agent_sdk.connectors.hubspot.models
---

Module airbyte_agent_sdk.connectors.hubspot.models
==================================================
Pydantic models for hubspot connector.

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

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[CompaniesSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[ContactsSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[DealsSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[CompaniesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CompaniesSearchResult"></a>

`CompaniesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ContactsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[DealsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CRMObject"></a>

`CRMObject(**data: Any)`
:   Generic HubSpot CRM object (for custom objects)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | Any`
    :   The type of the None singleton.

    `archived_at: str | Any | None`
    :   The type of the None singleton.

    `associations: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_write_trace_id: str | Any | None`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.CRMObjectProperties | Any`
    :   The type of the None singleton.

    `properties_with_history: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="CRMObjectProperties"></a>

`CRMObjectProperties(**data: Any)`
:   Object properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hs_createdate: str | Any | None`
    :   The type of the None singleton.

    `hs_lastmodifieddate: str | Any | None`
    :   The type of the None singleton.

    `hs_object_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CompaniesApiSearchResultMeta"></a>

`CompaniesApiSearchResultMeta(**data: Any)`
:   Metadata for companies.Action.API_SEARCH operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any`
    :   The type of the None singleton.

    `next_link: str | Any`
    :   The type of the None singleton.

    `total: int | Any`
    :   The type of the None singleton.

<a id="CompaniesList"></a>

`CompaniesList(**data: Any)`
:   Paginated list of companies
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.hubspot.models.Paging | Any`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.Company] | Any`
    :   The type of the None singleton.

    `total: int | Any`
    :   The type of the None singleton.

<a id="CompaniesListResultMeta"></a>

`CompaniesListResultMeta(**data: Any)`
:   Metadata for companies.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any`
    :   The type of the None singleton.

    `next_link: str | Any`
    :   The type of the None singleton.

<a id="CompaniesSearchData"></a>

`CompaniesSearchData(**data: Any)`
:   Search result data for companies entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the company has been deleted and moved to the recycling bin

    `contacts: list[typing.Any] | None`
    :   Associated contact records linked to this company

    `created_at: str | None`
    :   Timestamp when the company record was created

    `id: str | None`
    :   Unique identifier for the company record

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the company

    `updated_at: str | None`
    :   Timestamp when the company record was last modified

<a id="Company"></a>

`Company(**data: Any)`
:   HubSpot company object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | Any`
    :   The type of the None singleton.

    `archived_at: str | Any | None`
    :   The type of the None singleton.

    `associations: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_write_trace_id: str | Any | None`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.CompanyProperties | Any`
    :   The type of the None singleton.

    `properties_with_history: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="CompanyProperties"></a>

`CompanyProperties(**data: Any)`
:   Company properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `createdate: str | Any | None`
    :   The type of the None singleton.

    `domain: str | Any | None`
    :   The type of the None singleton.

    `hs_lastmodifieddate: str | Any | None`
    :   The type of the None singleton.

    `hs_object_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

<a id="Contact"></a>

`Contact(**data: Any)`
:   HubSpot contact object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | Any`
    :   The type of the None singleton.

    `archived_at: str | Any | None`
    :   The type of the None singleton.

    `associations: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_write_trace_id: str | Any | None`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.ContactProperties | Any`
    :   The type of the None singleton.

    `properties_with_history: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="ContactProperties"></a>

`ContactProperties(**data: Any)`
:   Contact properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `createdate: str | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `firstname: str | Any | None`
    :   The type of the None singleton.

    `hs_object_id: str | Any | None`
    :   The type of the None singleton.

    `lastmodifieddate: str | Any | None`
    :   The type of the None singleton.

    `lastname: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ContactsApiSearchResultMeta"></a>

`ContactsApiSearchResultMeta(**data: Any)`
:   Metadata for contacts.Action.API_SEARCH operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any`
    :   The type of the None singleton.

    `next_link: str | Any`
    :   The type of the None singleton.

    `total: int | Any`
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

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.hubspot.models.Paging | Any`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.Contact] | Any`
    :   The type of the None singleton.

    `total: int | Any`
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

    `next_cursor: str | Any`
    :   The type of the None singleton.

    `next_link: str | Any`
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

    `archived: bool | None`
    :   Boolean flag indicating whether the contact has been archived or deleted.

    `companies: list[typing.Any] | None`
    :   Associated company records linked to this contact.

    `created_at: str | None`
    :   Timestamp indicating when the contact was first created in the system.

    `id: str | None`
    :   Unique identifier for the contact record.

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Key-value object storing all contact properties and their values.

    `updated_at: str | None`
    :   Timestamp indicating when the contact record was last modified.

<a id="Deal"></a>

`Deal(**data: Any)`
:   HubSpot deal object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | Any`
    :   The type of the None singleton.

    `archived_at: str | Any | None`
    :   The type of the None singleton.

    `associations: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_write_trace_id: str | Any | None`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.DealProperties | Any`
    :   The type of the None singleton.

    `properties_with_history: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="DealProperties"></a>

`DealProperties(**data: Any)`
:   Deal properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | Any | None`
    :   The type of the None singleton.

    `closedate: str | Any | None`
    :   The type of the None singleton.

    `createdate: str | Any | None`
    :   The type of the None singleton.

    `dealname: str | Any | None`
    :   The type of the None singleton.

    `dealstage: str | Any | None`
    :   The type of the None singleton.

    `hs_lastmodifieddate: str | Any | None`
    :   The type of the None singleton.

    `hs_object_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pipeline: str | Any | None`
    :   The type of the None singleton.

<a id="DealsApiSearchResultMeta"></a>

`DealsApiSearchResultMeta(**data: Any)`
:   Metadata for deals.Action.API_SEARCH operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any`
    :   The type of the None singleton.

    `next_link: str | Any`
    :   The type of the None singleton.

    `total: int | Any`
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

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.hubspot.models.Paging | Any`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.Deal] | Any`
    :   The type of the None singleton.

    `total: int | Any`
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

    `next_cursor: str | Any`
    :   The type of the None singleton.

    `next_link: str | Any`
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

    `archived: bool | None`
    :   Indicates whether the deal has been deleted and moved to the recycling bin

    `companies: list[typing.Any] | None`
    :   Collection of company records associated with the deal

    `contacts: list[typing.Any] | None`
    :   Collection of contact records associated with the deal

    `created_at: str | None`
    :   Timestamp when the deal record was originally created

    `id: str | None`
    :   Unique identifier for the deal record

    `line_items: list[typing.Any] | None`
    :   Collection of product line items associated with the deal

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Key-value object containing all deal properties and custom fields

    `updated_at: str | None`
    :   Timestamp when the deal record was last modified

<a id="HubspotCheckResult"></a>

`HubspotCheckResult(**data: Any)`
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

<a id="HubspotExecuteResult"></a>

`HubspotExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult[list[Schema]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="HubspotExecuteResultWithMeta"></a>

`HubspotExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[CRMObject], ObjectsListResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Company], CompaniesApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Company], CompaniesListResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Contact], ContactsApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Contact], ContactsListResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Deal], DealsApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Deal], DealsListResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Ticket], TicketsApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Ticket], TicketsListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`HubspotExecuteResultWithMeta[list[CRMObject], ObjectsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ObjectsListResult"></a>

`ObjectsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HubspotExecuteResultWithMeta[list[Company], CompaniesApiSearchResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CompaniesApiSearchResult"></a>

`CompaniesApiSearchResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HubspotExecuteResultWithMeta[list[Company], CompaniesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CompaniesListResult"></a>

`CompaniesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HubspotExecuteResultWithMeta[list[Contact], ContactsApiSearchResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ContactsApiSearchResult"></a>

`ContactsApiSearchResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HubspotExecuteResultWithMeta[list[Contact], ContactsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
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

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HubspotExecuteResultWithMeta[list[Deal], DealsApiSearchResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DealsApiSearchResult"></a>

`DealsApiSearchResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HubspotExecuteResultWithMeta[list[Deal], DealsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
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

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HubspotExecuteResultWithMeta[list[Ticket], TicketsApiSearchResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TicketsApiSearchResult"></a>

`TicketsApiSearchResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HubspotExecuteResultWithMeta[list[Ticket], TicketsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TicketsListResult"></a>

`TicketsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HubspotExecuteResult[list[Schema]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SchemasListResult"></a>

`SchemasListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="HubspotOAuthCredentials"></a>

`HubspotOAuthCredentials(**data: Any)`
:   HubSpot OAuth App Credentials - Provide your own HubSpot OAuth app credentials to override the default Airbyte-managed ones.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str`
    :   Your HubSpot OAuth app's client ID

    `client_secret: str`
    :   Your HubSpot OAuth app's client secret

    `model_config`
    :   The type of the None singleton.

<a id="HubspotOauth2AuthConfig"></a>

`HubspotOauth2AuthConfig(**data: Any)`
:   OAuth2
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str | None`
    :   Your HubSpot OAuth2 Access Token (optional if refresh_token is provided)

    `client_id: str | None`
    :   Your HubSpot OAuth2 Client ID

    `client_secret: str | None`
    :   Your HubSpot OAuth2 Client Secret

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   Your HubSpot OAuth2 Refresh Token

<a id="HubspotPrivateAppAuthConfig"></a>

`HubspotPrivateAppAuthConfig(**data: Any)`
:   Private App
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `private_app_token: str`
    :   Access token from a HubSpot Private App

<a id="ObjectsList"></a>

`ObjectsList(**data: Any)`
:   Paginated list of generic CRM objects
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.hubspot.models.Paging | Any`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.CRMObject] | Any`
    :   The type of the None singleton.

<a id="ObjectsListResultMeta"></a>

`ObjectsListResultMeta(**data: Any)`
:   Metadata for objects.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any`
    :   The type of the None singleton.

    `next_link: str | Any`
    :   The type of the None singleton.

<a id="Paging"></a>

`Paging(**data: Any)`
:   Pagination information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: airbyte_agent_sdk.connectors.hubspot.models.PagingNext | Any`
    :   The type of the None singleton.

<a id="PagingNext"></a>

`PagingNext(**data: Any)`
:   Nested schema for Paging.next
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `after: str | Any`
    :   Cursor for next page

    `link: str | Any`
    :   URL for next page

    `model_config`
    :   The type of the None singleton.

<a id="Schema"></a>

`Schema(**data: Any)`
:   Custom object schema definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allows_sensitive_properties: bool | Any`
    :   The type of the None singleton.

    `archived: bool | Any`
    :   The type of the None singleton.

    `associations: list[airbyte_agent_sdk.connectors.hubspot.models.SchemaAssociationsItem] | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `created_by_user_id: int | Any`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `fully_qualified_name: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `labels: airbyte_agent_sdk.connectors.hubspot.models.SchemaLabels | Any`
    :   The type of the None singleton.

    `meta_type: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `object_type_id: str | Any`
    :   The type of the None singleton.

    `primary_display_property: str | Any`
    :   The type of the None singleton.

    `properties: list[airbyte_agent_sdk.connectors.hubspot.models.SchemaPropertiesItem] | Any`
    :   The type of the None singleton.

    `required_properties: list[str] | Any`
    :   The type of the None singleton.

    `restorable: bool | Any`
    :   The type of the None singleton.

    `searchable_properties: list[str] | Any`
    :   The type of the None singleton.

    `secondary_display_properties: list[str] | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `updated_by_user_id: int | Any`
    :   The type of the None singleton.

<a id="SchemaAssociationsItem"></a>

`SchemaAssociationsItem(**data: Any)`
:   Nested schema for Schema.associations_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cardinality: str | Any`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `from_object_type_id: str | Any`
    :   The type of the None singleton.

    `has_user_enforced_max_from_object_ids: bool | Any`
    :   The type of the None singleton.

    `has_user_enforced_max_to_object_ids: bool | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `inverse_cardinality: str | Any`
    :   The type of the None singleton.

    `max_from_object_ids: int | Any`
    :   The type of the None singleton.

    `max_to_object_ids: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `to_object_type_id: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

<a id="SchemaLabels"></a>

`SchemaLabels(**data: Any)`
:   Display labels
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `plural: str | Any`
    :   The type of the None singleton.

    `singular: str | Any`
    :   The type of the None singleton.

<a id="SchemaPropertiesItem"></a>

`SchemaPropertiesItem(**data: Any)`
:   Nested schema for Schema.properties_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | Any`
    :   The type of the None singleton.

    `calculated: bool | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `created_user_id: str | Any`
    :   The type of the None singleton.

    `data_sensitivity: str | Any`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `display_order: int | Any`
    :   The type of the None singleton.

    `external_options: bool | Any`
    :   The type of the None singleton.

    `field_type: str | Any`
    :   The type of the None singleton.

    `form_field: bool | Any`
    :   The type of the None singleton.

    `group_name: str | Any`
    :   The type of the None singleton.

    `has_unique_value: bool | Any`
    :   The type of the None singleton.

    `hidden: bool | Any`
    :   The type of the None singleton.

    `hubspot_defined: bool | Any`
    :   The type of the None singleton.

    `label: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modification_metadata: airbyte_agent_sdk.connectors.hubspot.models.SchemaPropertiesItemModificationmetadata | Any`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `options: list[typing.Any] | Any`
    :   The type of the None singleton.

    `show_currency_symbol: bool | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `updated_user_id: str | Any`
    :   The type of the None singleton.

<a id="SchemaPropertiesItemModificationmetadata"></a>

`SchemaPropertiesItemModificationmetadata(**data: Any)`
:   Nested schema for SchemaPropertiesItem.modificationMetadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archivable: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `read_only_definition: bool | Any`
    :   The type of the None singleton.

    `read_only_options: bool | Any`
    :   The type of the None singleton.

    `read_only_value: bool | Any`
    :   The type of the None singleton.

<a id="SchemasList"></a>

`SchemasList(**data: Any)`
:   List of custom object schemas
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.Schema] | Any`
    :   The type of the None singleton.

<a id="Ticket"></a>

`Ticket(**data: Any)`
:   HubSpot ticket object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | Any`
    :   The type of the None singleton.

    `archived_at: str | Any | None`
    :   The type of the None singleton.

    `associations: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_write_trace_id: str | Any | None`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.TicketProperties | Any`
    :   The type of the None singleton.

    `properties_with_history: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="TicketProperties"></a>

`TicketProperties(**data: Any)`
:   Ticket properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | Any | None`
    :   The type of the None singleton.

    `createdate: str | Any | None`
    :   The type of the None singleton.

    `hs_lastmodifieddate: str | Any | None`
    :   The type of the None singleton.

    `hs_object_id: str | Any | None`
    :   The type of the None singleton.

    `hs_pipeline: str | Any | None`
    :   The type of the None singleton.

    `hs_pipeline_stage: str | Any | None`
    :   The type of the None singleton.

    `hs_ticket_category: str | Any | None`
    :   The type of the None singleton.

    `hs_ticket_priority: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `subject: str | Any | None`
    :   The type of the None singleton.

<a id="TicketsApiSearchResultMeta"></a>

`TicketsApiSearchResultMeta(**data: Any)`
:   Metadata for tickets.Action.API_SEARCH operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any`
    :   The type of the None singleton.

    `next_link: str | Any`
    :   The type of the None singleton.

    `total: int | Any`
    :   The type of the None singleton.

<a id="TicketsList"></a>

`TicketsList(**data: Any)`
:   Paginated list of tickets
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.hubspot.models.Paging | Any`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.Ticket] | Any`
    :   The type of the None singleton.

    `total: int | Any`
    :   The type of the None singleton.

<a id="TicketsListResultMeta"></a>

`TicketsListResultMeta(**data: Any)`
:   Metadata for tickets.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any`
    :   The type of the None singleton.

    `next_link: str | Any`
    :   The type of the None singleton.