---
id: airbyte_agent_sdk-connectors-incident_io-models
title: airbyte_agent_sdk.connectors.incident_io.models
---

Module airbyte_agent_sdk.connectors.incident_io.models
======================================================
Pydantic models for incident-io connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

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

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[AlertsSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[CatalogTypesSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[CustomFieldsSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[EscalationsSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[IncidentRolesSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[IncidentStatusesSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[IncidentTimestampsSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[IncidentUpdatesSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[IncidentsSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[SchedulesSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[SeveritiesSearchData]
    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[AlertsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`AlertsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CatalogTypesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`CatalogTypesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CustomFieldsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`CustomFieldsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[EscalationsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`EscalationsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[IncidentRolesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IncidentRolesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[IncidentStatusesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IncidentStatusesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[IncidentTimestampsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IncidentTimestampsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[IncidentUpdatesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IncidentUpdatesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[IncidentsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IncidentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SchedulesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`SchedulesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SeveritiesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`SeveritiesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`UsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`Alert(**data: Any)`
:   An alert ingested from an alert source
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `alert_source_id: str | Any | None`
    :   The type of the None singleton.

    `attributes: list[airbyte_agent_sdk.connectors.incident_io.models.AlertAttributesItem] | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `deduplication_key: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `resolved_at: str | Any | None`
    :   The type of the None singleton.

    `source_url: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`AlertAttributesItem(**data: Any)`
:   Nested schema for Alert.attributes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attribute: airbyte_agent_sdk.connectors.incident_io.models.AlertAttributesItemAttribute | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: airbyte_agent_sdk.connectors.incident_io.models.AlertAttributesItemValue | Any | None`
    :   The type of the None singleton.

`AlertAttributesItemAttribute(**data: Any)`
:   Nested schema for AlertAttributesItem.attribute
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `array: bool | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

`AlertAttributesItemValue(**data: Any)`
:   Nested schema for AlertAttributesItem.value
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `catalog_entry: airbyte_agent_sdk.connectors.incident_io.models.AlertAttributesItemValueCatalogEntry | Any | None`
    :   The type of the None singleton.

    `label: str | Any | None`
    :   The type of the None singleton.

    `literal: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`AlertAttributesItemValueCatalogEntry(**data: Any)`
:   Nested schema for AlertAttributesItemValue.catalog_entry
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `catalog_type_id: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

`AlertsListResultMeta(**data: Any)`
:   Metadata for alerts.Action.LIST operation
    
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

`AlertsSearchData(**data: Any)`
:   Search result data for alerts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `alert_source_id: str | None`
    :   ID of the alert source that generated this alert

    `attributes: list[typing.Any] | None`
    :   Structured alert attributes

    `created_at: str | None`
    :   When the alert was created

    `deduplication_key: str | None`
    :   Deduplication key uniquely referencing this alert

    `description: str | None`
    :   Description of the alert

    `id: str | None`
    :   Unique identifier for the alert

    `model_config`
    :   The type of the None singleton.

    `resolved_at: str | None`
    :   When the alert was resolved

    `source_url: str | None`
    :   Link to the alert in the upstream system

    `status: str | None`
    :   Status of the alert: firing or resolved

    `title: str | None`
    :   Title of the alert

    `updated_at: str | None`
    :   When the alert was last updated

`CatalogType(**data: Any)`
:   A catalog type defining a category of catalog entries
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `categories: list[str] | Any | None`
    :   The type of the None singleton.

    `color: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `icon: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_editable: bool | Any | None`
    :   The type of the None singleton.

    `last_synced_at: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `ranked: bool | Any | None`
    :   The type of the None singleton.

    `registry_type: str | Any | None`
    :   The type of the None singleton.

    `required_integrations: list[str] | Any | None`
    :   The type of the None singleton.

    `schema_: airbyte_agent_sdk.connectors.incident_io.models.CatalogTypeSchema | Any | None`
    :   The type of the None singleton.

    `semantic_type: str | Any | None`
    :   The type of the None singleton.

    `type_name: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`CatalogTypeSchema(**data: Any)`
:   Schema definition for the catalog type
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: list[airbyte_agent_sdk.connectors.incident_io.models.CatalogTypeSchemaAttributesItem] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `version: float | Any | None`
    :   The type of the None singleton.

`CatalogTypeSchemaAttributesItem(**data: Any)`
:   Nested schema for CatalogTypeSchema.attributes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `array: bool | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `mode: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

`CatalogTypesSearchData(**data: Any)`
:   Search result data for catalog_types entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: dict[str, typing.Any] | None`
    :   Annotations metadata

    `categories: list[typing.Any] | None`
    :   Categories this type belongs to

    `color: str | None`
    :   Display color

    `created_at: str | None`
    :   When the catalog type was created

    `description: str | None`
    :   Description of the catalog type

    `icon: str | None`
    :   Display icon

    `id: str | None`
    :   Unique identifier for the catalog type

    `is_editable: bool | None`
    :   Whether entries can be edited

    `last_synced_at: str | None`
    :   When the catalog type was last synced

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the catalog type

    `ranked: bool | None`
    :   Whether entries are ranked

    `registry_type: str | None`
    :   Registry type if synced from an integration

    `required_integrations: list[typing.Any] | None`
    :   Integrations required for this type

    `schema_: dict[str, typing.Any] | None`
    :   Schema definition for the catalog type

    `semantic_type: str | None`
    :   Semantic type for special behavior

    `type_name: str | None`
    :   Programmatic type name

    `updated_at: str | None`
    :   When the catalog type was last updated

`CustomField(**data: Any)`
:   A custom field definition for incidents
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `catalog_type_id: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `field_type: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`CustomFieldsSearchData(**data: Any)`
:   Search result data for custom_fields entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When the custom field was created

    `description: str | None`
    :   Description of the custom field

    `field_type: str | None`
    :   Type of field

    `id: str | None`
    :   Unique identifier for the custom field

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the custom field

    `updated_at: str | None`
    :   When the custom field was last updated

`Escalation(**data: Any)`
:   An escalation that pages people via escalation paths
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `creator: airbyte_agent_sdk.connectors.incident_io.models.EscalationCreator | Any | None`
    :   The type of the None singleton.

    `escalation_path_id: str | Any | None`
    :   The type of the None singleton.

    `events: list[airbyte_agent_sdk.connectors.incident_io.models.EscalationEventsItem] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `priority: airbyte_agent_sdk.connectors.incident_io.models.EscalationPriority | Any | None`
    :   The type of the None singleton.

    `related_alerts: list[airbyte_agent_sdk.connectors.incident_io.models.EscalationRelatedAlertsItem] | Any | None`
    :   The type of the None singleton.

    `related_incidents: list[airbyte_agent_sdk.connectors.incident_io.models.EscalationRelatedIncidentsItem] | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`EscalationCreator(**data: Any)`
:   The creator of this escalation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `alert: airbyte_agent_sdk.connectors.incident_io.models.EscalationCreatorAlert | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.incident_io.models.EscalationCreatorUser | Any | None`
    :   The type of the None singleton.

    `workflow: airbyte_agent_sdk.connectors.incident_io.models.EscalationCreatorWorkflow | Any | None`
    :   The type of the None singleton.

`EscalationCreatorAlert(**data: Any)`
:   Nested schema for EscalationCreator.alert
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

`EscalationCreatorUser(**data: Any)`
:   Nested schema for EscalationCreator.user
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `role: str | Any | None`
    :   The type of the None singleton.

    `slack_user_id: str | Any | None`
    :   The type of the None singleton.

`EscalationCreatorWorkflow(**data: Any)`
:   Nested schema for EscalationCreator.workflow
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

`EscalationEventsItem(**data: Any)`
:   Nested schema for Escalation.events_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channels: list[airbyte_agent_sdk.connectors.incident_io.models.EscalationEventsItemChannelsItem] | Any | None`
    :   The type of the None singleton.

    `event: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `occurred_at: str | Any | None`
    :   The type of the None singleton.

    `urgency: str | Any | None`
    :   The type of the None singleton.

    `users: list[airbyte_agent_sdk.connectors.incident_io.models.EscalationEventsItemUsersItem] | Any | None`
    :   The type of the None singleton.

`EscalationEventsItemChannelsItem(**data: Any)`
:   Nested schema for EscalationEventsItem.channels_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `microsoft_teams_channel_id: str | Any | None`
    :   The type of the None singleton.

    `microsoft_teams_team_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `slack_channel_id: str | Any | None`
    :   The type of the None singleton.

    `slack_team_id: str | Any | None`
    :   The type of the None singleton.

`EscalationEventsItemUsersItem(**data: Any)`
:   Nested schema for EscalationEventsItem.users_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `role: str | Any | None`
    :   The type of the None singleton.

    `slack_user_id: str | Any | None`
    :   The type of the None singleton.

`EscalationPriority(**data: Any)`
:   Priority of the escalation
    
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
    :   The type of the None singleton.

`EscalationRelatedAlertsItem(**data: Any)`
:   Nested schema for Escalation.related_alerts_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `alert_source_id: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `deduplication_key: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `resolved_at: str | Any | None`
    :   The type of the None singleton.

    `source_url: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`EscalationRelatedIncidentsItem(**data: Any)`
:   Nested schema for Escalation.related_incidents_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `external_id: int | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `reference: str | Any | None`
    :   The type of the None singleton.

    `status_category: str | Any | None`
    :   The type of the None singleton.

    `summary: str | Any | None`
    :   The type of the None singleton.

    `visibility: str | Any | None`
    :   The type of the None singleton.

`EscalationsListResultMeta(**data: Any)`
:   Metadata for escalations.Action.LIST operation
    
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

`EscalationsSearchData(**data: Any)`
:   Search result data for escalations entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When the escalation was created

    `creator: dict[str, typing.Any] | None`
    :   The creator of this escalation

    `escalation_path_id: str | None`
    :   ID of the escalation path used

    `events: list[typing.Any] | None`
    :   History of escalation events

    `id: str | None`
    :   Unique identifier for the escalation

    `model_config`
    :   The type of the None singleton.

    `priority: dict[str, typing.Any] | None`
    :   Priority of the escalation

    `related_alerts: list[typing.Any] | None`
    :   Alerts related to this escalation

    `related_incidents: list[typing.Any] | None`
    :   Incidents related to this escalation

    `status: str | None`
    :   Status: pending, triggered, acked, resolved, expired, cancelled

    `title: str | None`
    :   Title of the escalation

    `updated_at: str | None`
    :   When the escalation was last updated

`Incident(**data: Any)`
:   An incident tracked in incident.io
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `call_url: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `creator: airbyte_agent_sdk.connectors.incident_io.models.IncidentCreator | Any | None`
    :   The type of the None singleton.

    `custom_field_entries: list[airbyte_agent_sdk.connectors.incident_io.models.IncidentCustomFieldEntriesItem] | Any | None`
    :   The type of the None singleton.

    `duration_metrics: list[airbyte_agent_sdk.connectors.incident_io.models.IncidentDurationMetricsItem] | Any | None`
    :   The type of the None singleton.

    `has_debrief: bool | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `incident_role_assignments: list[airbyte_agent_sdk.connectors.incident_io.models.IncidentIncidentRoleAssignmentsItem] | Any | None`
    :   The type of the None singleton.

    `incident_status: airbyte_agent_sdk.connectors.incident_io.models.IncidentIncidentStatus | Any | None`
    :   The type of the None singleton.

    `incident_timestamp_values: list[airbyte_agent_sdk.connectors.incident_io.models.IncidentIncidentTimestampValuesItem] | Any | None`
    :   The type of the None singleton.

    `incident_type: airbyte_agent_sdk.connectors.incident_io.models.IncidentIncidentType | Any | None`
    :   The type of the None singleton.

    `mode: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `permalink: str | Any | None`
    :   The type of the None singleton.

    `reference: str | Any | None`
    :   The type of the None singleton.

    `severity: airbyte_agent_sdk.connectors.incident_io.models.IncidentSeverity | Any | None`
    :   The type of the None singleton.

    `slack_channel_id: str | Any | None`
    :   The type of the None singleton.

    `slack_channel_name: str | Any | None`
    :   The type of the None singleton.

    `slack_team_id: str | Any | None`
    :   The type of the None singleton.

    `summary: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `visibility: str | Any | None`
    :   The type of the None singleton.

    `workload_minutes_late: float | Any | None`
    :   The type of the None singleton.

    `workload_minutes_sleeping: float | Any | None`
    :   The type of the None singleton.

    `workload_minutes_total: float | Any | None`
    :   The type of the None singleton.

    `workload_minutes_working: float | Any | None`
    :   The type of the None singleton.

`IncidentCreator(**data: Any)`
:   The user who created the incident
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.incident_io.models.IncidentCreatorUser | Any | None`
    :   The type of the None singleton.

`IncidentCreatorUser(**data: Any)`
:   Nested schema for IncidentCreator.user
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `role: str | Any | None`
    :   The type of the None singleton.

    `slack_user_id: str | Any | None`
    :   The type of the None singleton.

`IncidentCustomFieldEntriesItem(**data: Any)`
:   Nested schema for Incident.custom_field_entries_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `custom_field: airbyte_agent_sdk.connectors.incident_io.models.IncidentCustomFieldEntriesItemCustomField | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `values: list[typing.Any] | Any | None`
    :   The type of the None singleton.

`IncidentCustomFieldEntriesItemCustomField(**data: Any)`
:   Nested schema for IncidentCustomFieldEntriesItem.custom_field
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | Any | None`
    :   The type of the None singleton.

    `field_type: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `options: list[typing.Any] | Any | None`
    :   The type of the None singleton.

`IncidentDurationMetricsItem(**data: Any)`
:   Nested schema for Incident.duration_metrics_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `duration_metric: airbyte_agent_sdk.connectors.incident_io.models.IncidentDurationMetricsItemDurationMetric | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`IncidentDurationMetricsItemDurationMetric(**data: Any)`
:   Nested schema for IncidentDurationMetricsItem.duration_metric
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

`IncidentIncidentRoleAssignmentsItem(**data: Any)`
:   Nested schema for Incident.incident_role_assignments_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee: airbyte_agent_sdk.connectors.incident_io.models.IncidentIncidentRoleAssignmentsItemAssignee | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `role: airbyte_agent_sdk.connectors.incident_io.models.IncidentIncidentRoleAssignmentsItemRole | Any | None`
    :   The type of the None singleton.

`IncidentIncidentRoleAssignmentsItemAssignee(**data: Any)`
:   Nested schema for IncidentIncidentRoleAssignmentsItem.assignee
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `role: str | Any | None`
    :   The type of the None singleton.

    `slack_user_id: str | Any | None`
    :   The type of the None singleton.

`IncidentIncidentRoleAssignmentsItemRole(**data: Any)`
:   Nested schema for IncidentIncidentRoleAssignmentsItem.role
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `instructions: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `required: bool | Any | None`
    :   The type of the None singleton.

    `role_type: str | Any | None`
    :   The type of the None singleton.

    `shortform: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`IncidentIncidentStatus(**data: Any)`
:   Current status of the incident
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `category: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `rank: float | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`IncidentIncidentTimestampValuesItem(**data: Any)`
:   Nested schema for Incident.incident_timestamp_values_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `incident_timestamp: airbyte_agent_sdk.connectors.incident_io.models.IncidentIncidentTimestampValuesItemIncidentTimestamp | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: airbyte_agent_sdk.connectors.incident_io.models.IncidentIncidentTimestampValuesItemValue | Any | None`
    :   The type of the None singleton.

`IncidentIncidentTimestampValuesItemIncidentTimestamp(**data: Any)`
:   Nested schema for IncidentIncidentTimestampValuesItem.incident_timestamp
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `rank: float | Any | None`
    :   The type of the None singleton.

`IncidentIncidentTimestampValuesItemValue(**data: Any)`
:   Nested schema for IncidentIncidentTimestampValuesItem.value
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `value: str | Any | None`
    :   The type of the None singleton.

`IncidentIncidentType(**data: Any)`
:   Type of the incident
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `create_in_triage: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `is_default: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `private_incidents_only: bool | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`IncidentIoAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your incident.io API key. Create one at https://app.incident.io/settings/api-keys

    `model_config`
    :   The type of the None singleton.

`IncidentIoCheckResult(**data: Any)`
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

`IncidentIoExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult[list[CatalogType]]
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult[list[CustomField]]
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult[list[IncidentRole]]
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult[list[IncidentStatus]]
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult[list[IncidentTimestamp]]
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult[list[Severity]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

`IncidentIoExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta[list[Alert], AlertsListResultMeta]
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta[list[Escalation], EscalationsListResultMeta]
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta[list[IncidentUpdate], IncidentUpdatesListResultMeta]
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta[list[Incident], IncidentsListResultMeta]
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta[list[Schedule], SchedulesListResultMeta]
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta[list[User], UsersListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`IncidentIoExecuteResultWithMeta[list[Alert], AlertsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`AlertsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IncidentIoExecuteResultWithMeta[list[Escalation], EscalationsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`EscalationsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IncidentIoExecuteResultWithMeta[list[IncidentUpdate], IncidentUpdatesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IncidentUpdatesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IncidentIoExecuteResultWithMeta[list[Incident], IncidentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IncidentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IncidentIoExecuteResultWithMeta[list[Schedule], SchedulesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`SchedulesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IncidentIoExecuteResultWithMeta[list[User], UsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`UsersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IncidentIoExecuteResult[list[CatalogType]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`CatalogTypesListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IncidentIoExecuteResult[list[CustomField]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`CustomFieldsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IncidentIoExecuteResult[list[IncidentRole]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IncidentRolesListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IncidentIoExecuteResult[list[IncidentStatus]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IncidentStatusesListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IncidentIoExecuteResult[list[IncidentTimestamp]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IncidentTimestampsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IncidentIoExecuteResult[list[Severity]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`SeveritiesListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.incident_io.models.IncidentIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IncidentRole(**data: Any)`
:   A role that can be assigned during an incident
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `instructions: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `required: bool | Any | None`
    :   The type of the None singleton.

    `role_type: str | Any | None`
    :   The type of the None singleton.

    `shortform: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`IncidentRolesSearchData(**data: Any)`
:   Search result data for incident_roles entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When the role was created

    `description: str | None`
    :   Description of the role

    `id: str | None`
    :   Unique identifier for the incident role

    `instructions: str | None`
    :   Instructions for the role holder

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the role

    `required: bool | None`
    :   Whether this role must be assigned

    `role_type: str | None`
    :   Type of role

    `shortform: str | None`
    :   Short form label for the role

    `updated_at: str | None`
    :   When the role was last updated

`IncidentSeverity(**data: Any)`
:   Severity of the incident
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `rank: float | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`IncidentStatus(**data: Any)`
:   A status that an incident can be in
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `category: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `rank: float | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`IncidentStatusesSearchData(**data: Any)`
:   Search result data for incident_statuses entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `category: str | None`
    :   Category: triage, active, post-incident, closed, etc.

    `created_at: str | None`
    :   When the status was created

    `description: str | None`
    :   Description of the status

    `id: str | None`
    :   Unique identifier for the status

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the status

    `rank: float | None`
    :   Rank for ordering

    `updated_at: str | None`
    :   When the status was last updated

`IncidentTimestamp(**data: Any)`
:   A timestamp definition for incidents
    
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

    `name: str | Any | None`
    :   The type of the None singleton.

    `rank: float | Any | None`
    :   The type of the None singleton.

`IncidentTimestampsSearchData(**data: Any)`
:   Search result data for incident_timestamps entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   Unique identifier for the timestamp

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the timestamp

    `rank: float | None`
    :   Rank for ordering

`IncidentUpdate(**data: Any)`
:   An update posted to an incident
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `incident_id: str | Any | None`
    :   The type of the None singleton.

    `message: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `new_incident_status: airbyte_agent_sdk.connectors.incident_io.models.IncidentUpdateNewIncidentStatus | Any | None`
    :   The type of the None singleton.

    `new_severity: airbyte_agent_sdk.connectors.incident_io.models.IncidentUpdateNewSeverity | Any | None`
    :   The type of the None singleton.

    `updater: airbyte_agent_sdk.connectors.incident_io.models.IncidentUpdateUpdater | Any | None`
    :   The type of the None singleton.

`IncidentUpdateNewIncidentStatus(**data: Any)`
:   New incident status set by this update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `category: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `rank: float | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`IncidentUpdateNewSeverity(**data: Any)`
:   New severity set by this update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `rank: float | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`IncidentUpdateUpdater(**data: Any)`
:   Who made this update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.incident_io.models.IncidentUpdateUpdaterUser | Any | None`
    :   The type of the None singleton.

`IncidentUpdateUpdaterUser(**data: Any)`
:   Nested schema for IncidentUpdateUpdater.user
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `role: str | Any | None`
    :   The type of the None singleton.

    `slack_user_id: str | Any | None`
    :   The type of the None singleton.

`IncidentUpdatesListResultMeta(**data: Any)`
:   Metadata for incident_updates.Action.LIST operation
    
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

`IncidentUpdatesSearchData(**data: Any)`
:   Search result data for incident_updates entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When the update was created

    `id: str | None`
    :   Unique identifier for the incident update

    `incident_id: str | None`
    :   ID of the incident this update belongs to

    `message: str | None`
    :   Update message content

    `model_config`
    :   The type of the None singleton.

    `new_incident_status: dict[str, typing.Any] | None`
    :   New incident status set by this update

    `new_severity: dict[str, typing.Any] | None`
    :   New severity set by this update

    `updater: dict[str, typing.Any] | None`
    :   Who made this update

`IncidentsListResultMeta(**data: Any)`
:   Metadata for incidents.Action.LIST operation
    
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

`IncidentsSearchData(**data: Any)`
:   Search result data for incidents entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When the incident was created

    `creator: dict[str, typing.Any] | None`
    :   The user who created the incident

    `custom_field_entries: list[typing.Any] | None`
    :   Custom field values for the incident

    `duration_metrics: list[typing.Any] | None`
    :   Duration metrics associated with the incident

    `has_debrief: bool | None`
    :   Whether the incident has had a debrief

    `id: str | None`
    :   Unique identifier for the incident

    `incident_role_assignments: list[typing.Any] | None`
    :   Role assignments for the incident

    `incident_status: dict[str, typing.Any] | None`
    :   Current status of the incident

    `incident_timestamp_values: list[typing.Any] | None`
    :   Timestamp values for the incident

    `incident_type: dict[str, typing.Any] | None`
    :   Type of the incident

    `mode: str | None`
    :   Mode of the incident: standard, retrospective, test, or tutorial

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name/title of the incident

    `permalink: str | None`
    :   Link to the incident in the dashboard

    `reference: str | None`
    :   Human-readable reference (e.g. INC-123)

    `severity: dict[str, typing.Any] | None`
    :   Severity of the incident

    `slack_channel_id: str | None`
    :   Slack channel ID for the incident

    `slack_channel_name: str | None`
    :   Slack channel name for the incident

    `slack_team_id: str | None`
    :   Slack team/workspace ID

    `summary: str | None`
    :   Detailed summary of the incident

    `updated_at: str | None`
    :   When the incident was last updated

    `visibility: str | None`
    :   Whether the incident is public or private

    `workload_minutes_late: float | None`
    :   Minutes of workload classified as late

    `workload_minutes_sleeping: float | None`
    :   Minutes of workload classified as sleeping

    `workload_minutes_total: float | None`
    :   Total workload minutes

    `workload_minutes_working: float | None`
    :   Minutes of workload classified as working

`PaginationMeta(**data: Any)`
:   Cursor-based pagination metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `after: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `page_size: int | Any | None`
    :   The type of the None singleton.

`Schedule(**data: Any)`
:   An on-call schedule
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `config: airbyte_agent_sdk.connectors.incident_io.models.ScheduleConfig | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `current_shifts: list[airbyte_agent_sdk.connectors.incident_io.models.ScheduleCurrentShiftsItem] | Any | None`
    :   The type of the None singleton.

    `holidays_public_config: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `team_ids: list[str] | Any | None`
    :   The type of the None singleton.

    `timezone: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`ScheduleConfig(**data: Any)`
:   Schedule configuration with rotations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `rotations: list[airbyte_agent_sdk.connectors.incident_io.models.ScheduleConfigRotationsItem] | Any | None`
    :   The type of the None singleton.

`ScheduleConfigRotationsItem(**data: Any)`
:   Nested schema for ScheduleConfig.rotations_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `handover_start_at: str | Any | None`
    :   The type of the None singleton.

    `handovers: list[airbyte_agent_sdk.connectors.incident_io.models.ScheduleConfigRotationsItemHandoversItem] | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `layers: list[airbyte_agent_sdk.connectors.incident_io.models.ScheduleConfigRotationsItemLayersItem] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

`ScheduleConfigRotationsItemHandoversItem(**data: Any)`
:   Nested schema for ScheduleConfigRotationsItem.handovers_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `interval: float | Any | None`
    :   The type of the None singleton.

    `interval_type: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`ScheduleConfigRotationsItemLayersItem(**data: Any)`
:   Nested schema for ScheduleConfigRotationsItem.layers_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

`ScheduleCurrentShiftsItem(**data: Any)`
:   Nested schema for Schedule.current_shifts_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_at: str | Any | None`
    :   The type of the None singleton.

    `fingerprint: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rotation_id: str | Any | None`
    :   The type of the None singleton.

    `start_at: str | Any | None`
    :   The type of the None singleton.

`SchedulesListResultMeta(**data: Any)`
:   Metadata for schedules.Action.LIST operation
    
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

`SchedulesSearchData(**data: Any)`
:   Search result data for schedules entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `annotations: dict[str, typing.Any] | None`
    :   Annotations metadata

    `config: dict[str, typing.Any] | None`
    :   Schedule configuration with rotations

    `created_at: str | None`
    :   When the schedule was created

    `current_shifts: list[typing.Any] | None`
    :   Currently active shifts

    `id: str | None`
    :   Unique identifier for the schedule

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the schedule

    `timezone: str | None`
    :   Timezone for the schedule

    `updated_at: str | None`
    :   When the schedule was last updated

`SeveritiesSearchData(**data: Any)`
:   Search result data for severities entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When the severity was created

    `description: str | None`
    :   Description of the severity

    `id: str | None`
    :   Unique identifier for the severity

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the severity

    `rank: float | None`
    :   Rank for ordering

    `updated_at: str | None`
    :   When the severity was last updated

`Severity(**data: Any)`
:   A severity level for incidents
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `rank: float | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`User(**data: Any)`
:   A user in the incident.io organisation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `base_role: airbyte_agent_sdk.connectors.incident_io.models.UserBaseRole | Any | None`
    :   The type of the None singleton.

    `custom_roles: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `role: str | Any | None`
    :   The type of the None singleton.

    `slack_user_id: str | Any | None`
    :   The type of the None singleton.

`UserBaseRole(**data: Any)`
:   Base role assigned to the user
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

`UsersListResultMeta(**data: Any)`
:   Metadata for users.Action.LIST operation
    
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

`UsersSearchData(**data: Any)`
:   Search result data for users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `base_role: dict[str, typing.Any] | None`
    :   Base role assigned to the user

    `custom_roles: list[typing.Any] | None`
    :   Custom roles assigned to the user

    `email: str | None`
    :   Email address of the user

    `id: str | None`
    :   Unique identifier for the user

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Full name of the user

    `role: str | None`
    :   Deprecated role field

    `slack_user_id: str | None`
    :   Slack user ID