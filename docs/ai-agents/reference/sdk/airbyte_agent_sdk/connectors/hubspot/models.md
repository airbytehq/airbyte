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

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[CallsSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[CompaniesSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[ContactsSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[DealsSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[EmailsSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[MeetingsSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[NotesSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[TasksSearchData]
    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult[TicketsSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[CallsSearchData](**data: Any)`
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

<a id="CallsSearchResult"></a>

`CallsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

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

`AirbyteSearchResult[EmailsSearchData](**data: Any)`
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

<a id="EmailsSearchResult"></a>

`EmailsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[MeetingsSearchData](**data: Any)`
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

<a id="MeetingsSearchResult"></a>

`MeetingsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[NotesSearchData](**data: Any)`
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

<a id="NotesSearchResult"></a>

`NotesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TasksSearchData](**data: Any)`
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

<a id="TasksSearchResult"></a>

`TasksSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TicketsSearchData](**data: Any)`
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

<a id="TicketsSearchResult"></a>

`TicketsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.hubspot.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AssociationLabeledParams"></a>

`AssociationLabeledParams(**data: Any)`
:   Array of association type specifications. Each item defines a labeled association type
    to apply between the two records. Multiple labels can be set in a single call.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AssociationListResult"></a>

`AssociationListResult(**data: Any)`
:   Paginated list of associations for a CRM record
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.hubspot.models.AssociationListResultPaging | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.AssociationListResultResultsItem] | None`
    :   The type of the None singleton.

<a id="AssociationListResultPaging"></a>

`AssociationListResultPaging(**data: Any)`
:   Pagination information for retrieving additional results
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `additional_properties: typing.Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next: airbyte_agent_sdk.connectors.hubspot.models.AssociationListResultPagingNext | None`
    :   Cursor for the next page of results

<a id="AssociationListResultPagingNext"></a>

`AssociationListResultPagingNext(**data: Any)`
:   Cursor for the next page of results
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `after: str | None`
    :   Paging cursor token for retrieving the next page

    `link: str | None`
    :   URL for retrieving the next page of results

    `model_config`
    :   The type of the None singleton.

<a id="AssociationListResultResultsItem"></a>

`AssociationListResultResultsItem(**data: Any)`
:   Nested schema for AssociationListResult.results_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `association_types: list[airbyte_agent_sdk.connectors.hubspot.models.AssociationListResultResultsItemAssociationtypesItem] | None`
    :   List of association types linking the two records

    `model_config`
    :   The type of the None singleton.

    `to_object_id: typing.Any | None`
    :   ID of the associated target record

<a id="AssociationListResultResultsItemAssociationtypesItem"></a>

`AssociationListResultResultsItemAssociationtypesItem(**data: Any)`
:   Nested schema for AssociationListResultResultsItem.associationTypes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `category: str | None`
    :   Category of the association (HUBSPOT_DEFINED, USER_DEFINED, or INTEGRATOR_DEFINED)

    `label: str | None`
    :   Human-readable label for the association type (e.g., "Primary Company")

    `model_config`
    :   The type of the None singleton.

    `type_id: int | None`
    :   Numeric identifier for the association type

<a id="AssociationResult"></a>

`AssociationResult(**data: Any)`
:   Result of creating an association between two CRM records
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `completed_at: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `requested_at: str | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.AssociationResultResultsItem] | None`
    :   The type of the None singleton.

    `started_at: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

<a id="AssociationResultResultsItem"></a>

`AssociationResultResultsItem(**data: Any)`
:   Nested schema for AssociationResult.results_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `association_spec: airbyte_agent_sdk.connectors.hubspot.models.AssociationResultResultsItemAssociationspec | None`
    :   Details about the association type

    `from_: airbyte_agent_sdk.connectors.hubspot.models.AssociationResultResultsItemFrom | None`
    :   The source record of the association

    `model_config`
    :   The type of the None singleton.

    `to: airbyte_agent_sdk.connectors.hubspot.models.AssociationResultResultsItemTo | None`
    :   The target record of the association

<a id="AssociationResultResultsItemAssociationspec"></a>

`AssociationResultResultsItemAssociationspec(**data: Any)`
:   Details about the association type
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `association_category: str | None`
    :   Category of the association (HUBSPOT_DEFINED or USER_DEFINED)

    `association_type_id: int | None`
    :   Numeric ID of the association type

    `model_config`
    :   The type of the None singleton.

<a id="AssociationResultResultsItemFrom"></a>

`AssociationResultResultsItemFrom(**data: Any)`
:   The source record of the association
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   ID of the source record

    `model_config`
    :   The type of the None singleton.

<a id="AssociationResultResultsItemTo"></a>

`AssociationResultResultsItemTo(**data: Any)`
:   The target record of the association
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   ID of the target record

    `model_config`
    :   The type of the None singleton.

<a id="AssociationsListResultMeta"></a>

`AssociationsListResultMeta(**data: Any)`
:   Metadata for associations.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

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

    `archived: bool | None`
    :   The type of the None singleton.

    `archived_at: str | None`
    :   The type of the None singleton.

    `associations: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_write_trace_id: str | None`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.CRMObjectProperties | None`
    :   The type of the None singleton.

    `properties_with_history: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
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

    `hs_createdate: str | None`
    :   The type of the None singleton.

    `hs_lastmodifieddate: str | None`
    :   The type of the None singleton.

    `hs_object_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Call"></a>

`Call(**data: Any)`
:   HubSpot call engagement object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   The type of the None singleton.

    `archived_at: str | None`
    :   The type of the None singleton.

    `associations: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.CallProperties | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="CallCreateParams"></a>

`CallCreateParams(**data: Any)`
:   Parameters for creating a new call
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `associations: list[airbyte_agent_sdk.connectors.hubspot.models.CallCreateParamsAssociationsItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.CallCreateParamsProperties`
    :   The type of the None singleton.

<a id="CallCreateParamsAssociationsItem"></a>

`CallCreateParamsAssociationsItem(**data: Any)`
:   Nested schema for CallCreateParams.associations_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `to: airbyte_agent_sdk.connectors.hubspot.models.CallCreateParamsAssociationsItemTo | None`
    :   The type of the None singleton.

    `types: list[airbyte_agent_sdk.connectors.hubspot.models.CallCreateParamsAssociationsItemTypesItem] | None`
    :   The type of the None singleton.

<a id="CallCreateParamsAssociationsItemTo"></a>

`CallCreateParamsAssociationsItemTo(**data: Any)`
:   Nested schema for CallCreateParamsAssociationsItem.to
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   ID of the record to associate with

    `model_config`
    :   The type of the None singleton.

<a id="CallCreateParamsAssociationsItemTypesItem"></a>

`CallCreateParamsAssociationsItemTypesItem(**data: Any)`
:   Nested schema for CallCreateParamsAssociationsItem.types_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `association_category: str | None`
    :   Association category (e.g., HUBSPOT_DEFINED)

    `association_type_id: int | None`
    :   Association type ID (e.g., 194 for call-to-contact, 182 for call-to-company, 206 for call-to-deal, 220 for call-to-ticket)

    `model_config`
    :   The type of the None singleton.

<a id="CallCreateParamsProperties"></a>

`CallCreateParamsProperties(**data: Any)`
:   Call properties to set
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hs_call_body: str | None`
    :   Description or notes about the call

    `hs_call_direction: str | None`
    :   Direction of the call (INBOUND or OUTBOUND)

    `hs_call_disposition: str | None`
    :   The outcome of the call (e.g., connected, no answer, busy, left voicemail)

    `hs_call_duration: str | None`
    :   Duration of the call in milliseconds

    `hs_call_from_number: str | None`
    :   Phone number the call was made from

    `hs_call_status: str | None`
    :   Status of the call (e.g., COMPLETED, BUSY, NO_ANSWER, FAILED, CANCELED)

    `hs_call_title: str | None`
    :   Title or subject of the call

    `hs_call_to_number: str | None`
    :   Phone number the call was made to

    `hs_timestamp: str`
    :   Required. Timestamp when the call activity occurred (ISO 8601 format, e.g. 2025-01-15T10:30:00.000Z). Use the current time if the user does not specify one.

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this call

    `model_config`
    :   The type of the None singleton.

<a id="CallProperties"></a>

`CallProperties(**data: Any)`
:   Call properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hs_call_body: str | None`
    :   Description or notes about the call

    `hs_call_direction: str | None`
    :   Direction of the call (INBOUND or OUTBOUND)

    `hs_call_disposition: str | None`
    :   The outcome of the call (e.g., connected, no answer, busy, left voicemail)

    `hs_call_duration: str | None`
    :   Duration of the call in milliseconds

    `hs_call_from_number: str | None`
    :   Phone number the call was made from

    `hs_call_status: str | None`
    :   Status of the call (e.g., COMPLETED, BUSY, NO_ANSWER, FAILED, CANCELED, CONNECTING, RINGING, IN_PROGRESS)

    `hs_call_title: str | None`
    :   Title or subject of the call

    `hs_call_to_number: str | None`
    :   Phone number the call was made to

    `hs_createdate: str | None`
    :   Date the call was created

    `hs_lastmodifieddate: str | None`
    :   Last modified date

    `hs_object_id: str | None`
    :   HubSpot object ID

    `hs_timestamp: str | None`
    :   Timestamp when the call activity occurred

    `hubspot_owner_id: str | None`
    :   ID of the call owner

    `model_config`
    :   The type of the None singleton.

<a id="CallUpdateParams"></a>

`CallUpdateParams(**data: Any)`
:   Parameters for updating an existing call. Only provided properties will be updated.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.CallUpdateParamsProperties`
    :   The type of the None singleton.

<a id="CallUpdateParamsProperties"></a>

`CallUpdateParamsProperties(**data: Any)`
:   Call properties to update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hs_call_body: str | None`
    :   Description or notes about the call

    `hs_call_direction: str | None`
    :   Direction of the call (INBOUND or OUTBOUND)

    `hs_call_disposition: str | None`
    :   The outcome of the call

    `hs_call_duration: str | None`
    :   Duration of the call in milliseconds

    `hs_call_from_number: str | None`
    :   Phone number the call was made from

    `hs_call_status: str | None`
    :   Status of the call (e.g., COMPLETED, BUSY, NO_ANSWER)

    `hs_call_title: str | None`
    :   Title or subject of the call

    `hs_call_to_number: str | None`
    :   Phone number the call was made to

    `hs_timestamp: str | None`
    :   Timestamp when the call activity occurred

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this call

    `model_config`
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

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.hubspot.models.Paging | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.Call] | None`
    :   The type of the None singleton.

    `total: int | None`
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

    `next_cursor: str | None`
    :   The type of the None singleton.

    `next_link: str | None`
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

    `archived: bool | None`
    :   Indicates whether the call has been archived

    `created_at: str | None`
    :   Timestamp when the call was created

    `id: str | None`
    :   Unique identifier for the call record

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the call

    `properties_hs_call_body: str | None`
    :   Description or notes about the call

    `properties_hs_call_direction: str | None`
    :   Direction of the call (INBOUND or OUTBOUND)

    `properties_hs_call_duration: str | None`
    :   Duration of the call in milliseconds

    `properties_hs_call_status: str | None`
    :   Status of the call (e.g., COMPLETED, BUSY, NO_ANSWER)

    `properties_hs_call_title: str | None`
    :   Title or subject of the call

    `properties_hs_createdate: str | None`
    :   Date the call was created

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the call

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_timestamp: str | None`
    :   Timestamp when the call activity occurred

    `properties_hubspot_owner_id: str | None`
    :   ID of the call owner

    `updated_at: str | None`
    :   Timestamp when the call record was last modified

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

    `next_cursor: str | None`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

    `total: int | None`
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

    `paging: airbyte_agent_sdk.connectors.hubspot.models.Paging | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.Company] | None`
    :   The type of the None singleton.

    `total: int | None`
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

    `next_cursor: str | None`
    :   The type of the None singleton.

    `next_link: str | None`
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

    `properties_createdate: str | None`
    :   Date the company was created

    `properties_domain: str | None`
    :   Company domain name

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the company

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hubspot_owner_id: str | None`
    :   ID of the HubSpot owner assigned to this company

    `properties_name: str | None`
    :   Company name

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

    `archived: bool | None`
    :   The type of the None singleton.

    `archived_at: str | None`
    :   The type of the None singleton.

    `associations: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_write_trace_id: str | None`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.CompanyProperties | None`
    :   The type of the None singleton.

    `properties_with_history: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="CompanyCreateParams"></a>

`CompanyCreateParams(**data: Any)`
:   Parameters for creating a new company
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.CompanyCreateParamsProperties`
    :   The type of the None singleton.

<a id="CompanyCreateParamsProperties"></a>

`CompanyCreateParamsProperties(**data: Any)`
:   Company properties to set
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annualrevenue: str | None`
    :   Annual revenue

    `city: str | None`
    :   Company city

    `country: str | None`
    :   Company country

    `description: str | None`
    :   Company description

    `domain: str | None`
    :   Company domain name (e.g., example.com)

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this company

    `industry: str | None`
    :   Company industry (e.g., COMPUTER_SOFTWARE, INFORMATION_TECHNOLOGY_AND_SERVICES, INTERNET, FINANCIAL_SERVICES, MARKETING_AND_ADVERTISING, EDUCATION_MANAGEMENT)

    `lifecyclestage: str | None`
    :   Lifecycle stage (e.g., subscriber, lead, marketingqualifiedlead, salesqualifiedlead, opportunity, customer, evangelist, other)

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   Company name (required)

    `numberofemployees: str | None`
    :   Number of employees

    `phone: str | None`
    :   Company phone number

    `state: str | None`
    :   Company state/region

    `website: str | None`
    :   Company website URL

    `zip: str | None`
    :   Company postal/zip code

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

    `createdate: str | None`
    :   The type of the None singleton.

    `domain: str | None`
    :   The type of the None singleton.

    `hs_lastmodifieddate: str | None`
    :   The type of the None singleton.

    `hs_object_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

<a id="CompanyUpdateParams"></a>

`CompanyUpdateParams(**data: Any)`
:   Parameters for updating an existing company. Only provided properties will be updated.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.CompanyUpdateParamsProperties`
    :   The type of the None singleton.

<a id="CompanyUpdateParamsProperties"></a>

`CompanyUpdateParamsProperties(**data: Any)`
:   Company properties to update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annualrevenue: str | None`
    :   Annual revenue

    `city: str | None`
    :   Company city

    `country: str | None`
    :   Company country

    `description: str | None`
    :   Company description

    `domain: str | None`
    :   Company domain name (e.g., example.com)

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this company

    `industry: str | None`
    :   Company industry (e.g., COMPUTER_SOFTWARE, INFORMATION_TECHNOLOGY_AND_SERVICES, INTERNET, FINANCIAL_SERVICES, MARKETING_AND_ADVERTISING, EDUCATION_MANAGEMENT)

    `lifecyclestage: str | None`
    :   Lifecycle stage (e.g., subscriber, lead, marketingqualifiedlead, salesqualifiedlead, opportunity, customer, evangelist, other)

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Company name

    `numberofemployees: str | None`
    :   Number of employees

    `phone: str | None`
    :   Company phone number

    `state: str | None`
    :   Company state/region

    `website: str | None`
    :   Company website URL

    `zip: str | None`
    :   Company postal/zip code

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

    `archived: bool | None`
    :   The type of the None singleton.

    `archived_at: str | None`
    :   The type of the None singleton.

    `associations: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_write_trace_id: str | None`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.ContactProperties | None`
    :   The type of the None singleton.

    `properties_with_history: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="ContactCreateParams"></a>

`ContactCreateParams(**data: Any)`
:   Parameters for creating a new contact
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.ContactCreateParamsProperties`
    :   The type of the None singleton.

<a id="ContactCreateParamsProperties"></a>

`ContactCreateParamsProperties(**data: Any)`
:   Contact properties to set
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `company: str | None`
    :   Company name associated with the contact

    `email: str`
    :   Contact email address (required, used as unique identifier)

    `firstname: str | None`
    :   Contact first name

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this contact

    `jobtitle: str | None`
    :   Contact job title

    `lastname: str | None`
    :   Contact last name

    `lifecyclestage: str | None`
    :   Lifecycle stage (e.g., subscriber, lead, marketingqualifiedlead, salesqualifiedlead, opportunity, customer, evangelist, other)

    `model_config`
    :   The type of the None singleton.

    `phone: str | None`
    :   Contact phone number

    `website: str | None`
    :   Contact website URL

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

    `createdate: str | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `firstname: str | None`
    :   The type of the None singleton.

    `hs_object_id: str | None`
    :   The type of the None singleton.

    `lastmodifieddate: str | None`
    :   The type of the None singleton.

    `lastname: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ContactUpdateParams"></a>

`ContactUpdateParams(**data: Any)`
:   Parameters for updating an existing contact. Only provided properties will be updated.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.ContactUpdateParamsProperties`
    :   The type of the None singleton.

<a id="ContactUpdateParamsProperties"></a>

`ContactUpdateParamsProperties(**data: Any)`
:   Contact properties to update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `company: str | None`
    :   Company name associated with the contact

    `email: str | None`
    :   Contact email address

    `firstname: str | None`
    :   Contact first name

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this contact

    `jobtitle: str | None`
    :   Contact job title

    `lastname: str | None`
    :   Contact last name

    `lifecyclestage: str | None`
    :   Lifecycle stage (e.g., subscriber, lead, marketingqualifiedlead, salesqualifiedlead, opportunity, customer, evangelist, other)

    `model_config`
    :   The type of the None singleton.

    `phone: str | None`
    :   Contact phone number

    `website: str | None`
    :   Contact website URL

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

    `next_cursor: str | None`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

    `total: int | None`
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

    `paging: airbyte_agent_sdk.connectors.hubspot.models.Paging | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.Contact] | None`
    :   The type of the None singleton.

    `total: int | None`
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

    `next_cursor: str | None`
    :   The type of the None singleton.

    `next_link: str | None`
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
    :   Boolean flag indicating whether the contact has been archived or deleted

    `companies: list[typing.Any] | None`
    :   Associated company records linked to this contact

    `created_at: str | None`
    :   Timestamp indicating when the contact was first created in the system

    `id: str | None`
    :   Unique identifier for the contact record

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Key-value object storing all contact properties and their values.

    `properties_associatedcompanyid: str | None`
    :   ID of the associated company

    `properties_createdate: str | None`
    :   Date the contact was created

    `properties_email: str | None`
    :   Contact email address

    `properties_firstname: str | None`
    :   Contact first name

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hubspot_owner_id: str | None`
    :   ID of the HubSpot owner assigned to this contact

    `properties_lastmodifieddate: str | None`
    :   Last modified date of the contact

    `properties_lastname: str | None`
    :   Contact last name

    `updated_at: str | None`
    :   Timestamp indicating when the contact record was last modified

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

    `archived: bool | None`
    :   The type of the None singleton.

    `archived_at: str | None`
    :   The type of the None singleton.

    `associations: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_write_trace_id: str | None`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.DealProperties | None`
    :   The type of the None singleton.

    `properties_with_history: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="DealCreateParams"></a>

`DealCreateParams(**data: Any)`
:   Parameters for creating a new deal
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.DealCreateParamsProperties`
    :   The type of the None singleton.

<a id="DealCreateParamsProperties"></a>

`DealCreateParamsProperties(**data: Any)`
:   Deal properties to set
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | None`
    :   Deal amount

    `closedate: str | None`
    :   Expected close date (ISO 8601 format, e.g., 2024-12-31T00:00:00.000Z)

    `dealname: str`
    :   Deal name (required)

    `dealstage: str | None`
    :   Deal stage ID (e.g., appointmentscheduled, qualifiedtobuy, presentationscheduled, decisionmakerboughtin, contractsent, closedwon, closedlost)

    `dealtype: str | None`
    :   Deal type (e.g., newbusiness, existingbusiness)

    `description: str | None`
    :   Deal description

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this deal

    `model_config`
    :   The type of the None singleton.

    `pipeline: str | None`
    :   Deal pipeline ID (defaults to the default pipeline)

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

    `amount: str | None`
    :   The type of the None singleton.

    `closedate: str | None`
    :   The type of the None singleton.

    `createdate: str | None`
    :   The type of the None singleton.

    `dealname: str | None`
    :   The type of the None singleton.

    `dealstage: str | None`
    :   The type of the None singleton.

    `hs_lastmodifieddate: str | None`
    :   The type of the None singleton.

    `hs_object_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pipeline: str | None`
    :   The type of the None singleton.

<a id="DealUpdateParams"></a>

`DealUpdateParams(**data: Any)`
:   Parameters for updating an existing deal. Only provided properties will be updated.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.DealUpdateParamsProperties`
    :   The type of the None singleton.

<a id="DealUpdateParamsProperties"></a>

`DealUpdateParamsProperties(**data: Any)`
:   Deal properties to update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: str | None`
    :   Deal amount

    `closedate: str | None`
    :   Expected close date (ISO 8601 format, e.g., 2024-12-31T00:00:00.000Z)

    `dealname: str | None`
    :   Deal name

    `dealstage: str | None`
    :   Deal stage ID (e.g., appointmentscheduled, qualifiedtobuy, presentationscheduled, decisionmakerboughtin, contractsent, closedwon, closedlost)

    `dealtype: str | None`
    :   Deal type (e.g., newbusiness, existingbusiness)

    `description: str | None`
    :   Deal description

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this deal

    `model_config`
    :   The type of the None singleton.

    `pipeline: str | None`
    :   Deal pipeline ID

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

    `next_cursor: str | None`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

    `total: int | None`
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

    `paging: airbyte_agent_sdk.connectors.hubspot.models.Paging | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.Deal] | None`
    :   The type of the None singleton.

    `total: int | None`
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

    `next_cursor: str | None`
    :   The type of the None singleton.

    `next_link: str | None`
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

    `properties_amount: str | None`
    :   Deal amount

    `properties_closedate: str | None`
    :   Expected close date of the deal

    `properties_createdate: str | None`
    :   Date the deal was created

    `properties_dealname: str | None`
    :   Deal name

    `properties_dealstage: str | None`
    :   Current deal stage

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the deal

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hubspot_owner_id: str | None`
    :   ID of the HubSpot owner assigned to this deal

    `properties_pipeline: str | None`
    :   Deal pipeline

    `updated_at: str | None`
    :   Timestamp when the deal record was last modified

<a id="Email"></a>

`Email(**data: Any)`
:   HubSpot email engagement object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   The type of the None singleton.

    `archived_at: str | None`
    :   The type of the None singleton.

    `associations: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.EmailProperties | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="EmailCreateParams"></a>

`EmailCreateParams(**data: Any)`
:   Parameters for creating a new email
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `associations: list[airbyte_agent_sdk.connectors.hubspot.models.EmailCreateParamsAssociationsItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.EmailCreateParamsProperties`
    :   The type of the None singleton.

<a id="EmailCreateParamsAssociationsItem"></a>

`EmailCreateParamsAssociationsItem(**data: Any)`
:   Nested schema for EmailCreateParams.associations_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `to: airbyte_agent_sdk.connectors.hubspot.models.EmailCreateParamsAssociationsItemTo | None`
    :   The type of the None singleton.

    `types: list[airbyte_agent_sdk.connectors.hubspot.models.EmailCreateParamsAssociationsItemTypesItem] | None`
    :   The type of the None singleton.

<a id="EmailCreateParamsAssociationsItemTo"></a>

`EmailCreateParamsAssociationsItemTo(**data: Any)`
:   Nested schema for EmailCreateParamsAssociationsItem.to
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   ID of the record to associate with

    `model_config`
    :   The type of the None singleton.

<a id="EmailCreateParamsAssociationsItemTypesItem"></a>

`EmailCreateParamsAssociationsItemTypesItem(**data: Any)`
:   Nested schema for EmailCreateParamsAssociationsItem.types_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `association_category: str | None`
    :   Association category (e.g., HUBSPOT_DEFINED)

    `association_type_id: int | None`
    :   Association type ID (e.g., 198 for email-to-contact, 186 for email-to-company, 210 for email-to-deal, 224 for email-to-ticket)

    `model_config`
    :   The type of the None singleton.

<a id="EmailCreateParamsProperties"></a>

`EmailCreateParamsProperties(**data: Any)`
:   Email properties to set
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hs_email_direction: str`
    :   Required. Direction of the email (EMAIL for sent, INCOMING_EMAIL for received, FORWARDED_EMAIL for forwarded)

    `hs_email_html: str | None`
    :   HTML body of the email

    `hs_email_sender_email: str | None`
    :   Sender email address

    `hs_email_status: str | None`
    :   Status of the email (BOUNCED, FAILED, SCHEDULED, SENDING, SENT, DRAFT)

    `hs_email_subject: str | None`
    :   Subject line of the email

    `hs_email_text: str | None`
    :   Plain text body of the email

    `hs_email_to_email: str | None`
    :   Recipient email address(es)

    `hs_timestamp: str`
    :   Required. Timestamp when the email activity occurred (ISO 8601 format, e.g. 2025-01-15T10:30:00.000Z). Use the current time if the user does not specify one.

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this email

    `model_config`
    :   The type of the None singleton.

<a id="EmailProperties"></a>

`EmailProperties(**data: Any)`
:   Email properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hs_createdate: str | None`
    :   Date the email was created

    `hs_email_direction: str | None`
    :   Direction of the email (EMAIL, INCOMING_EMAIL, FORWARDED_EMAIL)

    `hs_email_html: str | None`
    :   HTML body of the email

    `hs_email_sender_email: str | None`
    :   Sender email address

    `hs_email_status: str | None`
    :   Status of the email (e.g., BOUNCED, FAILED, SCHEDULED, SENDING, SENT, DRAFT)

    `hs_email_subject: str | None`
    :   Subject line of the email

    `hs_email_text: str | None`
    :   Plain text body of the email

    `hs_email_to_email: str | None`
    :   Recipient email address(es)

    `hs_lastmodifieddate: str | None`
    :   Last modified date

    `hs_object_id: str | None`
    :   HubSpot object ID

    `hs_timestamp: str | None`
    :   Timestamp when the email activity occurred

    `hubspot_owner_id: str | None`
    :   ID of the email owner

    `model_config`
    :   The type of the None singleton.

<a id="EmailUpdateParams"></a>

`EmailUpdateParams(**data: Any)`
:   Parameters for updating an existing email. Only provided properties will be updated.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.EmailUpdateParamsProperties`
    :   The type of the None singleton.

<a id="EmailUpdateParamsProperties"></a>

`EmailUpdateParamsProperties(**data: Any)`
:   Email properties to update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hs_email_direction: str | None`
    :   Direction of the email (EMAIL, INCOMING_EMAIL, FORWARDED_EMAIL)

    `hs_email_html: str | None`
    :   HTML body of the email

    `hs_email_status: str | None`
    :   Status of the email (BOUNCED, FAILED, SCHEDULED, SENDING, SENT, DRAFT)

    `hs_email_subject: str | None`
    :   Subject line of the email

    `hs_email_text: str | None`
    :   Plain text body of the email

    `hs_timestamp: str | None`
    :   Timestamp when the email activity occurred

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this email

    `model_config`
    :   The type of the None singleton.

<a id="EmailsList"></a>

`EmailsList(**data: Any)`
:   Paginated list of emails
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.hubspot.models.Paging | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.Email] | None`
    :   The type of the None singleton.

    `total: int | None`
    :   The type of the None singleton.

<a id="EmailsListResultMeta"></a>

`EmailsListResultMeta(**data: Any)`
:   Metadata for emails.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

<a id="EmailsSearchData"></a>

`EmailsSearchData(**data: Any)`
:   Search result data for emails entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the email has been archived

    `created_at: str | None`
    :   Timestamp when the email was created

    `id: str | None`
    :   Unique identifier for the email record

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the email

    `properties_hs_createdate: str | None`
    :   Date the email was created

    `properties_hs_email_direction: str | None`
    :   Direction of the email (EMAIL, INCOMING_EMAIL, FORWARDED_EMAIL)

    `properties_hs_email_status: str | None`
    :   Status of the email (BOUNCED, FAILED, SCHEDULED, SENDING, SENT, DRAFT)

    `properties_hs_email_subject: str | None`
    :   Subject line of the email

    `properties_hs_email_text: str | None`
    :   Plain text body of the email

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the email

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_timestamp: str | None`
    :   Timestamp when the email activity occurred

    `properties_hubspot_owner_id: str | None`
    :   ID of the email owner

    `updated_at: str | None`
    :   Timestamp when the email record was last modified

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

    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[AssociationListResult, AssociationsListResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[CRMObject], ObjectsListResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Call], CallsListResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Company], CompaniesApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Company], CompaniesListResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Contact], ContactsApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Contact], ContactsListResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Deal], DealsApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Deal], DealsListResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Email], EmailsListResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Meeting], MeetingsListResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Note], NotesListResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Task], TasksListResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Ticket], TicketsApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.hubspot.models.HubspotExecuteResultWithMeta[list[Ticket], TicketsListResultMeta]

    ### Class variables

    `meta: ~S | None`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`HubspotExecuteResultWithMeta[AssociationListResult, AssociationsListResultMeta](**data: Any)`
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

<a id="AssociationsListResult"></a>

`AssociationsListResult(**data: Any)`
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

`HubspotExecuteResultWithMeta[list[Call], CallsListResultMeta](**data: Any)`
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

<a id="CallsListResult"></a>

`CallsListResult(**data: Any)`
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

`HubspotExecuteResultWithMeta[list[Email], EmailsListResultMeta](**data: Any)`
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

<a id="EmailsListResult"></a>

`EmailsListResult(**data: Any)`
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

`HubspotExecuteResultWithMeta[list[Meeting], MeetingsListResultMeta](**data: Any)`
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

<a id="MeetingsListResult"></a>

`MeetingsListResult(**data: Any)`
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

`HubspotExecuteResultWithMeta[list[Note], NotesListResultMeta](**data: Any)`
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

<a id="NotesListResult"></a>

`NotesListResult(**data: Any)`
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

`HubspotExecuteResultWithMeta[list[Task], TasksListResultMeta](**data: Any)`
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

<a id="TasksListResult"></a>

`TasksListResult(**data: Any)`
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

<a id="Meeting"></a>

`Meeting(**data: Any)`
:   HubSpot meeting engagement object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   The type of the None singleton.

    `archived_at: str | None`
    :   The type of the None singleton.

    `associations: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.MeetingProperties | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="MeetingCreateParams"></a>

`MeetingCreateParams(**data: Any)`
:   Parameters for creating a new meeting
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `associations: list[airbyte_agent_sdk.connectors.hubspot.models.MeetingCreateParamsAssociationsItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.MeetingCreateParamsProperties`
    :   The type of the None singleton.

<a id="MeetingCreateParamsAssociationsItem"></a>

`MeetingCreateParamsAssociationsItem(**data: Any)`
:   Nested schema for MeetingCreateParams.associations_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `to: airbyte_agent_sdk.connectors.hubspot.models.MeetingCreateParamsAssociationsItemTo | None`
    :   The type of the None singleton.

    `types: list[airbyte_agent_sdk.connectors.hubspot.models.MeetingCreateParamsAssociationsItemTypesItem] | None`
    :   The type of the None singleton.

<a id="MeetingCreateParamsAssociationsItemTo"></a>

`MeetingCreateParamsAssociationsItemTo(**data: Any)`
:   Nested schema for MeetingCreateParamsAssociationsItem.to
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   ID of the record to associate with

    `model_config`
    :   The type of the None singleton.

<a id="MeetingCreateParamsAssociationsItemTypesItem"></a>

`MeetingCreateParamsAssociationsItemTypesItem(**data: Any)`
:   Nested schema for MeetingCreateParamsAssociationsItem.types_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `association_category: str | None`
    :   Association category (e.g., HUBSPOT_DEFINED)

    `association_type_id: int | None`
    :   Association type ID (e.g., 200 for meeting-to-contact, 188 for meeting-to-company, 212 for meeting-to-deal, 226 for meeting-to-ticket)

    `model_config`
    :   The type of the None singleton.

<a id="MeetingCreateParamsProperties"></a>

`MeetingCreateParamsProperties(**data: Any)`
:   Meeting properties to set
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hs_internal_meeting_notes: str | None`
    :   Internal notes about the meeting

    `hs_meeting_body: str | None`
    :   Description or notes about the meeting (supports HTML)

    `hs_meeting_end_time: str | None`
    :   End time of the meeting (ISO 8601 format, e.g. 2025-01-15T11:30:00.000Z)

    `hs_meeting_location: str | None`
    :   Location of the meeting

    `hs_meeting_outcome: str | None`
    :   Outcome of the meeting (e.g., SCHEDULED, COMPLETED, RESCHEDULED, NO_SHOW, CANCELED)

    `hs_meeting_start_time: str | None`
    :   Start time of the meeting (ISO 8601 format, e.g. 2025-01-15T10:30:00.000Z)

    `hs_meeting_title: str`
    :   Required. Title of the meeting

    `hs_timestamp: str`
    :   Required. Timestamp when the meeting activity occurred (ISO 8601 format, e.g. 2025-01-15T10:30:00.000Z). Use the current time if the user does not specify one.

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this meeting

    `model_config`
    :   The type of the None singleton.

<a id="MeetingProperties"></a>

`MeetingProperties(**data: Any)`
:   Meeting properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hs_createdate: str | None`
    :   Date the meeting was created

    `hs_internal_meeting_notes: str | None`
    :   Internal notes about the meeting

    `hs_lastmodifieddate: str | None`
    :   Last modified date

    `hs_meeting_body: str | None`
    :   Description or notes about the meeting

    `hs_meeting_end_time: str | None`
    :   End time of the meeting (ISO 8601 format)

    `hs_meeting_location: str | None`
    :   Location of the meeting

    `hs_meeting_outcome: str | None`
    :   Outcome of the meeting (e.g., SCHEDULED, COMPLETED, RESCHEDULED, NO_SHOW, CANCELED)

    `hs_meeting_start_time: str | None`
    :   Start time of the meeting (ISO 8601 format)

    `hs_meeting_title: str | None`
    :   Title of the meeting

    `hs_object_id: str | None`
    :   HubSpot object ID

    `hs_timestamp: str | None`
    :   Timestamp when the meeting activity occurred

    `hubspot_owner_id: str | None`
    :   ID of the meeting owner

    `model_config`
    :   The type of the None singleton.

<a id="MeetingUpdateParams"></a>

`MeetingUpdateParams(**data: Any)`
:   Parameters for updating an existing meeting. Only provided properties will be updated.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.MeetingUpdateParamsProperties`
    :   The type of the None singleton.

<a id="MeetingUpdateParamsProperties"></a>

`MeetingUpdateParamsProperties(**data: Any)`
:   Meeting properties to update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hs_internal_meeting_notes: str | None`
    :   Internal notes about the meeting

    `hs_meeting_body: str | None`
    :   Description or notes about the meeting (supports HTML)

    `hs_meeting_end_time: str | None`
    :   End time of the meeting (ISO 8601 format)

    `hs_meeting_location: str | None`
    :   Location of the meeting

    `hs_meeting_outcome: str | None`
    :   Outcome of the meeting (e.g., SCHEDULED, COMPLETED, RESCHEDULED, NO_SHOW, CANCELED)

    `hs_meeting_start_time: str | None`
    :   Start time of the meeting (ISO 8601 format)

    `hs_meeting_title: str | None`
    :   Title of the meeting

    `hs_timestamp: str | None`
    :   Timestamp when the meeting activity occurred

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this meeting

    `model_config`
    :   The type of the None singleton.

<a id="MeetingsList"></a>

`MeetingsList(**data: Any)`
:   Paginated list of meetings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.hubspot.models.Paging | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.Meeting] | None`
    :   The type of the None singleton.

    `total: int | None`
    :   The type of the None singleton.

<a id="MeetingsListResultMeta"></a>

`MeetingsListResultMeta(**data: Any)`
:   Metadata for meetings.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

<a id="MeetingsSearchData"></a>

`MeetingsSearchData(**data: Any)`
:   Search result data for meetings entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the meeting has been archived

    `created_at: str | None`
    :   Timestamp when the meeting was created

    `id: str | None`
    :   Unique identifier for the meeting record

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the meeting

    `properties_hs_createdate: str | None`
    :   Date the meeting was created

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the meeting

    `properties_hs_meeting_body: str | None`
    :   Description or notes about the meeting

    `properties_hs_meeting_end_time: str | None`
    :   End time of the meeting

    `properties_hs_meeting_location: str | None`
    :   Location of the meeting

    `properties_hs_meeting_outcome: str | None`
    :   Outcome of the meeting (e.g., SCHEDULED, COMPLETED, NO_SHOW, CANCELED)

    `properties_hs_meeting_start_time: str | None`
    :   Start time of the meeting

    `properties_hs_meeting_title: str | None`
    :   Title of the meeting

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_timestamp: str | None`
    :   Timestamp when the meeting activity occurred

    `properties_hubspot_owner_id: str | None`
    :   ID of the meeting owner

    `updated_at: str | None`
    :   Timestamp when the meeting record was last modified

<a id="Note"></a>

`Note(**data: Any)`
:   HubSpot note/engagement object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   The type of the None singleton.

    `archived_at: str | None`
    :   The type of the None singleton.

    `associations: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.NoteProperties | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="NoteCreateParams"></a>

`NoteCreateParams(**data: Any)`
:   Parameters for creating a new note
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `associations: list[airbyte_agent_sdk.connectors.hubspot.models.NoteCreateParamsAssociationsItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.NoteCreateParamsProperties`
    :   The type of the None singleton.

<a id="NoteCreateParamsAssociationsItem"></a>

`NoteCreateParamsAssociationsItem(**data: Any)`
:   Nested schema for NoteCreateParams.associations_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `to: airbyte_agent_sdk.connectors.hubspot.models.NoteCreateParamsAssociationsItemTo | None`
    :   The type of the None singleton.

    `types: list[airbyte_agent_sdk.connectors.hubspot.models.NoteCreateParamsAssociationsItemTypesItem] | None`
    :   The type of the None singleton.

<a id="NoteCreateParamsAssociationsItemTo"></a>

`NoteCreateParamsAssociationsItemTo(**data: Any)`
:   Nested schema for NoteCreateParamsAssociationsItem.to
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   ID of the record to associate with

    `model_config`
    :   The type of the None singleton.

<a id="NoteCreateParamsAssociationsItemTypesItem"></a>

`NoteCreateParamsAssociationsItemTypesItem(**data: Any)`
:   Nested schema for NoteCreateParamsAssociationsItem.types_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `association_category: str | None`
    :   Association category (e.g., HUBSPOT_DEFINED)

    `association_type_id: int | None`
    :   Association type ID (e.g., 202 for note-to-contact, 190 for note-to-company, 214 for note-to-deal, 18 for note-to-ticket)

    `model_config`
    :   The type of the None singleton.

<a id="NoteCreateParamsProperties"></a>

`NoteCreateParamsProperties(**data: Any)`
:   Note properties to set
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hs_note_body: str`
    :   The body content of the note (supports HTML)

    `hs_timestamp: str`
    :   Required. Timestamp when the note activity occurred (ISO 8601 format, e.g. 2025-01-15T10:30:00.000Z). Use the current time if the user does not specify one.

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this note

    `model_config`
    :   The type of the None singleton.

<a id="NoteProperties"></a>

`NoteProperties(**data: Any)`
:   Note properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hs_createdate: str | None`
    :   Date the note was created

    `hs_lastmodifieddate: str | None`
    :   Last modified date

    `hs_note_body: str | None`
    :   The body content of the note (supports HTML)

    `hs_object_id: str | None`
    :   HubSpot object ID

    `hs_timestamp: str | None`
    :   Timestamp when the note activity occurred

    `hubspot_owner_id: str | None`
    :   ID of the note owner

    `model_config`
    :   The type of the None singleton.

<a id="NoteUpdateParams"></a>

`NoteUpdateParams(**data: Any)`
:   Parameters for updating an existing note. Only provided properties will be updated.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.NoteUpdateParamsProperties`
    :   The type of the None singleton.

<a id="NoteUpdateParamsProperties"></a>

`NoteUpdateParamsProperties(**data: Any)`
:   Note properties to update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hs_note_body: str | None`
    :   The body content of the note (supports HTML)

    `hs_timestamp: str | None`
    :   Timestamp when the note activity occurred

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this note

    `model_config`
    :   The type of the None singleton.

<a id="NotesList"></a>

`NotesList(**data: Any)`
:   Paginated list of notes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.hubspot.models.Paging | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.Note] | None`
    :   The type of the None singleton.

    `total: int | None`
    :   The type of the None singleton.

<a id="NotesListResultMeta"></a>

`NotesListResultMeta(**data: Any)`
:   Metadata for notes.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

<a id="NotesSearchData"></a>

`NotesSearchData(**data: Any)`
:   Search result data for notes entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the note has been archived

    `created_at: str | None`
    :   Timestamp when the note was created

    `id: str | None`
    :   Unique identifier for the note record

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the note

    `properties_hs_createdate: str | None`
    :   Date the note was created

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the note

    `properties_hs_note_body: str | None`
    :   The body content of the note (supports HTML)

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_timestamp: str | None`
    :   Timestamp when the note activity occurred

    `properties_hubspot_owner_id: str | None`
    :   ID of the note owner

    `updated_at: str | None`
    :   Timestamp when the note record was last modified

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

    `paging: airbyte_agent_sdk.connectors.hubspot.models.Paging | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.CRMObject] | None`
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

    `next_cursor: str | None`
    :   The type of the None singleton.

    `next_link: str | None`
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

    `next: airbyte_agent_sdk.connectors.hubspot.models.PagingNext | None`
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

    `after: str | None`
    :   Cursor for next page

    `link: str | None`
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

    `allows_sensitive_properties: bool | None`
    :   The type of the None singleton.

    `archived: bool | None`
    :   The type of the None singleton.

    `associations: list[airbyte_agent_sdk.connectors.hubspot.models.SchemaAssociationsItem] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `created_by_user_id: int | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `fully_qualified_name: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `labels: airbyte_agent_sdk.connectors.hubspot.models.SchemaLabels | None`
    :   The type of the None singleton.

    `meta_type: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `object_type_id: str | None`
    :   The type of the None singleton.

    `primary_display_property: str | None`
    :   The type of the None singleton.

    `properties: list[airbyte_agent_sdk.connectors.hubspot.models.SchemaPropertiesItem] | None`
    :   The type of the None singleton.

    `required_properties: list[str] | None`
    :   The type of the None singleton.

    `restorable: bool | None`
    :   The type of the None singleton.

    `searchable_properties: list[str] | None`
    :   The type of the None singleton.

    `secondary_display_properties: list[str] | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `updated_by_user_id: int | None`
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

    `cardinality: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `from_object_type_id: str | None`
    :   The type of the None singleton.

    `has_user_enforced_max_from_object_ids: bool | None`
    :   The type of the None singleton.

    `has_user_enforced_max_to_object_ids: bool | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `inverse_cardinality: str | None`
    :   The type of the None singleton.

    `max_from_object_ids: int | None`
    :   The type of the None singleton.

    `max_to_object_ids: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `to_object_type_id: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
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

    `plural: str | None`
    :   The type of the None singleton.

    `singular: str | None`
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

    `archived: bool | None`
    :   The type of the None singleton.

    `calculated: bool | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `created_user_id: str | None`
    :   The type of the None singleton.

    `data_sensitivity: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `display_order: int | None`
    :   The type of the None singleton.

    `external_options: bool | None`
    :   The type of the None singleton.

    `field_type: str | None`
    :   The type of the None singleton.

    `form_field: bool | None`
    :   The type of the None singleton.

    `group_name: str | None`
    :   The type of the None singleton.

    `has_unique_value: bool | None`
    :   The type of the None singleton.

    `hidden: bool | None`
    :   The type of the None singleton.

    `hubspot_defined: bool | None`
    :   The type of the None singleton.

    `label: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modification_metadata: airbyte_agent_sdk.connectors.hubspot.models.SchemaPropertiesItemModificationmetadata | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `options: list[typing.Any] | None`
    :   The type of the None singleton.

    `show_currency_symbol: bool | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `updated_user_id: str | None`
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

    `archivable: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `read_only_definition: bool | None`
    :   The type of the None singleton.

    `read_only_options: bool | None`
    :   The type of the None singleton.

    `read_only_value: bool | None`
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

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.Schema] | None`
    :   The type of the None singleton.

<a id="Task"></a>

`Task(**data: Any)`
:   HubSpot task engagement object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   The type of the None singleton.

    `archived_at: str | None`
    :   The type of the None singleton.

    `associations: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.TaskProperties | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="TaskCreateParams"></a>

`TaskCreateParams(**data: Any)`
:   Parameters for creating a new task
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `associations: list[airbyte_agent_sdk.connectors.hubspot.models.TaskCreateParamsAssociationsItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.TaskCreateParamsProperties`
    :   The type of the None singleton.

<a id="TaskCreateParamsAssociationsItem"></a>

`TaskCreateParamsAssociationsItem(**data: Any)`
:   Nested schema for TaskCreateParams.associations_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `to: airbyte_agent_sdk.connectors.hubspot.models.TaskCreateParamsAssociationsItemTo | None`
    :   The type of the None singleton.

    `types: list[airbyte_agent_sdk.connectors.hubspot.models.TaskCreateParamsAssociationsItemTypesItem] | None`
    :   The type of the None singleton.

<a id="TaskCreateParamsAssociationsItemTo"></a>

`TaskCreateParamsAssociationsItemTo(**data: Any)`
:   Nested schema for TaskCreateParamsAssociationsItem.to
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   ID of the record to associate with

    `model_config`
    :   The type of the None singleton.

<a id="TaskCreateParamsAssociationsItemTypesItem"></a>

`TaskCreateParamsAssociationsItemTypesItem(**data: Any)`
:   Nested schema for TaskCreateParamsAssociationsItem.types_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `association_category: str | None`
    :   Association category (e.g., HUBSPOT_DEFINED)

    `association_type_id: int | None`
    :   Association type ID (e.g., 204 for task-to-contact, 192 for task-to-company, 216 for task-to-deal, 228 for task-to-ticket)

    `model_config`
    :   The type of the None singleton.

<a id="TaskCreateParamsProperties"></a>

`TaskCreateParamsProperties(**data: Any)`
:   Task properties to set
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hs_task_body: str | None`
    :   Description or notes for the task (supports HTML)

    `hs_task_priority: str | None`
    :   Priority of the task (LOW, MEDIUM, HIGH)

    `hs_task_reminders: str | None`
    :   Reminder timestamp for the task (epoch milliseconds)

    `hs_task_status: str | None`
    :   Status of the task (NOT_STARTED, IN_PROGRESS, WAITING, COMPLETED, DEFERRED). Defaults to NOT_STARTED.

    `hs_task_subject: str`
    :   Required. Subject or title of the task

    `hs_task_type: str | None`
    :   Type of the task (TODO, CALL, EMAIL). Defaults to TODO.

    `hs_timestamp: str`
    :   Required. Due date / timestamp for the task (ISO 8601 format, e.g. 2025-01-15T10:30:00.000Z). Use the current time if the user does not specify one.

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this task

    `model_config`
    :   The type of the None singleton.

<a id="TaskProperties"></a>

`TaskProperties(**data: Any)`
:   Task properties
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hs_createdate: str | None`
    :   Date the task was created

    `hs_lastmodifieddate: str | None`
    :   Last modified date

    `hs_object_id: str | None`
    :   HubSpot object ID

    `hs_task_body: str | None`
    :   Description or notes for the task (supports HTML)

    `hs_task_priority: str | None`
    :   Priority of the task (e.g., LOW, MEDIUM, HIGH)

    `hs_task_reminders: str | None`
    :   Reminder timestamp for the task (epoch milliseconds)

    `hs_task_status: str | None`
    :   Status of the task (e.g., NOT_STARTED, IN_PROGRESS, WAITING, COMPLETED, DEFERRED)

    `hs_task_subject: str | None`
    :   Subject or title of the task

    `hs_task_type: str | None`
    :   Type of the task (e.g., TODO, CALL, EMAIL)

    `hs_timestamp: str | None`
    :   Timestamp when the task activity occurred (due date)

    `hubspot_owner_id: str | None`
    :   ID of the task owner

    `model_config`
    :   The type of the None singleton.

<a id="TaskUpdateParams"></a>

`TaskUpdateParams(**data: Any)`
:   Parameters for updating an existing task. Only provided properties will be updated.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.TaskUpdateParamsProperties`
    :   The type of the None singleton.

<a id="TaskUpdateParamsProperties"></a>

`TaskUpdateParamsProperties(**data: Any)`
:   Task properties to update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hs_task_body: str | None`
    :   Description or notes for the task (supports HTML)

    `hs_task_priority: str | None`
    :   Priority of the task (LOW, MEDIUM, HIGH)

    `hs_task_reminders: str | None`
    :   Reminder timestamp for the task (epoch milliseconds)

    `hs_task_status: str | None`
    :   Status of the task (NOT_STARTED, IN_PROGRESS, WAITING, COMPLETED, DEFERRED)

    `hs_task_subject: str | None`
    :   Subject or title of the task

    `hs_task_type: str | None`
    :   Type of the task (TODO, CALL, EMAIL)

    `hs_timestamp: str | None`
    :   Due date / timestamp for the task

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this task

    `model_config`
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

    `model_config`
    :   The type of the None singleton.

    `paging: airbyte_agent_sdk.connectors.hubspot.models.Paging | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.Task] | None`
    :   The type of the None singleton.

    `total: int | None`
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

    `next_cursor: str | None`
    :   The type of the None singleton.

    `next_link: str | None`
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

    `archived: bool | None`
    :   Indicates whether the task has been archived

    `created_at: str | None`
    :   Timestamp when the task was created

    `id: str | None`
    :   Unique identifier for the task record

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the task

    `properties_hs_createdate: str | None`
    :   Date the task was created

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the task

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_task_body: str | None`
    :   Description or notes for the task

    `properties_hs_task_priority: str | None`
    :   Priority of the task (LOW, MEDIUM, HIGH)

    `properties_hs_task_status: str | None`
    :   Status of the task (NOT_STARTED, IN_PROGRESS, WAITING, COMPLETED, DEFERRED)

    `properties_hs_task_subject: str | None`
    :   Subject or title of the task

    `properties_hs_task_type: str | None`
    :   Type of the task (TODO, CALL, EMAIL)

    `properties_hs_timestamp: str | None`
    :   Due date / timestamp for the task

    `properties_hubspot_owner_id: str | None`
    :   ID of the task owner

    `updated_at: str | None`
    :   Timestamp when the task record was last modified

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

    `archived: bool | None`
    :   The type of the None singleton.

    `archived_at: str | None`
    :   The type of the None singleton.

    `associations: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_write_trace_id: str | None`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.TicketProperties | None`
    :   The type of the None singleton.

    `properties_with_history: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="TicketCreateParams"></a>

`TicketCreateParams(**data: Any)`
:   Parameters for creating a new support ticket
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.TicketCreateParamsProperties`
    :   The type of the None singleton.

<a id="TicketCreateParamsProperties"></a>

`TicketCreateParamsProperties(**data: Any)`
:   Ticket properties to set
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   Ticket description/content

    `hs_pipeline: str`
    :   Ticket pipeline ID (required, use '0' for default pipeline)

    `hs_pipeline_stage: str`
    :   Pipeline stage ID (required, e.g., '1' for New in the default pipeline)

    `hs_ticket_category: str | None`
    :   Ticket category

    `hs_ticket_priority: str | None`
    :   Ticket priority (e.g., LOW, MEDIUM, HIGH)

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this ticket

    `model_config`
    :   The type of the None singleton.

    `subject: str`
    :   Ticket subject line (required)

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

    `content: str | None`
    :   The type of the None singleton.

    `createdate: str | None`
    :   The type of the None singleton.

    `hs_lastmodifieddate: str | None`
    :   The type of the None singleton.

    `hs_object_id: str | None`
    :   The type of the None singleton.

    `hs_pipeline: str | None`
    :   The type of the None singleton.

    `hs_pipeline_stage: str | None`
    :   The type of the None singleton.

    `hs_ticket_category: str | None`
    :   The type of the None singleton.

    `hs_ticket_priority: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `subject: str | None`
    :   The type of the None singleton.

<a id="TicketUpdateParams"></a>

`TicketUpdateParams(**data: Any)`
:   Parameters for updating an existing ticket. Only provided properties will be updated.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `properties: airbyte_agent_sdk.connectors.hubspot.models.TicketUpdateParamsProperties`
    :   The type of the None singleton.

<a id="TicketUpdateParamsProperties"></a>

`TicketUpdateParamsProperties(**data: Any)`
:   Ticket properties to update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   Ticket description/content

    `hs_pipeline: str | None`
    :   Ticket pipeline ID

    `hs_pipeline_stage: str | None`
    :   Pipeline stage ID

    `hs_ticket_category: str | None`
    :   Ticket category

    `hs_ticket_priority: str | None`
    :   Ticket priority (e.g., LOW, MEDIUM, HIGH)

    `hubspot_owner_id: str | None`
    :   ID of the HubSpot owner to assign to this ticket

    `model_config`
    :   The type of the None singleton.

    `subject: str | None`
    :   Ticket subject line

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

    `next_cursor: str | None`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

    `total: int | None`
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

    `paging: airbyte_agent_sdk.connectors.hubspot.models.Paging | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.hubspot.models.Ticket] | None`
    :   The type of the None singleton.

    `total: int | None`
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

    `next_cursor: str | None`
    :   The type of the None singleton.

    `next_link: str | None`
    :   The type of the None singleton.

<a id="TicketsSearchData"></a>

`TicketsSearchData(**data: Any)`
:   Search result data for tickets entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Indicates whether the ticket has been deleted and moved to the recycling bin

    `companies: list[typing.Any] | None`
    :   Collection of company records associated with the ticket

    `contacts: list[typing.Any] | None`
    :   Collection of contact records associated with the ticket

    `created_at: str | None`
    :   Timestamp when the ticket record was originally created

    `id: str | None`
    :   Unique identifier for the ticket record

    `model_config`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any]`
    :   Object containing all property values for the ticket

    `properties_content: str | None`
    :   Ticket content/description

    `properties_createdate: str | None`
    :   Date the ticket was created

    `properties_hs_lastmodifieddate: str | None`
    :   Last modified date of the ticket

    `properties_hs_object_id: str | None`
    :   HubSpot object ID

    `properties_hs_pipeline: str | None`
    :   Ticket pipeline

    `properties_hs_pipeline_stage: str | None`
    :   Current pipeline stage of the ticket

    `properties_hs_ticket_category: str | None`
    :   Ticket category

    `properties_hs_ticket_priority: str | None`
    :   Ticket priority level

    `properties_subject: str | None`
    :   Ticket subject line

    `updated_at: str | None`
    :   Timestamp when the ticket record was last modified