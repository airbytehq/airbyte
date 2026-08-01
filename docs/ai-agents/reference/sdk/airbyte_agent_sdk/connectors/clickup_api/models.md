---
id: airbyte_agent_sdk-connectors-clickup_api-models
title: airbyte_agent_sdk.connectors.clickup_api.models
---

Module airbyte_agent_sdk.connectors.clickup_api.models
======================================================
Pydantic models for clickup-api connector.

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

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[CommentsSearchData]
    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[FoldersSearchData]
    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[GoalsSearchData]
    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[ListsSearchData]
    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[SpacesSearchData]
    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[TasksSearchData]
    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[TeamsSearchData]
    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[TimeTrackingSearchData]
    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult[UserSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[CommentsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CommentsSearchResult"></a>

`CommentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[FoldersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="FoldersSearchResult"></a>

`FoldersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[GoalsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="GoalsSearchResult"></a>

`GoalsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ListsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ListsSearchResult"></a>

`ListsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SpacesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SpacesSearchResult"></a>

`SpacesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TasksSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TeamsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TeamsSearchResult"></a>

`TeamsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TimeTrackingSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TimeTrackingSearchResult"></a>

`TimeTrackingSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UserSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UserSearchResult"></a>

`UserSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ClickupApiAuthConfig"></a>

`ClickupApiAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your ClickUp personal API token

    `model_config`
    :   The type of the None singleton.

<a id="ClickupApiCheckResult"></a>

`ClickupApiCheckResult(**data: Any)`
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

<a id="ClickupApiExecuteResult"></a>

`ClickupApiExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[Comment]]
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[Folder]]
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[Goal]]
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[List]]
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[Member]]
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[Space]]
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[Team]]
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[TimeEntry]]
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult[list[View]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="ClickupApiExecuteResultWithMeta"></a>

`ClickupApiExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResultWithMeta[list[Doc], DocsListResultMeta]
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResultWithMeta[list[Task], TasksApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResultWithMeta[list[Task], TasksListResultMeta]
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResultWithMeta[list[Task], ViewTasksListResultMeta]

    ### Class variables

    `meta: ~S | None`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`ClickupApiExecuteResultWithMeta[list[Doc], DocsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DocsListResult"></a>

`DocsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ClickupApiExecuteResultWithMeta[list[Task], TasksApiSearchResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TasksApiSearchResult"></a>

`TasksApiSearchResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ClickupApiExecuteResultWithMeta[list[Task], TasksListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
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

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ClickupApiExecuteResultWithMeta[list[Task], ViewTasksListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ViewTasksListResult"></a>

`ViewTasksListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ClickupApiExecuteResult[list[Comment]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CommentsListResult"></a>

`CommentsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ClickupApiExecuteResult[list[Folder]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="FoldersListResult"></a>

`FoldersListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ClickupApiExecuteResult[list[Goal]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="GoalsListResult"></a>

`GoalsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ClickupApiExecuteResult[list[List]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ListsListResult"></a>

`ListsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ClickupApiExecuteResult[list[Member]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MembersListResult"></a>

`MembersListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ClickupApiExecuteResult[list[Space]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SpacesListResult"></a>

`SpacesListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ClickupApiExecuteResult[list[Team]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TeamsListResult"></a>

`TeamsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ClickupApiExecuteResult[list[TimeEntry]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TimeTrackingListResult"></a>

`TimeTrackingListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ClickupApiExecuteResult[list[View]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ViewsListResult"></a>

`ViewsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.clickup_api.models.ClickupApiExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Comment"></a>

`Comment(**data: Any)`
:   Comment type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assigned_by: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `assignee: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `comment: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `comment_text: str | None`
    :   The type of the None singleton.

    `date: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reactions: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `resolved: bool | None`
    :   The type of the None singleton.

    `user: dict[str, typing.Any] | None`
    :   The type of the None singleton.

<a id="CommentCreateParams"></a>

`CommentCreateParams(**data: Any)`
:   CommentCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee: int | None`
    :   The type of the None singleton.

    `comment_text: str`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `notify_all: bool | None`
    :   The type of the None singleton.

<a id="CommentCreateResponse"></a>

`CommentCreateResponse(**data: Any)`
:   CommentCreateResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `date: int | None`
    :   The type of the None singleton.

    `hist_id: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `version: dict[str, typing.Any] | None`
    :   The type of the None singleton.

<a id="CommentUpdateParams"></a>

`CommentUpdateParams(**data: Any)`
:   CommentUpdateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee: int | None`
    :   The type of the None singleton.

    `comment_text: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `resolved: bool | None`
    :   The type of the None singleton.

<a id="CommentUpdateResponse"></a>

`CommentUpdateResponse(**data: Any)`
:   CommentUpdateResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CommentsListResponse"></a>

`CommentsListResponse(**data: Any)`
:   CommentsListResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `comments: list[airbyte_agent_sdk.connectors.clickup_api.models.Comment] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CommentsSearchData"></a>

`CommentsSearchData(**data: Any)`
:   Search result data for comments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `comment_text: str | None`
    :   Plain-text content of the comment

    `date: str | None`
    :   Timestamp when the comment was posted, in ClickUp timestamp format

    `id: str`
    :   Unique identifier for the comment

    `model_config`
    :   The type of the None singleton.

    `reply_count: float | None`
    :   Number of replies on the comment

<a id="Doc"></a>

`Doc(**data: Any)`
:   Doc type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: str | None`
    :   The type of the None singleton.

    `creator: int | None`
    :   The type of the None singleton.

    `date_created: int | None`
    :   The type of the None singleton.

    `date_updated: int | None`
    :   The type of the None singleton.

    `deleted: bool | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `parent: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `public: bool | None`
    :   The type of the None singleton.

    `type_: int | None`
    :   The type of the None singleton.

    `workspace_id: int | None`
    :   The type of the None singleton.

<a id="DocsListResponse"></a>

`DocsListResponse(**data: Any)`
:   DocsListResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `docs: list[airbyte_agent_sdk.connectors.clickup_api.models.Doc] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

<a id="DocsListResultMeta"></a>

`DocsListResultMeta(**data: Any)`
:   Metadata for docs.Action.LIST operation
    
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

<a id="Folder"></a>

`Folder(**data: Any)`
:   Folder type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   The type of the None singleton.

    `deleted: bool | None`
    :   The type of the None singleton.

    `hidden: bool | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `lists: list[airbyte_agent_sdk.connectors.clickup_api.models.FolderListsItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `orderindex: int | None`
    :   The type of the None singleton.

    `override_statuses: bool | None`
    :   The type of the None singleton.

    `permission_level: str | None`
    :   The type of the None singleton.

    `space: airbyte_agent_sdk.connectors.clickup_api.models.FolderSpace | None`
    :   The type of the None singleton.

    `statuses: list[airbyte_agent_sdk.connectors.clickup_api.models.FolderStatusesItem] | None`
    :   The type of the None singleton.

    `task_count: str | None`
    :   The type of the None singleton.

<a id="FolderListsItem"></a>

`FolderListsItem(**data: Any)`
:   Nested schema for Folder.lists_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Whether the list is archived

    `assignee: dict[str, typing.Any] | None`
    :   List assignee

    `content: str | None`
    :   List description

    `due_date: str | None`
    :   Due date (Unix ms)

    `id: str | None`
    :   List ID

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   List name

    `orderindex: int | None`
    :   Sort order index

    `override_statuses: bool | None`
    :   Whether list overrides statuses

    `permission_level: str | None`
    :   User permission level

    `priority: dict[str, typing.Any] | None`
    :   List priority

    `space: dict[str, typing.Any] | None`
    :   Parent space reference

    `start_date: str | None`
    :   Start date (Unix ms)

    `status: dict[str, typing.Any] | None`
    :   List status

    `statuses: list[airbyte_agent_sdk.connectors.clickup_api.models.FolderListsItemStatusesItem] | None`
    :   List statuses

    `task_count: int | None`
    :   Number of tasks

<a id="FolderListsItemStatusesItem"></a>

`FolderListsItemStatusesItem(**data: Any)`
:   Nested schema for FolderListsItem.statuses_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   Status color hex code

    `id: str | None`
    :   Status ID

    `model_config`
    :   The type of the None singleton.

    `orderindex: int | None`
    :   Status order index

    `status: str | None`
    :   Status name

    `status_group: str | None`
    :   Status group identifier

    `type_: str | None`
    :   Status type (open, custom, closed)

<a id="FolderSpace"></a>

`FolderSpace(**data: Any)`
:   Parent space reference
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access: bool | None`
    :   Whether user has access

    `id: str | None`
    :   Space ID

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Space name

<a id="FolderStatusesItem"></a>

`FolderStatusesItem(**data: Any)`
:   Nested schema for Folder.statuses_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   Status color hex code

    `id: str | None`
    :   Status ID

    `model_config`
    :   The type of the None singleton.

    `orderindex: int | None`
    :   Status order index

    `status: str | None`
    :   Status name

    `type_: str | None`
    :   Status type (open, custom, closed)

<a id="FoldersListResponse"></a>

`FoldersListResponse(**data: Any)`
:   FoldersListResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `folders: list[airbyte_agent_sdk.connectors.clickup_api.models.Folder] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FoldersSearchData"></a>

`FoldersSearchData(**data: Any)`
:   Search result data for folders entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hidden: bool | None`
    :   Whether the folder is hidden from the sidebar

    `id: str | None`
    :   Unique identifier for the folder

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the folder

    `task_count: str | None`
    :   Number of tasks contained in the folder

<a id="Goal"></a>

`Goal(**data: Any)`
:   Goal type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `creator: int | None`
    :   The type of the None singleton.

    `date_created: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `due_date: str | None`
    :   The type of the None singleton.

    `history: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `key_results: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `members: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `multiple_owners: bool | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `owner: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `percent_completed: int | None`
    :   The type of the None singleton.

    `pretty_id: str | None`
    :   The type of the None singleton.

    `pretty_url: str | None`
    :   The type of the None singleton.

    `private: bool | None`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The type of the None singleton.

    `team_id: str | None`
    :   The type of the None singleton.

<a id="GoalResponse"></a>

`GoalResponse(**data: Any)`
:   GoalResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `goal: airbyte_agent_sdk.connectors.clickup_api.models.Goal | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="GoalsListResponse"></a>

`GoalsListResponse(**data: Any)`
:   GoalsListResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `folders: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `goals: list[airbyte_agent_sdk.connectors.clickup_api.models.Goal] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="GoalsSearchData"></a>

`GoalsSearchData(**data: Any)`
:   Search result data for goals entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Whether the goal has been archived

    `date_created: str | None`
    :   Creation timestamp of the goal, in ClickUp timestamp format

    `description: str | None`
    :   Description of the goal

    `due_date: str | None`
    :   Due date for the goal, in ClickUp timestamp format

    `id: str`
    :   Unique identifier for the goal

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the goal

    `percent_completed: float | None`
    :   Completion percentage of the goal, between 0 and 100

    `pinned: bool | None`
    :   Whether the goal is pinned to the top of the list

    `private: bool | None`
    :   Whether the goal is private to its owners

    `team_id: str | None`
    :   Identifier of the team that owns the goal

<a id="List"></a>

`List(**data: Any)`
:   List type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   The type of the None singleton.

    `assignee: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `content: str | None`
    :   The type of the None singleton.

    `deleted: bool | None`
    :   The type of the None singleton.

    `due_date: str | None`
    :   The type of the None singleton.

    `folder: airbyte_agent_sdk.connectors.clickup_api.models.ListFolder | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `inbound_address: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `orderindex: int | None`
    :   The type of the None singleton.

    `override_statuses: bool | None`
    :   The type of the None singleton.

    `permission_level: str | None`
    :   The type of the None singleton.

    `priority: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `space: airbyte_agent_sdk.connectors.clickup_api.models.ListSpace | None`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The type of the None singleton.

    `status: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `statuses: list[airbyte_agent_sdk.connectors.clickup_api.models.ListStatusesItem] | None`
    :   The type of the None singleton.

    `task_count: int | None`
    :   The type of the None singleton.

<a id="ListFolder"></a>

`ListFolder(**data: Any)`
:   Parent folder reference
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access: bool | None`
    :   Whether user has access

    `hidden: bool | None`
    :   Whether the folder is hidden

    `id: str | None`
    :   Folder ID

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Folder name

<a id="ListSpace"></a>

`ListSpace(**data: Any)`
:   Parent space reference
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access: bool | None`
    :   Whether user has access

    `id: str | None`
    :   Space ID

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Space name

<a id="ListStatusesItem"></a>

`ListStatusesItem(**data: Any)`
:   Nested schema for List.statuses_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   Status color hex code

    `id: str | None`
    :   Status ID

    `model_config`
    :   The type of the None singleton.

    `orderindex: int | None`
    :   Status order index

    `status: str | None`
    :   Status name

    `status_group: str | None`
    :   Status group identifier

    `type_: str | None`
    :   Status type (open, custom, closed)

<a id="ListsListResponse"></a>

`ListsListResponse(**data: Any)`
:   ListsListResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `lists: list[airbyte_agent_sdk.connectors.clickup_api.models.List] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ListsSearchData"></a>

`ListsSearchData(**data: Any)`
:   Search result data for lists entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   Whether the list has been archived

    `due_date: str | None`
    :   Due date for the list, in ClickUp timestamp format

    `id: str | None`
    :   Unique identifier for the list

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the list

    `priority: str | None`
    :   Priority assigned to the list

    `start_date: str | None`
    :   Start date for the list, in ClickUp timestamp format

    `task_count: int | None`
    :   Number of tasks contained in the list

<a id="Member"></a>

`Member(**data: Any)`
:   Member type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `initials: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `profile_picture: str | None`
    :   The type of the None singleton.

    `username: str | None`
    :   The type of the None singleton.

<a id="MembersListResponse"></a>

`MembersListResponse(**data: Any)`
:   MembersListResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `members: list[airbyte_agent_sdk.connectors.clickup_api.models.Member] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Space"></a>

`Space(**data: Any)`
:   Space type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_can_manage: bool | None`
    :   The type of the None singleton.

    `archived: bool | None`
    :   The type of the None singleton.

    `avatar: str | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `features: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeatures | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `multiple_assignees: bool | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `private: bool | None`
    :   The type of the None singleton.

    `statuses: list[airbyte_agent_sdk.connectors.clickup_api.models.SpaceStatusesItem] | None`
    :   The type of the None singleton.

<a id="SpaceFeatures"></a>

`SpaceFeatures(**data: Any)`
:   Feature flags for the space
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `check_unresolved: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesCheckUnresolved | None`
    :   Check unresolved feature settings

    `custom_fields: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesCustomFields | None`
    :   Custom fields feature settings

    `custom_items: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesCustomItems | None`
    :   Custom items feature settings

    `dependency_enforcement: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesDependencyEnforcement | None`
    :   Dependency enforcement settings

    `dependency_type_enabled: bool | None`
    :   Whether dependency types are enabled

    `dependency_warning: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesDependencyWarning | None`
    :   Dependency warning feature settings

    `due_dates: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesDueDates | None`
    :   Due dates feature settings

    `emails: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesEmails | None`
    :   Emails feature settings

    `milestones: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesMilestones | None`
    :   Milestones feature settings

    `model_config`
    :   The type of the None singleton.

    `multiple_assignees: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesMultipleAssignees | None`
    :   Multiple assignees feature settings

    `points: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesPoints | None`
    :   Points feature settings

    `priorities: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesPriorities | None`
    :   Priorities feature settings

    `remap_dependencies: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesRemapDependencies | None`
    :   Remap dependencies feature settings

    `reschedule_closed_dependencies: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesRescheduleClosedDependencies | None`
    :   Reschedule closed dependencies settings

    `scheduler_enabled: bool | None`
    :   Whether scheduler is enabled

    `sprints: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesSprints | None`
    :   Sprints feature settings

    `status_pies: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesStatusPies | None`
    :   Status pies feature settings

    `tags: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesTags | None`
    :   Tags feature settings

    `time_estimates: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesTimeEstimates | None`
    :   Time estimates feature settings

    `time_tracking: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesTimeTracking | None`
    :   Time tracking feature settings

<a id="SpaceFeaturesCheckUnresolved"></a>

`SpaceFeaturesCheckUnresolved(**data: Any)`
:   Check unresolved feature settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `checklists: bool | None`
    :   Check unresolved checklists

    `comments: bool | None`
    :   Check unresolved comments

    `enabled: bool | None`
    :   Whether check unresolved is enabled

    `model_config`
    :   The type of the None singleton.

    `subtasks: bool | None`
    :   Check unresolved subtasks

<a id="SpaceFeaturesCustomFields"></a>

`SpaceFeaturesCustomFields(**data: Any)`
:   Custom fields feature settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether custom fields are enabled

    `model_config`
    :   The type of the None singleton.

<a id="SpaceFeaturesCustomItems"></a>

`SpaceFeaturesCustomItems(**data: Any)`
:   Custom items feature settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether custom items are enabled

    `model_config`
    :   The type of the None singleton.

<a id="SpaceFeaturesDependencyEnforcement"></a>

`SpaceFeaturesDependencyEnforcement(**data: Any)`
:   Dependency enforcement settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enforcement_enabled: bool | None`
    :   Whether enforcement is enabled

    `enforcement_mode: int | None`
    :   Enforcement mode

    `model_config`
    :   The type of the None singleton.

<a id="SpaceFeaturesDependencyWarning"></a>

`SpaceFeaturesDependencyWarning(**data: Any)`
:   Dependency warning feature settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether dependency warnings are enabled

    `model_config`
    :   The type of the None singleton.

<a id="SpaceFeaturesDueDates"></a>

`SpaceFeaturesDueDates(**data: Any)`
:   Due dates feature settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether due dates are enabled

    `model_config`
    :   The type of the None singleton.

    `remap_closed_due_date: bool | None`
    :   Whether closed due dates are remapped

    `remap_due_dates: bool | None`
    :   Whether due dates are remapped

    `start_date: bool | None`
    :   Whether start dates are enabled

<a id="SpaceFeaturesEmails"></a>

`SpaceFeaturesEmails(**data: Any)`
:   Emails feature settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether emails are enabled

    `model_config`
    :   The type of the None singleton.

<a id="SpaceFeaturesMilestones"></a>

`SpaceFeaturesMilestones(**data: Any)`
:   Milestones feature settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether milestones are enabled

    `model_config`
    :   The type of the None singleton.

<a id="SpaceFeaturesMultipleAssignees"></a>

`SpaceFeaturesMultipleAssignees(**data: Any)`
:   Multiple assignees feature settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether multiple assignees are enabled

    `model_config`
    :   The type of the None singleton.

<a id="SpaceFeaturesPoints"></a>

`SpaceFeaturesPoints(**data: Any)`
:   Points feature settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether points are enabled

    `model_config`
    :   The type of the None singleton.

<a id="SpaceFeaturesPriorities"></a>

`SpaceFeaturesPriorities(**data: Any)`
:   Priorities feature settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether priorities are enabled

    `model_config`
    :   The type of the None singleton.

    `priorities: list[airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesPrioritiesPrioritiesItem] | None`
    :   Priority levels

<a id="SpaceFeaturesPrioritiesPrioritiesItem"></a>

`SpaceFeaturesPrioritiesPrioritiesItem(**data: Any)`
:   Nested schema for SpaceFeaturesPriorities.priorities_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   Priority color hex code

    `id: str | None`
    :   Priority ID

    `model_config`
    :   The type of the None singleton.

    `orderindex: str | None`
    :   Priority order index

    `priority: str | None`
    :   Priority name

<a id="SpaceFeaturesRemapDependencies"></a>

`SpaceFeaturesRemapDependencies(**data: Any)`
:   Remap dependencies feature settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether remap dependencies is enabled

    `model_config`
    :   The type of the None singleton.

<a id="SpaceFeaturesRescheduleClosedDependencies"></a>

`SpaceFeaturesRescheduleClosedDependencies(**data: Any)`
:   Reschedule closed dependencies settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether rescheduling closed dependencies is enabled

    `model_config`
    :   The type of the None singleton.

<a id="SpaceFeaturesSprints"></a>

`SpaceFeaturesSprints(**data: Any)`
:   Sprints feature settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether sprints are enabled

    `model_config`
    :   The type of the None singleton.

<a id="SpaceFeaturesStatusPies"></a>

`SpaceFeaturesStatusPies(**data: Any)`
:   Status pies feature settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether status pies are enabled

    `model_config`
    :   The type of the None singleton.

<a id="SpaceFeaturesTags"></a>

`SpaceFeaturesTags(**data: Any)`
:   Tags feature settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether tags are enabled

    `model_config`
    :   The type of the None singleton.

<a id="SpaceFeaturesTimeEstimates"></a>

`SpaceFeaturesTimeEstimates(**data: Any)`
:   Time estimates feature settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | None`
    :   Whether time estimates are enabled

    `model_config`
    :   The type of the None singleton.

    `per_assignee: bool | None`
    :   Whether per-assignee estimates are enabled

    `rollup: bool | None`
    :   Whether time estimate rollup is enabled

<a id="SpaceFeaturesTimeTracking"></a>

`SpaceFeaturesTimeTracking(**data: Any)`
:   Time tracking feature settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `default_to_billable: int | None`
    :   Default billable setting

    `enabled: bool | None`
    :   Whether time tracking is enabled

    `harvest: bool | None`
    :   Whether Harvest integration is enabled

    `model_config`
    :   The type of the None singleton.

    `rollup: bool | None`
    :   Whether time rollup is enabled

<a id="SpaceStatusesItem"></a>

`SpaceStatusesItem(**data: Any)`
:   Nested schema for Space.statuses_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   Status color hex code

    `id: str | None`
    :   Status ID

    `model_config`
    :   The type of the None singleton.

    `orderindex: int | None`
    :   Status order index

    `status: str | None`
    :   Status name

    `type_: str | None`
    :   Status type (open, custom, closed)

<a id="SpacesListResponse"></a>

`SpacesListResponse(**data: Any)`
:   SpacesListResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `spaces: list[airbyte_agent_sdk.connectors.clickup_api.models.Space] | None`
    :   The type of the None singleton.

<a id="SpacesSearchData"></a>

`SpacesSearchData(**data: Any)`
:   Search result data for spaces entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   Unique identifier for the space

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the space

    `private: bool | None`
    :   Whether the space is private

<a id="Task"></a>

`Task(**data: Any)`
:   Task type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | None`
    :   The type of the None singleton.

    `assignees: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `attachments: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `checklists: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `creator: airbyte_agent_sdk.connectors.clickup_api.models.TaskCreator | None`
    :   The type of the None singleton.

    `custom_fields: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `custom_id: str | None`
    :   The type of the None singleton.

    `custom_item_id: int | None`
    :   The type of the None singleton.

    `date_closed: str | None`
    :   The type of the None singleton.

    `date_created: str | None`
    :   The type of the None singleton.

    `date_done: str | None`
    :   The type of the None singleton.

    `date_updated: str | None`
    :   The type of the None singleton.

    `dependencies: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `due_date: str | None`
    :   The type of the None singleton.

    `folder: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `group_assignees: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `linked_tasks: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `list_: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `locations: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `orderindex: str | None`
    :   The type of the None singleton.

    `parent: str | None`
    :   The type of the None singleton.

    `permission_level: str | None`
    :   The type of the None singleton.

    `points: float | None`
    :   The type of the None singleton.

    `priority: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `project: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `sharing: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `space: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The type of the None singleton.

    `status: airbyte_agent_sdk.connectors.clickup_api.models.TaskStatus | None`
    :   The type of the None singleton.

    `tags: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `team_id: str | None`
    :   The type of the None singleton.

    `text_content: str | None`
    :   The type of the None singleton.

    `time_estimate: int | None`
    :   The type of the None singleton.

    `time_spent: int | None`
    :   The type of the None singleton.

    `top_level_parent: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

    `watchers: list[airbyte_agent_sdk.connectors.clickup_api.models.TaskWatchersItem] | None`
    :   The type of the None singleton.

<a id="TaskCreator"></a>

`TaskCreator(**data: Any)`
:   Task creator
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   Creator avatar color

    `email: str | None`
    :   Creator email

    `id: int | None`
    :   Creator user ID

    `model_config`
    :   The type of the None singleton.

    `profile_picture: str | None`
    :   Creator profile picture URL

    `username: str | None`
    :   Creator username

<a id="TaskStatus"></a>

`TaskStatus(**data: Any)`
:   Task status
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   Status color hex code

    `id: str | None`
    :   Status ID

    `model_config`
    :   The type of the None singleton.

    `orderindex: int | None`
    :   Status order index

    `status: str | None`
    :   Status name

    `type_: str | None`
    :   Status type (open, custom, closed)

<a id="TaskWatchersItem"></a>

`TaskWatchersItem(**data: Any)`
:   Nested schema for Task.watchers_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   Watcher avatar color

    `email: str | None`
    :   Watcher email

    `id: int | None`
    :   Watcher user ID

    `initials: str | None`
    :   Watcher initials

    `model_config`
    :   The type of the None singleton.

    `profile_picture: str | None`
    :   Watcher profile picture URL

    `username: str | None`
    :   Watcher username

<a id="TasksApiSearchResultMeta"></a>

`TasksApiSearchResultMeta(**data: Any)`
:   Metadata for tasks.Action.API_SEARCH operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `last_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TasksListResponse"></a>

`TasksListResponse(**data: Any)`
:   TasksListResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `last_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `tasks: list[airbyte_agent_sdk.connectors.clickup_api.models.Task] | None`
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

    `last_page: bool | None`
    :   The type of the None singleton.

    `model_config`
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

    `date_closed: str | None`
    :   Timestamp when the task was closed, in ClickUp timestamp format

    `date_created: str | None`
    :   Creation timestamp of the task, in ClickUp timestamp format

    `date_updated: str | None`
    :   Last update timestamp of the task, in ClickUp timestamp format

    `due_date: str | None`
    :   Due date for the task, in ClickUp timestamp format

    `id: str | None`
    :   Unique identifier for the task

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the task

    `parent: str | None`
    :   ID of the parent task, if this task is a subtask

    `start_date: str | None`
    :   Start date for the task, in ClickUp timestamp format

    `url: str | None`
    :   Permalink URL to view the task in ClickUp

<a id="Team"></a>

`Team(**data: Any)`
:   Team type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar: str | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `members: list[airbyte_agent_sdk.connectors.clickup_api.models.TeamMembersItem] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

<a id="TeamMembersItem"></a>

`TeamMembersItem(**data: Any)`
:   Nested schema for Team.members_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.clickup_api.models.TeamMembersItemUser | None`
    :   Member user details

<a id="TeamMembersItemUser"></a>

`TeamMembersItemUser(**data: Any)`
:   Member user details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   Avatar color

    `custom_role: dict[str, typing.Any] | None`
    :   Custom role details

    `date_invited: str | None`
    :   Date invited (Unix ms)

    `date_joined: str | None`
    :   Date joined (Unix ms)

    `email: str | None`
    :   Email address

    `id: int | None`
    :   User ID

    `initials: str | None`
    :   User initials

    `last_active: str | None`
    :   Last active timestamp (Unix ms)

    `model_config`
    :   The type of the None singleton.

    `profile_picture: str | None`
    :   Profile picture URL

    `role: int | None`
    :   User role ID

    `role_key: str | None`
    :   Role key name

    `role_subtype: int | None`
    :   User role subtype

    `username: str | None`
    :   Username

<a id="TeamsListResponse"></a>

`TeamsListResponse(**data: Any)`
:   TeamsListResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `teams: list[airbyte_agent_sdk.connectors.clickup_api.models.Team] | None`
    :   The type of the None singleton.

<a id="TeamsSearchData"></a>

`TeamsSearchData(**data: Any)`
:   Search result data for teams entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   Unique identifier for the team (workspace)

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the team

<a id="TimeEntriesListResponse"></a>

`TimeEntriesListResponse(**data: Any)`
:   TimeEntriesListResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.clickup_api.models.TimeEntry] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TimeEntry"></a>

`TimeEntry(**data: Any)`
:   TimeEntry type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `at: str | None`
    :   The type of the None singleton.

    `billable: bool | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `duration: str | None`
    :   The type of the None singleton.

    `end: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start: str | None`
    :   The type of the None singleton.

    `tags: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `task: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `user: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `wid: str | None`
    :   The type of the None singleton.

<a id="TimeEntryResponse"></a>

`TimeEntryResponse(**data: Any)`
:   TimeEntryResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.clickup_api.models.TimeEntry | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TimeTrackingSearchData"></a>

`TimeTrackingSearchData(**data: Any)`
:   Search result data for time_tracking entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `time: float | None`
    :   Total tracked time in milliseconds

    `user: dict[str, typing.Any] | None`
    :   User who tracked the time

<a id="User"></a>

`User(**data: Any)`
:   User type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `global_font_support: bool | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `initials: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `profile_picture: str | None`
    :   The type of the None singleton.

    `timezone: str | None`
    :   The type of the None singleton.

    `username: str | None`
    :   The type of the None singleton.

    `week_start_day: int | None`
    :   The type of the None singleton.

<a id="UserResponse"></a>

`UserResponse(**data: Any)`
:   UserResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.clickup_api.models.User | None`
    :   The type of the None singleton.

<a id="UserSearchData"></a>

`UserSearchData(**data: Any)`
:   Search result data for user entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | None`
    :   Unique identifier for the user

    `model_config`
    :   The type of the None singleton.

    `username: str | None`
    :   Display name of the user

<a id="View"></a>

`View(**data: Any)`
:   View type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `columns: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `creator: int | None`
    :   The type of the None singleton.

    `date_created: str | None`
    :   The type of the None singleton.

    `date_protected: str | None`
    :   The type of the None singleton.

    `divide: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `filters: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `grouping: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `orderindex: int | None`
    :   The type of the None singleton.

    `parent: airbyte_agent_sdk.connectors.clickup_api.models.ViewParent | None`
    :   The type of the None singleton.

    `protected: bool | None`
    :   The type of the None singleton.

    `protected_by: int | None`
    :   The type of the None singleton.

    `protected_note: str | None`
    :   The type of the None singleton.

    `public: bool | None`
    :   The type of the None singleton.

    `settings: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `sorting: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `team_sidebar: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `visibility: str | None`
    :   The type of the None singleton.

<a id="ViewParent"></a>

`ViewParent(**data: Any)`
:   Parent reference
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: typing.Any | None`
    :   Parent entity ID

    `model_config`
    :   The type of the None singleton.

    `type_: typing.Any | None`
    :   Parent entity type

<a id="ViewResponse"></a>

`ViewResponse(**data: Any)`
:   ViewResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `view: airbyte_agent_sdk.connectors.clickup_api.models.View | None`
    :   The type of the None singleton.

<a id="ViewTasksListResultMeta"></a>

`ViewTasksListResultMeta(**data: Any)`
:   Metadata for view_tasks.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `last_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ViewsListResponse"></a>

`ViewsListResponse(**data: Any)`
:   ViewsListResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `default_view: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `required_views: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `views: list[airbyte_agent_sdk.connectors.clickup_api.models.View] | None`
    :   The type of the None singleton.