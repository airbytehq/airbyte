---
id: airbyte_agent_sdk-connectors-harvest-models
title: airbyte_agent_sdk.connectors.harvest.models
---

Module airbyte_agent_sdk.connectors.harvest.models
==================================================
Pydantic models for harvest connector.

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

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[ClientsSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[CompanySearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[ContactsSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[EstimateItemCategoriesSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[EstimatesSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[ExpenseCategoriesSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[ExpensesSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[InvoiceItemCategoriesSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[InvoicesSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[ProjectsSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[RolesSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[TaskAssignmentsSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[TasksSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[TimeEntriesSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[TimeProjectsSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[TimeTasksSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[UserAssignmentsSearchData]
    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[ClientsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`ClientsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CompanySearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`CompanySearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ContactsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`ContactsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[EstimateItemCategoriesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`EstimateItemCategoriesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[EstimatesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`EstimatesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ExpenseCategoriesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`ExpenseCategoriesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ExpensesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`ExpensesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[InvoiceItemCategoriesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`InvoiceItemCategoriesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[InvoicesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`InvoicesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ProjectsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`ProjectsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[RolesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`RolesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TaskAssignmentsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`TaskAssignmentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TasksSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`TasksSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TimeEntriesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`TimeEntriesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TimeProjectsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`TimeProjectsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TimeTasksSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`TimeTasksSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UserAssignmentsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`UserAssignmentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.harvest.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`Client(**data: Any)`
:   A Harvest client
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `is_active: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `statement_key: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`ClientsList(**data: Any)`
:   Paginated list of clients
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `clients: list[airbyte_agent_sdk.connectors.harvest.models.Client] | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.harvest.models.PaginationLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: int | Any | None`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `previous_page: int | Any | None`
    :   The type of the None singleton.

    `total_entries: int | Any`
    :   The type of the None singleton.

    `total_pages: int | Any`
    :   The type of the None singleton.

`ClientsListResultMeta(**data: Any)`
:   Metadata for clients.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any | None`
    :   The type of the None singleton.

`ClientsSearchData(**data: Any)`
:   Search result data for clients entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: str | None`
    :   The client's postal address

    `created_at: str | None`
    :   When the client record was created

    `currency: str | None`
    :   The currency used by the client

    `id: int | None`
    :   Unique identifier for the client

    `is_active: bool | None`
    :   Whether the client is active

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The client's name

    `updated_at: str | None`
    :   When the client record was last updated

`Company(**data: Any)`
:   The Harvest company/account information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `approval_feature: bool | Any | None`
    :   The type of the None singleton.

    `base_uri: str | Any | None`
    :   The type of the None singleton.

    `clock: str | Any | None`
    :   The type of the None singleton.

    `color_scheme: str | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `currency_code_display: str | Any | None`
    :   The type of the None singleton.

    `currency_symbol_display: str | Any | None`
    :   The type of the None singleton.

    `date_format: str | Any | None`
    :   The type of the None singleton.

    `day_entry_notes_required: bool | Any | None`
    :   The type of the None singleton.

    `decimal_symbol: str | Any | None`
    :   The type of the None singleton.

    `estimate_feature: bool | Any | None`
    :   The type of the None singleton.

    `expense_feature: bool | Any | None`
    :   The type of the None singleton.

    `full_domain: str | Any | None`
    :   The type of the None singleton.

    `invoice_feature: bool | Any | None`
    :   The type of the None singleton.

    `is_active: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `plan_type: str | Any | None`
    :   The type of the None singleton.

    `saml_sign_in_required: bool | Any | None`
    :   The type of the None singleton.

    `team_feature: bool | Any | None`
    :   The type of the None singleton.

    `thousands_separator: str | Any | None`
    :   The type of the None singleton.

    `time_format: str | Any | None`
    :   The type of the None singleton.

    `wants_timestamp_timers: bool | Any | None`
    :   The type of the None singleton.

    `week_start_day: str | Any | None`
    :   The type of the None singleton.

    `weekly_capacity: int | Any | None`
    :   The type of the None singleton.

`CompanySearchData(**data: Any)`
:   Search result data for company entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `base_uri: str | None`
    :   The base URI

    `currency: str | None`
    :   Currency used by the company

    `full_domain: str | None`
    :   The full domain name

    `is_active: bool | None`
    :   Whether the company is active

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the company

    `plan_type: str | None`
    :   The plan type

    `weekly_capacity: int | None`
    :   Weekly capacity in seconds

`Contact(**data: Any)`
:   A Harvest contact associated with a client
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client: airbyte_agent_sdk.connectors.harvest.models.ContactClient | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `fax: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `phone_mobile: str | Any | None`
    :   The type of the None singleton.

    `phone_office: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`ContactClient(**data: Any)`
:   The client associated with this contact
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   Client ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   Client name

`ContactsList(**data: Any)`
:   Paginated list of contacts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `contacts: list[airbyte_agent_sdk.connectors.harvest.models.Contact] | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.harvest.models.PaginationLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: int | Any | None`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `previous_page: int | Any | None`
    :   The type of the None singleton.

    `total_entries: int | Any`
    :   The type of the None singleton.

    `total_pages: int | Any`
    :   The type of the None singleton.

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

    `next_link: str | Any | None`
    :   The type of the None singleton.

`ContactsSearchData(**data: Any)`
:   Search result data for contacts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client: dict[str, typing.Any] | None`
    :   Client associated with the contact

    `created_at: str | None`
    :   When created

    `email: str | None`
    :   Email address

    `first_name: str | None`
    :   First name

    `id: int | None`
    :   Unique identifier

    `last_name: str | None`
    :   Last name

    `model_config`
    :   The type of the None singleton.

    `title: str | None`
    :   Job title

    `updated_at: str | None`
    :   When last updated

`Estimate(**data: Any)`
:   A Harvest estimate
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `accepted_at: str | Any | None`
    :   The type of the None singleton.

    `amount: float | Any | None`
    :   The type of the None singleton.

    `client: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `client_key: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `creator: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `declined_at: str | Any | None`
    :   The type of the None singleton.

    `discount: float | Any | None`
    :   The type of the None singleton.

    `discount_amount: float | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `issue_date: str | Any | None`
    :   The type of the None singleton.

    `line_items: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `notes: str | Any | None`
    :   The type of the None singleton.

    `number: str | Any | None`
    :   The type of the None singleton.

    `purchase_order: str | Any | None`
    :   The type of the None singleton.

    `sent_at: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

    `subject: str | Any | None`
    :   The type of the None singleton.

    `tax: float | Any | None`
    :   The type of the None singleton.

    `tax2: float | Any | None`
    :   The type of the None singleton.

    `tax2_amount: float | Any | None`
    :   The type of the None singleton.

    `tax_amount: float | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`EstimateItemCategoriesList(**data: Any)`
:   Paginated list of estimate item categories
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `estimate_item_categories: list[airbyte_agent_sdk.connectors.harvest.models.EstimateItemCategory] | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.harvest.models.PaginationLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: int | Any | None`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `previous_page: int | Any | None`
    :   The type of the None singleton.

    `total_entries: int | Any`
    :   The type of the None singleton.

    `total_pages: int | Any`
    :   The type of the None singleton.

`EstimateItemCategoriesListResultMeta(**data: Any)`
:   Metadata for estimate_item_categories.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any | None`
    :   The type of the None singleton.

`EstimateItemCategoriesSearchData(**data: Any)`
:   Search result data for estimate_item_categories entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When created

    `id: int | None`
    :   Unique identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Category name

    `updated_at: str | None`
    :   When last updated

`EstimateItemCategory(**data: Any)`
:   A Harvest estimate item category
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`EstimatesList(**data: Any)`
:   Paginated list of estimates
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `estimates: list[airbyte_agent_sdk.connectors.harvest.models.Estimate] | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.harvest.models.PaginationLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: int | Any | None`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `previous_page: int | Any | None`
    :   The type of the None singleton.

    `total_entries: int | Any`
    :   The type of the None singleton.

    `total_pages: int | Any`
    :   The type of the None singleton.

`EstimatesListResultMeta(**data: Any)`
:   Metadata for estimates.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any | None`
    :   The type of the None singleton.

`EstimatesSearchData(**data: Any)`
:   Search result data for estimates entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: float | None`
    :   Total amount

    `client: dict[str, typing.Any] | None`
    :   Client details

    `created_at: str | None`
    :   When created

    `currency: str | None`
    :   Currency

    `id: int | None`
    :   Unique identifier

    `issue_date: str | None`
    :   Issue date

    `model_config`
    :   The type of the None singleton.

    `number: str | None`
    :   Estimate number

    `state: str | None`
    :   Current state

    `subject: str | None`
    :   Subject

    `updated_at: str | None`
    :   When last updated

`Expense(**data: Any)`
:   A Harvest expense
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `approval_status: str | Any | None`
    :   The type of the None singleton.

    `billable: bool | Any | None`
    :   The type of the None singleton.

    `client: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `expense_category: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `invoice: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `is_billed: bool | Any | None`
    :   The type of the None singleton.

    `is_closed: bool | Any | None`
    :   The type of the None singleton.

    `is_explicitly_locked: bool | Any | None`
    :   The type of the None singleton.

    `is_locked: bool | Any | None`
    :   The type of the None singleton.

    `locked_reason: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `notes: str | Any | None`
    :   The type of the None singleton.

    `project: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `receipt: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `spent_date: str | Any | None`
    :   The type of the None singleton.

    `total_cost: float | Any | None`
    :   The type of the None singleton.

    `units: float | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `user: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `user_assignment: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

`ExpenseCategoriesList(**data: Any)`
:   Paginated list of expense categories
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expense_categories: list[airbyte_agent_sdk.connectors.harvest.models.ExpenseCategory] | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.harvest.models.PaginationLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: int | Any | None`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `previous_page: int | Any | None`
    :   The type of the None singleton.

    `total_entries: int | Any`
    :   The type of the None singleton.

    `total_pages: int | Any`
    :   The type of the None singleton.

`ExpenseCategoriesListResultMeta(**data: Any)`
:   Metadata for expense_categories.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any | None`
    :   The type of the None singleton.

`ExpenseCategoriesSearchData(**data: Any)`
:   Search result data for expense_categories entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When created

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Category name

    `unit_name: str | None`
    :   Unit name

    `unit_price: float | None`
    :   Unit price

    `updated_at: str | None`
    :   When last updated

`ExpenseCategory(**data: Any)`
:   A Harvest expense category
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `is_active: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `unit_name: str | Any | None`
    :   The type of the None singleton.

    `unit_price: float | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`ExpensesList(**data: Any)`
:   Paginated list of expenses
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expenses: list[airbyte_agent_sdk.connectors.harvest.models.Expense] | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.harvest.models.PaginationLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: int | Any | None`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `previous_page: int | Any | None`
    :   The type of the None singleton.

    `total_entries: int | Any`
    :   The type of the None singleton.

    `total_pages: int | Any`
    :   The type of the None singleton.

`ExpensesListResultMeta(**data: Any)`
:   Metadata for expenses.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any | None`
    :   The type of the None singleton.

`ExpensesSearchData(**data: Any)`
:   Search result data for expenses entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `billable: bool | None`
    :   Whether billable

    `client: dict[str, typing.Any] | None`
    :   Associated client

    `created_at: str | None`
    :   When created

    `expense_category: dict[str, typing.Any] | None`
    :   Expense category

    `id: int | None`
    :   Unique identifier

    `is_billed: bool | None`
    :   Whether billed

    `model_config`
    :   The type of the None singleton.

    `notes: str | None`
    :   Notes

    `project: dict[str, typing.Any] | None`
    :   Associated project

    `spent_date: str | None`
    :   Date spent

    `total_cost: float | None`
    :   Total cost

    `updated_at: str | None`
    :   When last updated

    `user: dict[str, typing.Any] | None`
    :   Associated user

`HarvestCheckResult(**data: Any)`
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

`HarvestExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

`HarvestExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[Client], ClientsListResultMeta]
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[Contact], ContactsListResultMeta]
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[EstimateItemCategory], EstimateItemCategoriesListResultMeta]
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[Estimate], EstimatesListResultMeta]
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[ExpenseCategory], ExpenseCategoriesListResultMeta]
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[Expense], ExpensesListResultMeta]
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[InvoiceItemCategory], InvoiceItemCategoriesListResultMeta]
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[Invoice], InvoicesListResultMeta]
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[Project], ProjectsListResultMeta]
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[Role], RolesListResultMeta]
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[TaskAssignment], TaskAssignmentsListResultMeta]
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[Task], TasksListResultMeta]
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[TimeEntry], TimeEntriesListResultMeta]
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[TimeProject], TimeProjectsListResultMeta]
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[TimeTask], TimeTasksListResultMeta]
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[UserAssignment], UserAssignmentsListResultMeta]
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta[list[User], UsersListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`HarvestExecuteResultWithMeta[list[Client], ClientsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`ClientsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HarvestExecuteResultWithMeta[list[Contact], ContactsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`ContactsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HarvestExecuteResultWithMeta[list[EstimateItemCategory], EstimateItemCategoriesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`EstimateItemCategoriesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HarvestExecuteResultWithMeta[list[Estimate], EstimatesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`EstimatesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HarvestExecuteResultWithMeta[list[ExpenseCategory], ExpenseCategoriesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`ExpenseCategoriesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HarvestExecuteResultWithMeta[list[Expense], ExpensesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`ExpensesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HarvestExecuteResultWithMeta[list[InvoiceItemCategory], InvoiceItemCategoriesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`InvoiceItemCategoriesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HarvestExecuteResultWithMeta[list[Invoice], InvoicesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`InvoicesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HarvestExecuteResultWithMeta[list[Project], ProjectsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`ProjectsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HarvestExecuteResultWithMeta[list[Role], RolesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`RolesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HarvestExecuteResultWithMeta[list[TaskAssignment], TaskAssignmentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`TaskAssignmentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HarvestExecuteResultWithMeta[list[Task], TasksListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`TasksListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HarvestExecuteResultWithMeta[list[TimeEntry], TimeEntriesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`TimeEntriesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HarvestExecuteResultWithMeta[list[TimeProject], TimeProjectsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`TimeProjectsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HarvestExecuteResultWithMeta[list[TimeTask], TimeTasksListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`TimeTasksListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HarvestExecuteResultWithMeta[list[UserAssignment], UserAssignmentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`UserAssignmentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HarvestExecuteResultWithMeta[list[User], UsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
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

    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.harvest.models.HarvestExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`HarvestOauth20AuthConfig(**data: Any)`
:   OAuth 2.0
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str`
    :   Your Harvest account ID

    `client_id: str`
    :   Client ID

    `client_secret: str`
    :   Client Secret

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   Your Harvest OAuth2 refresh token

`HarvestPersonalAccessTokenAuthConfig(**data: Any)`
:   Personal Access Token
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str`
    :   Your Harvest account ID

    `model_config`
    :   The type of the None singleton.

    `token: str`
    :   Your Harvest personal access token

`HarvestReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Harvest.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `replication_start_date: str`
    :   UTC date and time in YYYY-MM-DDTHH:mm:ssZ format from which to start replicating data. Data before this date will not be replicated.

`Invoice(**data: Any)`
:   A Harvest invoice
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: float | Any | None`
    :   The type of the None singleton.

    `client: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `client_key: str | Any | None`
    :   The type of the None singleton.

    `closed_at: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `creator: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `discount: float | Any | None`
    :   The type of the None singleton.

    `discount_amount: float | Any | None`
    :   The type of the None singleton.

    `due_amount: float | Any | None`
    :   The type of the None singleton.

    `due_date: str | Any | None`
    :   The type of the None singleton.

    `estimate: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `issue_date: str | Any | None`
    :   The type of the None singleton.

    `line_items: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `notes: str | Any | None`
    :   The type of the None singleton.

    `number: str | Any | None`
    :   The type of the None singleton.

    `paid_at: str | Any | None`
    :   The type of the None singleton.

    `paid_date: str | Any | None`
    :   The type of the None singleton.

    `payment_options: list[str] | Any | None`
    :   The type of the None singleton.

    `payment_term: str | Any | None`
    :   The type of the None singleton.

    `period_end: str | Any | None`
    :   The type of the None singleton.

    `period_start: str | Any | None`
    :   The type of the None singleton.

    `purchase_order: str | Any | None`
    :   The type of the None singleton.

    `recurring_invoice_id: int | Any | None`
    :   The type of the None singleton.

    `retainer: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `sent_at: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

    `subject: str | Any | None`
    :   The type of the None singleton.

    `tax: float | Any | None`
    :   The type of the None singleton.

    `tax2: float | Any | None`
    :   The type of the None singleton.

    `tax2_amount: float | Any | None`
    :   The type of the None singleton.

    `tax_amount: float | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`InvoiceItemCategoriesList(**data: Any)`
:   Paginated list of invoice item categories
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `invoice_item_categories: list[airbyte_agent_sdk.connectors.harvest.models.InvoiceItemCategory] | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.harvest.models.PaginationLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: int | Any | None`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `previous_page: int | Any | None`
    :   The type of the None singleton.

    `total_entries: int | Any`
    :   The type of the None singleton.

    `total_pages: int | Any`
    :   The type of the None singleton.

`InvoiceItemCategoriesListResultMeta(**data: Any)`
:   Metadata for invoice_item_categories.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any | None`
    :   The type of the None singleton.

`InvoiceItemCategoriesSearchData(**data: Any)`
:   Search result data for invoice_item_categories entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When created

    `id: int | None`
    :   Unique identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Category name

    `updated_at: str | None`
    :   When last updated

    `use_as_expense: bool | None`
    :   Whether used as expense type

    `use_as_service: bool | None`
    :   Whether used as service type

`InvoiceItemCategory(**data: Any)`
:   A Harvest invoice item category
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `use_as_expense: bool | Any | None`
    :   The type of the None singleton.

    `use_as_service: bool | Any | None`
    :   The type of the None singleton.

`InvoicesList(**data: Any)`
:   Paginated list of invoices
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `invoices: list[airbyte_agent_sdk.connectors.harvest.models.Invoice] | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.harvest.models.PaginationLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: int | Any | None`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `previous_page: int | Any | None`
    :   The type of the None singleton.

    `total_entries: int | Any`
    :   The type of the None singleton.

    `total_pages: int | Any`
    :   The type of the None singleton.

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

    `next_link: str | Any | None`
    :   The type of the None singleton.

`InvoicesSearchData(**data: Any)`
:   Search result data for invoices entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `amount: float | None`
    :   Total amount

    `client: dict[str, typing.Any] | None`
    :   Client details

    `created_at: str | None`
    :   When created

    `currency: str | None`
    :   Currency

    `due_amount: float | None`
    :   Amount due

    `due_date: str | None`
    :   Due date

    `id: int | None`
    :   Unique identifier

    `issue_date: str | None`
    :   Issue date

    `model_config`
    :   The type of the None singleton.

    `number: str | None`
    :   Invoice number

    `state: str | None`
    :   Current state

    `subject: str | None`
    :   Subject

    `updated_at: str | None`
    :   When last updated

`PaginationLinks(**data: Any)`
:   Pagination links for navigating result pages
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `first: str | Any | None`
    :   The type of the None singleton.

    `last: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

    `previous: str | Any | None`
    :   The type of the None singleton.

`Project(**data: Any)`
:   A Harvest project
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bill_by: str | Any | None`
    :   The type of the None singleton.

    `budget: float | Any | None`
    :   The type of the None singleton.

    `budget_by: str | Any | None`
    :   The type of the None singleton.

    `budget_is_monthly: bool | Any | None`
    :   The type of the None singleton.

    `client: airbyte_agent_sdk.connectors.harvest.models.ProjectClient | Any | None`
    :   The type of the None singleton.

    `code: str | Any | None`
    :   The type of the None singleton.

    `cost_budget: float | Any | None`
    :   The type of the None singleton.

    `cost_budget_include_expenses: bool | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `ends_on: str | Any | None`
    :   The type of the None singleton.

    `fee: float | Any | None`
    :   The type of the None singleton.

    `hourly_rate: float | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `is_active: bool | Any | None`
    :   The type of the None singleton.

    `is_billable: bool | Any | None`
    :   The type of the None singleton.

    `is_fixed_fee: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `notes: str | Any | None`
    :   The type of the None singleton.

    `notify_when_over_budget: bool | Any | None`
    :   The type of the None singleton.

    `over_budget_notification_date: str | Any | None`
    :   The type of the None singleton.

    `over_budget_notification_percentage: float | Any | None`
    :   The type of the None singleton.

    `show_budget_to_all: bool | Any | None`
    :   The type of the None singleton.

    `starts_on: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`ProjectClient(**data: Any)`
:   The client associated with the project
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currency: str | Any | None`
    :   Client currency

    `id: int | Any | None`
    :   Client ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   Client name

`ProjectsList(**data: Any)`
:   Paginated list of projects
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: airbyte_agent_sdk.connectors.harvest.models.PaginationLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: int | Any | None`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `previous_page: int | Any | None`
    :   The type of the None singleton.

    `projects: list[airbyte_agent_sdk.connectors.harvest.models.Project] | Any`
    :   The type of the None singleton.

    `total_entries: int | Any`
    :   The type of the None singleton.

    `total_pages: int | Any`
    :   The type of the None singleton.

`ProjectsListResultMeta(**data: Any)`
:   Metadata for projects.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any | None`
    :   The type of the None singleton.

`ProjectsSearchData(**data: Any)`
:   Search result data for projects entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `budget: float | None`
    :   Budget amount

    `client: dict[str, typing.Any] | None`
    :   Client details

    `code: str | None`
    :   Project code

    `created_at: str | None`
    :   When created

    `hourly_rate: float | None`
    :   Hourly rate

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `is_billable: bool | None`
    :   Whether billable

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Project name

    `starts_on: str | None`
    :   Start date

    `updated_at: str | None`
    :   When last updated

`Role(**data: Any)`
:   A Harvest role
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `user_ids: list[int] | Any | None`
    :   The type of the None singleton.

`RolesList(**data: Any)`
:   Paginated list of roles
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: airbyte_agent_sdk.connectors.harvest.models.PaginationLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: int | Any | None`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `previous_page: int | Any | None`
    :   The type of the None singleton.

    `roles: list[airbyte_agent_sdk.connectors.harvest.models.Role] | Any`
    :   The type of the None singleton.

    `total_entries: int | Any`
    :   The type of the None singleton.

    `total_pages: int | Any`
    :   The type of the None singleton.

`RolesListResultMeta(**data: Any)`
:   Metadata for roles.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any | None`
    :   The type of the None singleton.

`RolesSearchData(**data: Any)`
:   Search result data for roles entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   When created

    `id: int | None`
    :   Unique identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Role name

    `updated_at: str | None`
    :   When last updated

    `user_ids: list[typing.Any] | None`
    :   User IDs with this role

`Task(**data: Any)`
:   A Harvest task
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `billable_by_default: bool | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `default_hourly_rate: float | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `is_active: bool | Any | None`
    :   The type of the None singleton.

    `is_default: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`TaskAssignment(**data: Any)`
:   A Harvest task assignment linking a task to a project
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `billable: bool | Any | None`
    :   The type of the None singleton.

    `budget: float | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `hourly_rate: float | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `is_active: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `project: airbyte_agent_sdk.connectors.harvest.models.TaskAssignmentProject | Any | None`
    :   The type of the None singleton.

    `task: airbyte_agent_sdk.connectors.harvest.models.TaskAssignmentTask | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

`TaskAssignmentProject(**data: Any)`
:   The project associated with the assignment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | Any | None`
    :   Project code

    `id: int | Any | None`
    :   Project ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   Project name

`TaskAssignmentTask(**data: Any)`
:   The task associated with the assignment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   Task ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   Task name

`TaskAssignmentsList(**data: Any)`
:   Paginated list of task assignments
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: airbyte_agent_sdk.connectors.harvest.models.PaginationLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: int | Any | None`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `previous_page: int | Any | None`
    :   The type of the None singleton.

    `task_assignments: list[airbyte_agent_sdk.connectors.harvest.models.TaskAssignment] | Any`
    :   The type of the None singleton.

    `total_entries: int | Any`
    :   The type of the None singleton.

    `total_pages: int | Any`
    :   The type of the None singleton.

`TaskAssignmentsListResultMeta(**data: Any)`
:   Metadata for task_assignments.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any | None`
    :   The type of the None singleton.

`TaskAssignmentsSearchData(**data: Any)`
:   Search result data for task_assignments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `billable: bool | None`
    :   Whether billable

    `created_at: str | None`
    :   When created

    `hourly_rate: float | None`
    :   Hourly rate

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `model_config`
    :   The type of the None singleton.

    `project: dict[str, typing.Any] | None`
    :   Associated project

    `task: dict[str, typing.Any] | None`
    :   Associated task

    `updated_at: str | None`
    :   When last updated

`TasksList(**data: Any)`
:   Paginated list of tasks
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: airbyte_agent_sdk.connectors.harvest.models.PaginationLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: int | Any | None`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `previous_page: int | Any | None`
    :   The type of the None singleton.

    `tasks: list[airbyte_agent_sdk.connectors.harvest.models.Task] | Any`
    :   The type of the None singleton.

    `total_entries: int | Any`
    :   The type of the None singleton.

    `total_pages: int | Any`
    :   The type of the None singleton.

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

    `next_link: str | Any | None`
    :   The type of the None singleton.

`TasksSearchData(**data: Any)`
:   Search result data for tasks entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `billable_by_default: bool | None`
    :   Whether billable by default

    `created_at: str | None`
    :   When created

    `default_hourly_rate: float | None`
    :   Default hourly rate

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Task name

    `updated_at: str | None`
    :   When last updated

`TimeEntriesList(**data: Any)`
:   Paginated list of time entries
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: airbyte_agent_sdk.connectors.harvest.models.PaginationLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: int | Any | None`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `previous_page: int | Any | None`
    :   The type of the None singleton.

    `time_entries: list[airbyte_agent_sdk.connectors.harvest.models.TimeEntry] | Any`
    :   The type of the None singleton.

    `total_entries: int | Any`
    :   The type of the None singleton.

    `total_pages: int | Any`
    :   The type of the None singleton.

`TimeEntriesListResultMeta(**data: Any)`
:   Metadata for time_entries.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any | None`
    :   The type of the None singleton.

`TimeEntriesSearchData(**data: Any)`
:   Search result data for time_entries entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `billable: bool | None`
    :   Whether billable

    `client: dict[str, typing.Any] | None`
    :   Associated client

    `created_at: str | None`
    :   When created

    `hours: float | None`
    :   Hours logged

    `id: int | None`
    :   Unique identifier

    `is_billed: bool | None`
    :   Whether billed

    `model_config`
    :   The type of the None singleton.

    `notes: str | None`
    :   Notes

    `project: dict[str, typing.Any] | None`
    :   Associated project

    `spent_date: str | None`
    :   Date time was spent

    `task: dict[str, typing.Any] | None`
    :   Associated task

    `updated_at: str | None`
    :   When last updated

    `user: dict[str, typing.Any] | None`
    :   Associated user

`TimeEntry(**data: Any)`
:   A Harvest time entry
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `approval_status: str | Any | None`
    :   The type of the None singleton.

    `billable: bool | Any | None`
    :   The type of the None singleton.

    `billable_rate: float | Any | None`
    :   The type of the None singleton.

    `budgeted: bool | Any | None`
    :   The type of the None singleton.

    `client: airbyte_agent_sdk.connectors.harvest.models.TimeEntryClient | Any | None`
    :   The type of the None singleton.

    `cost_rate: float | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `ended_time: str | Any | None`
    :   The type of the None singleton.

    `external_reference: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `hours: float | Any | None`
    :   The type of the None singleton.

    `hours_without_timer: float | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `invoice: airbyte_agent_sdk.connectors.harvest.models.TimeEntryInvoice | Any | None`
    :   The type of the None singleton.

    `is_billed: bool | Any | None`
    :   The type of the None singleton.

    `is_closed: bool | Any | None`
    :   The type of the None singleton.

    `is_explicitly_locked: bool | Any | None`
    :   The type of the None singleton.

    `is_locked: bool | Any | None`
    :   The type of the None singleton.

    `is_running: bool | Any | None`
    :   The type of the None singleton.

    `locked_reason: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `notes: str | Any | None`
    :   The type of the None singleton.

    `project: airbyte_agent_sdk.connectors.harvest.models.TimeEntryProject | Any | None`
    :   The type of the None singleton.

    `rounded_hours: float | Any | None`
    :   The type of the None singleton.

    `spent_date: str | Any | None`
    :   The type of the None singleton.

    `started_time: str | Any | None`
    :   The type of the None singleton.

    `task: airbyte_agent_sdk.connectors.harvest.models.TimeEntryTask | Any | None`
    :   The type of the None singleton.

    `task_assignment: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `timer_started_at: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.harvest.models.TimeEntryUser | Any | None`
    :   The type of the None singleton.

    `user_assignment: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

`TimeEntryClient(**data: Any)`
:   The client associated with the time entry
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   Client ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   Client name

`TimeEntryInvoice(**data: Any)`
:   The invoice associated with the time entry
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   Invoice ID

    `model_config`
    :   The type of the None singleton.

    `number: str | Any | None`
    :   Invoice number

`TimeEntryProject(**data: Any)`
:   The project associated with the time entry
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   Project ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   Project name

`TimeEntryTask(**data: Any)`
:   The task associated with the time entry
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   Task ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   Task name

`TimeEntryUser(**data: Any)`
:   The user associated with the time entry
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   User ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   User name

`TimeProject(**data: Any)`
:   A time report entry grouped by project
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `billable_amount: float | Any | None`
    :   The type of the None singleton.

    `billable_hours: float | Any | None`
    :   The type of the None singleton.

    `client_id: int | Any | None`
    :   The type of the None singleton.

    `client_name: str | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `project_id: int | Any | None`
    :   The type of the None singleton.

    `project_name: str | Any | None`
    :   The type of the None singleton.

    `total_hours: float | Any | None`
    :   The type of the None singleton.

`TimeProjectsList(**data: Any)`
:   Paginated list of time report entries by project
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: airbyte_agent_sdk.connectors.harvest.models.PaginationLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: int | Any | None`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `previous_page: int | Any | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.harvest.models.TimeProject] | Any`
    :   The type of the None singleton.

    `total_entries: int | Any`
    :   The type of the None singleton.

    `total_pages: int | Any`
    :   The type of the None singleton.

`TimeProjectsListResultMeta(**data: Any)`
:   Metadata for time_projects.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any | None`
    :   The type of the None singleton.

`TimeProjectsSearchData(**data: Any)`
:   Search result data for time_projects entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `billable_amount: float | None`
    :   Total billable amount

    `billable_hours: float | None`
    :   Number of billable hours

    `client_id: int | None`
    :   Client identifier

    `client_name: str | None`
    :   Client name

    `currency: str | None`
    :   Currency code

    `model_config`
    :   The type of the None singleton.

    `project_id: int | None`
    :   Project identifier

    `project_name: str | None`
    :   Project name

    `total_hours: float | None`
    :   Total hours spent

`TimeTask(**data: Any)`
:   A time report entry grouped by task
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `billable_amount: float | Any | None`
    :   The type of the None singleton.

    `billable_hours: float | Any | None`
    :   The type of the None singleton.

    `currency: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `task_id: int | Any | None`
    :   The type of the None singleton.

    `task_name: str | Any | None`
    :   The type of the None singleton.

    `total_hours: float | Any | None`
    :   The type of the None singleton.

`TimeTasksList(**data: Any)`
:   Paginated list of time report entries by task
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: airbyte_agent_sdk.connectors.harvest.models.PaginationLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: int | Any | None`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `previous_page: int | Any | None`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.harvest.models.TimeTask] | Any`
    :   The type of the None singleton.

    `total_entries: int | Any`
    :   The type of the None singleton.

    `total_pages: int | Any`
    :   The type of the None singleton.

`TimeTasksListResultMeta(**data: Any)`
:   Metadata for time_tasks.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any | None`
    :   The type of the None singleton.

`TimeTasksSearchData(**data: Any)`
:   Search result data for time_tasks entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `billable_amount: float | None`
    :   Total billable amount

    `billable_hours: float | None`
    :   Number of billable hours

    `currency: str | None`
    :   Currency code

    `model_config`
    :   The type of the None singleton.

    `task_id: int | None`
    :   Task identifier

    `task_name: str | None`
    :   Task name

    `total_hours: float | None`
    :   Total hours spent

`User(**data: Any)`
:   A Harvest user
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_roles: list[str] | Any | None`
    :   The type of the None singleton.

    `avatar_url: str | Any | None`
    :   The type of the None singleton.

    `calendar_integration_enabled: bool | Any | None`
    :   The type of the None singleton.

    `calendar_integration_source: str | Any | None`
    :   The type of the None singleton.

    `can_create_projects: bool | Any | None`
    :   The type of the None singleton.

    `cost_rate: float | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `default_hourly_rate: float | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `employee_id: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `has_access_to_all_future_projects: bool | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `is_active: bool | Any | None`
    :   The type of the None singleton.

    `is_contractor: bool | Any | None`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `permissions_claims: list[str] | Any | None`
    :   The type of the None singleton.

    `roles: list[str] | Any | None`
    :   The type of the None singleton.

    `telephone: str | Any | None`
    :   The type of the None singleton.

    `timezone: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `weekly_capacity: int | Any | None`
    :   The type of the None singleton.

`UserAssignment(**data: Any)`
:   A Harvest user assignment linking a user to a project
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `budget: float | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `hourly_rate: float | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `is_active: bool | Any | None`
    :   The type of the None singleton.

    `is_project_manager: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `project: airbyte_agent_sdk.connectors.harvest.models.UserAssignmentProject | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `use_default_rates: bool | Any | None`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.harvest.models.UserAssignmentUser | Any | None`
    :   The type of the None singleton.

`UserAssignmentProject(**data: Any)`
:   The project associated with the assignment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `code: str | Any | None`
    :   Project code

    `id: int | Any | None`
    :   Project ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   Project name

`UserAssignmentUser(**data: Any)`
:   The user associated with the assignment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   User ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   User name

`UserAssignmentsList(**data: Any)`
:   Paginated list of user assignments
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: airbyte_agent_sdk.connectors.harvest.models.PaginationLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: int | Any | None`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `previous_page: int | Any | None`
    :   The type of the None singleton.

    `total_entries: int | Any`
    :   The type of the None singleton.

    `total_pages: int | Any`
    :   The type of the None singleton.

    `user_assignments: list[airbyte_agent_sdk.connectors.harvest.models.UserAssignment] | Any`
    :   The type of the None singleton.

`UserAssignmentsListResultMeta(**data: Any)`
:   Metadata for user_assignments.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_link: str | Any | None`
    :   The type of the None singleton.

`UserAssignmentsSearchData(**data: Any)`
:   Search result data for user_assignments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `budget: float | None`
    :   Budget

    `created_at: str | None`
    :   When created

    `hourly_rate: float | None`
    :   Hourly rate

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `is_project_manager: bool | None`
    :   Whether project manager

    `model_config`
    :   The type of the None singleton.

    `project: dict[str, typing.Any] | None`
    :   Associated project

    `updated_at: str | None`
    :   When last updated

    `user: dict[str, typing.Any] | None`
    :   Associated user

`UsersList(**data: Any)`
:   Paginated list of users
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: airbyte_agent_sdk.connectors.harvest.models.PaginationLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: int | Any | None`
    :   The type of the None singleton.

    `page: int | Any`
    :   The type of the None singleton.

    `per_page: int | Any`
    :   The type of the None singleton.

    `previous_page: int | Any | None`
    :   The type of the None singleton.

    `total_entries: int | Any`
    :   The type of the None singleton.

    `total_pages: int | Any`
    :   The type of the None singleton.

    `users: list[airbyte_agent_sdk.connectors.harvest.models.User] | Any`
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

    `next_link: str | Any | None`
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

    `avatar_url: str | None`
    :   Avatar URL

    `cost_rate: float | None`
    :   Cost rate

    `created_at: str | None`
    :   When created

    `default_hourly_rate: float | None`
    :   Default hourly rate

    `email: str | None`
    :   Email address

    `first_name: str | None`
    :   First name

    `id: int | None`
    :   Unique identifier

    `is_active: bool | None`
    :   Whether active

    `is_contractor: bool | None`
    :   Whether contractor

    `last_name: str | None`
    :   Last name

    `model_config`
    :   The type of the None singleton.

    `roles: list[typing.Any] | None`
    :   Assigned roles

    `telephone: str | None`
    :   Phone number

    `timezone: str | None`
    :   Timezone

    `updated_at: str | None`
    :   When last updated

    `weekly_capacity: int | None`
    :   Weekly capacity in seconds