---
id: airbyte_agent_sdk-connectors-asana-models
title: airbyte_agent_sdk.connectors.asana.models
---

Module airbyte_agent_sdk.connectors.asana.models
================================================
Pydantic models for asana connector.

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

    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult[AttachmentsSearchData]
    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult[ProjectsSearchData]
    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult[SectionsSearchData]
    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult[TagsSearchData]
    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult[TasksSearchData]
    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult[TeamsSearchData]
    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult[UsersSearchData]
    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult[WorkspacesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.asana.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[AttachmentsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AttachmentsSearchResult"></a>

`AttachmentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ProjectsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProjectsSearchResult"></a>

`ProjectsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SectionsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SectionsSearchResult"></a>

`SectionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TagsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TagsSearchResult"></a>

`TagsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TasksSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TeamsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UsersSearchResult"></a>

`UsersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[WorkspacesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WorkspacesSearchResult"></a>

`WorkspacesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AsanaCheckResult"></a>

`AsanaCheckResult(**data: Any)`
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

<a id="AsanaExecuteResult"></a>

`AsanaExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="AsanaExecuteResultWithMeta"></a>

`AsanaExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[AttachmentCompact], AttachmentsListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[ProjectCompact], ProjectsListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[ProjectCompact], TaskProjectsListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[ProjectCompact], TeamProjectsListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[ProjectCompact], WorkspaceProjectsListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[SectionCompact], ProjectSectionsListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TagCompact], WorkspaceTagsListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TaskCompact], ProjectTasksListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TaskCompact], SectionTasksListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TaskCompact], TagTasksListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TaskCompact], TaskDependenciesListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TaskCompact], TaskDependentsListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TaskCompact], TaskSubtasksListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TaskCompact], TasksListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TaskCompact], WorkspaceTaskSearchListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TeamCompact], UserTeamsListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[TeamCompact], WorkspaceTeamsListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[UserCompact], TeamUsersListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[UserCompact], UsersListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[UserCompact], WorkspaceUsersListResultMeta]
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta[list[WorkspaceCompact], WorkspacesListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`AsanaExecuteResultWithMeta[list[AttachmentCompact], AttachmentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AttachmentsListResult"></a>

`AttachmentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[ProjectCompact], ProjectsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProjectsListResult"></a>

`ProjectsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[ProjectCompact], TaskProjectsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TaskProjectsListResult"></a>

`TaskProjectsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[ProjectCompact], TeamProjectsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TeamProjectsListResult"></a>

`TeamProjectsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[ProjectCompact], WorkspaceProjectsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WorkspaceProjectsListResult"></a>

`WorkspaceProjectsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[SectionCompact], ProjectSectionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProjectSectionsListResult"></a>

`ProjectSectionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[TagCompact], WorkspaceTagsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WorkspaceTagsListResult"></a>

`WorkspaceTagsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[TaskCompact], ProjectTasksListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProjectTasksListResult"></a>

`ProjectTasksListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[TaskCompact], SectionTasksListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SectionTasksListResult"></a>

`SectionTasksListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[TaskCompact], TagTasksListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TagTasksListResult"></a>

`TagTasksListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[TaskCompact], TaskDependenciesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TaskDependenciesListResult"></a>

`TaskDependenciesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[TaskCompact], TaskDependentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TaskDependentsListResult"></a>

`TaskDependentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[TaskCompact], TaskSubtasksListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TaskSubtasksListResult"></a>

`TaskSubtasksListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[TaskCompact], TasksListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
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

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[TaskCompact], WorkspaceTaskSearchListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WorkspaceTaskSearchListResult"></a>

`WorkspaceTaskSearchListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[TeamCompact], UserTeamsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UserTeamsListResult"></a>

`UserTeamsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[TeamCompact], WorkspaceTeamsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WorkspaceTeamsListResult"></a>

`WorkspaceTeamsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[UserCompact], TeamUsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TeamUsersListResult"></a>

`TeamUsersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[UserCompact], UsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UsersListResult"></a>

`UsersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[UserCompact], WorkspaceUsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WorkspaceUsersListResult"></a>

`WorkspaceUsersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`AsanaExecuteResultWithMeta[list[WorkspaceCompact], WorkspacesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="WorkspacesListResult"></a>

`WorkspacesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.asana.models.AsanaExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AsanaOauth2AuthConfig"></a>

`AsanaOauth2AuthConfig(**data: Any)`
:   OAuth 2
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str | None`
    :   OAuth access token for API requests

    `client_id: str | None`
    :   Connected App Consumer Key

    `client_secret: str | None`
    :   Connected App Consumer Secret

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   OAuth refresh token for automatic token renewal

<a id="AsanaPersonalAccessTokenAuthConfig"></a>

`AsanaPersonalAccessTokenAuthConfig(**data: Any)`
:   Personal Access Token
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `token: str`
    :   Your Asana Personal Access Token. Generate one at https://app.asana.com/0/my-apps

<a id="Attachment"></a>

`Attachment(**data: Any)`
:   Full attachment object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any`
    :   The type of the None singleton.

    `download_url: str | Any | None`
    :   The type of the None singleton.

    `gid: str | Any`
    :   The type of the None singleton.

    `host: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `parent: airbyte_agent_sdk.connectors.asana.models.AttachmentParent | Any`
    :   The type of the None singleton.

    `permanent_url: str | Any | None`
    :   The type of the None singleton.

    `resource_subtype: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

    `size: int | Any | None`
    :   The type of the None singleton.

    `view_url: str | Any | None`
    :   The type of the None singleton.

<a id="AttachmentCompact"></a>

`AttachmentCompact(**data: Any)`
:   Compact attachment object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_subtype: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="AttachmentParent"></a>

`AttachmentParent(**data: Any)`
:   The parent object this attachment is attached to
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_subtype: str | Any`
    :   The subtype of the parent resource

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="AttachmentResponse"></a>

`AttachmentResponse(**data: Any)`
:   Attachment response wrapper
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.Attachment | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="AttachmentsList"></a>

`AttachmentsList(**data: Any)`
:   Paginated list of attachments containing compact attachment objects
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.asana.models.AttachmentCompact] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: airbyte_agent_sdk.connectors.asana.models.AttachmentsListNextPage | Any | None`
    :   The type of the None singleton.

<a id="AttachmentsListNextPage"></a>

`AttachmentsListNextPage(**data: Any)`
:   Nested schema for AttachmentsList.next_page
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `offset: str | Any`
    :   The type of the None singleton.

    `path: str | Any`
    :   The type of the None singleton.

    `uri: str | Any`
    :   The type of the None singleton.

<a id="AttachmentsListResultMeta"></a>

`AttachmentsListResultMeta(**data: Any)`
:   Metadata for attachments.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="AttachmentsSearchData"></a>

`AttachmentsSearchData(**data: Any)`
:   Search result data for attachments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `connected_to_app: bool | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `download_url: str | None`
    :   The type of the None singleton.

    `gid: str | None`
    :   The type of the None singleton.

    `host: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `parent: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `permanent_url: str | None`
    :   The type of the None singleton.

    `resource_subtype: str | None`
    :   The type of the None singleton.

    `resource_type: str | None`
    :   The type of the None singleton.

    `size: int | None`
    :   The type of the None singleton.

    `view_url: str | None`
    :   The type of the None singleton.

<a id="EmptyResponse"></a>

`EmptyResponse(**data: Any)`
:   Empty response returned by delete operations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Project"></a>

`Project(**data: Any)`
:   Full project object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | Any`
    :   The type of the None singleton.

    `color: str | Any | None`
    :   The type of the None singleton.

    `completed: bool | Any`
    :   The type of the None singleton.

    `completed_at: str | Any | None`
    :   The type of the None singleton.

    `completed_by: airbyte_agent_sdk.connectors.asana.models.ProjectCompletedBy | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `current_status: airbyte_agent_sdk.connectors.asana.models.ProjectCurrentStatus | Any | None`
    :   The type of the None singleton.

    `current_status_update: airbyte_agent_sdk.connectors.asana.models.ProjectCurrentStatusUpdate | Any | None`
    :   The type of the None singleton.

    `custom_fields: list[typing.Any] | Any`
    :   The type of the None singleton.

    `default_access_level: str | Any`
    :   The type of the None singleton.

    `default_view: str | Any`
    :   The type of the None singleton.

    `due_date: str | Any | None`
    :   The type of the None singleton.

    `due_on: str | Any | None`
    :   The type of the None singleton.

    `followers: list[airbyte_agent_sdk.connectors.asana.models.ProjectFollowersItem] | Any`
    :   The type of the None singleton.

    `gid: str | Any`
    :   The type of the None singleton.

    `icon: str | Any | None`
    :   The type of the None singleton.

    `members: list[airbyte_agent_sdk.connectors.asana.models.ProjectMembersItem] | Any`
    :   The type of the None singleton.

    `minimum_access_level_for_customization: str | Any`
    :   The type of the None singleton.

    `minimum_access_level_for_sharing: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_at: str | Any`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `notes: str | Any`
    :   The type of the None singleton.

    `owner: airbyte_agent_sdk.connectors.asana.models.ProjectOwner | Any`
    :   The type of the None singleton.

    `permalink_url: str | Any`
    :   The type of the None singleton.

    `privacy_setting: str | Any`
    :   The type of the None singleton.

    `public: bool | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

    `start_on: str | Any | None`
    :   The type of the None singleton.

    `team: airbyte_agent_sdk.connectors.asana.models.ProjectTeam | Any | None`
    :   The type of the None singleton.

    `workspace: airbyte_agent_sdk.connectors.asana.models.ProjectWorkspace | Any`
    :   The type of the None singleton.

<a id="ProjectCompact"></a>

`ProjectCompact(**data: Any)`
:   Compact project object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="ProjectCompletedBy"></a>

`ProjectCompletedBy(**data: Any)`
:   Nested schema for Project.completed_by
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="ProjectCreateParams"></a>

`ProjectCreateParams(**data: Any)`
:   Parameters for creating a new project
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.ProjectCreateParamsData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ProjectCreateParamsData"></a>

`ProjectCreateParamsData(**data: Any)`
:   Nested schema for ProjectCreateParams.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | Any`
    :   Whether the project is archived

    `color: str | Any`
    :   Color of the project (e.g., dark-pink, dark-green, dark-blue, dark-red, dark-teal, dark-brown, dark-orange, dark-purple, dark-warm-gray, light-pink, light-green, light-blue, light-red, light-teal, light-brown, light-orange, light-purple, light-warm-gray, none)

    `default_view: str | Any`
    :   The default view of the project (list, board, calendar, timeline)

    `due_on: str | Any`
    :   Due date in YYYY-MM-DD format

    `html_notes: str | Any`
    :   HTML-formatted description of the project

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Name of the project

    `notes: str | Any`
    :   Free-form textual description of the project (plain text)

    `privacy_setting: str | Any`
    :   Privacy setting: public_to_workspace or private

    `start_on: str | Any`
    :   Start date in YYYY-MM-DD format

    `team: str | Any`
    :   GID of the team to share the project with (required for organizations)

    `workspace: str | Any`
    :   GID of the workspace to create the project in

<a id="ProjectCurrentStatus"></a>

`ProjectCurrentStatus(**data: Any)`
:   Nested schema for Project.current_status
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author: airbyte_agent_sdk.connectors.asana.models.ProjectCurrentStatusAuthor | Any`
    :   The type of the None singleton.

    `color: str | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `created_by: airbyte_agent_sdk.connectors.asana.models.ProjectCurrentStatusCreatedBy | Any`
    :   The type of the None singleton.

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_at: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

    `text: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

<a id="ProjectCurrentStatusAuthor"></a>

`ProjectCurrentStatusAuthor(**data: Any)`
:   Nested schema for ProjectCurrentStatus.author
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="ProjectCurrentStatusCreatedBy"></a>

`ProjectCurrentStatusCreatedBy(**data: Any)`
:   Nested schema for ProjectCurrentStatus.created_by
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="ProjectCurrentStatusUpdate"></a>

`ProjectCurrentStatusUpdate(**data: Any)`
:   Nested schema for Project.current_status_update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `resource_subtype: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

<a id="ProjectFollowersItem"></a>

`ProjectFollowersItem(**data: Any)`
:   Nested schema for Project.followers_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="ProjectMembersItem"></a>

`ProjectMembersItem(**data: Any)`
:   Nested schema for Project.members_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="ProjectOwner"></a>

`ProjectOwner(**data: Any)`
:   Nested schema for Project.owner
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="ProjectResponse"></a>

`ProjectResponse(**data: Any)`
:   Project response wrapper
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.Project | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ProjectSectionsListResultMeta"></a>

`ProjectSectionsListResultMeta(**data: Any)`
:   Metadata for project_sections.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="ProjectTasksListResultMeta"></a>

`ProjectTasksListResultMeta(**data: Any)`
:   Metadata for project_tasks.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="ProjectTeam"></a>

`ProjectTeam(**data: Any)`
:   Nested schema for Project.team
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="ProjectUpdateParams"></a>

`ProjectUpdateParams(**data: Any)`
:   Parameters for updating an existing project
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.ProjectUpdateParamsData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ProjectUpdateParamsData"></a>

`ProjectUpdateParamsData(**data: Any)`
:   Nested schema for ProjectUpdateParams.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | Any`
    :   Whether the project is archived

    `color: str | Any`
    :   Color of the project

    `default_view: str | Any`
    :   The default view of the project (list, board, calendar, timeline)

    `due_on: str | Any`
    :   Due date in YYYY-MM-DD format

    `html_notes: str | Any`
    :   HTML-formatted description of the project

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Name of the project

    `notes: str | Any`
    :   Free-form textual description of the project (plain text)

    `start_on: str | Any`
    :   Start date in YYYY-MM-DD format

<a id="ProjectWorkspace"></a>

`ProjectWorkspace(**data: Any)`
:   Nested schema for Project.workspace
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="ProjectsList"></a>

`ProjectsList(**data: Any)`
:   Paginated list of projects containing compact project objects
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.asana.models.ProjectCompact] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: airbyte_agent_sdk.connectors.asana.models.ProjectsListNextPage | Any | None`
    :   The type of the None singleton.

<a id="ProjectsListNextPage"></a>

`ProjectsListNextPage(**data: Any)`
:   Nested schema for ProjectsList.next_page
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `offset: str | Any`
    :   The type of the None singleton.

    `path: str | Any`
    :   The type of the None singleton.

    `uri: str | Any`
    :   The type of the None singleton.

<a id="ProjectsListResultMeta"></a>

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

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="ProjectsSearchData"></a>

`ProjectsSearchData(**data: Any)`
:   Search result data for projects entity.
    
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

    `created_at: str | None`
    :   The type of the None singleton.

    `current_status: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `custom_field_settings: list[typing.Any] | None`
    :   The type of the None singleton.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `default_view: str | None`
    :   The type of the None singleton.

    `due_date: str | None`
    :   The type of the None singleton.

    `due_on: str | None`
    :   The type of the None singleton.

    `followers: list[typing.Any] | None`
    :   The type of the None singleton.

    `gid: str | None`
    :   The type of the None singleton.

    `html_notes: str | None`
    :   The type of the None singleton.

    `icon: str | None`
    :   The type of the None singleton.

    `is_template: bool | None`
    :   The type of the None singleton.

    `members: list[typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_at: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `notes: str | None`
    :   The type of the None singleton.

    `owner: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `permalink_url: str | None`
    :   The type of the None singleton.

    `public: bool | None`
    :   The type of the None singleton.

    `resource_type: str | None`
    :   The type of the None singleton.

    `start_on: str | None`
    :   The type of the None singleton.

    `team: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `workspace: dict[str, typing.Any] | None`
    :   The type of the None singleton.

<a id="Section"></a>

`Section(**data: Any)`
:   Full section object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any`
    :   The type of the None singleton.

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `project: airbyte_agent_sdk.connectors.asana.models.SectionProject | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="SectionAddTaskParams"></a>

`SectionAddTaskParams(**data: Any)`
:   Parameters for adding a task to a section
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.SectionAddTaskParamsData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SectionAddTaskParamsData"></a>

`SectionAddTaskParamsData(**data: Any)`
:   Nested schema for SectionAddTaskParams.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `insert_after: str | Any`
    :   GID of a task in this section after which the added task should be inserted. Cannot be provided together with insert_before.

    `insert_before: str | Any`
    :   GID of a task in this section before which the added task should be inserted. Cannot be provided together with insert_after.

    `model_config`
    :   The type of the None singleton.

    `task: str | Any`
    :   The GID of the task to add to this section

<a id="SectionCompact"></a>

`SectionCompact(**data: Any)`
:   Compact section object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="SectionCreateParams"></a>

`SectionCreateParams(**data: Any)`
:   Parameters for creating a new section in a project
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.SectionCreateParamsData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SectionCreateParamsData"></a>

`SectionCreateParamsData(**data: Any)`
:   Nested schema for SectionCreateParams.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `insert_after: str | Any`
    :   GID of a section in the same project after which the new section should be inserted. Cannot be provided together with insert_before.

    `insert_before: str | Any`
    :   GID of a section in the same project before which the new section should be inserted. Cannot be provided together with insert_after.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The name of the section (this is displayed as the column header in board view)

<a id="SectionProject"></a>

`SectionProject(**data: Any)`
:   Nested schema for Section.project
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="SectionResponse"></a>

`SectionResponse(**data: Any)`
:   Section response wrapper
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.Section | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SectionTasksListResultMeta"></a>

`SectionTasksListResultMeta(**data: Any)`
:   Metadata for section_tasks.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="SectionUpdateParams"></a>

`SectionUpdateParams(**data: Any)`
:   Parameters for updating an existing section
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.SectionUpdateParamsData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SectionUpdateParamsData"></a>

`SectionUpdateParamsData(**data: Any)`
:   Nested schema for SectionUpdateParams.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The new name of the section

<a id="SectionsList"></a>

`SectionsList(**data: Any)`
:   Paginated list of sections containing compact section objects
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.asana.models.SectionCompact] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: airbyte_agent_sdk.connectors.asana.models.SectionsListNextPage | Any | None`
    :   The type of the None singleton.

<a id="SectionsListNextPage"></a>

`SectionsListNextPage(**data: Any)`
:   Nested schema for SectionsList.next_page
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `offset: str | Any`
    :   The type of the None singleton.

    `path: str | Any`
    :   The type of the None singleton.

    `uri: str | Any`
    :   The type of the None singleton.

<a id="SectionsSearchData"></a>

`SectionsSearchData(**data: Any)`
:   Search result data for sections entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `gid: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `project: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `resource_type: str | None`
    :   The type of the None singleton.

<a id="Story"></a>

`Story(**data: Any)`
:   A story represents an activity associated with an object in Asana
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any`
    :   The type of the None singleton.

    `created_by: airbyte_agent_sdk.connectors.asana.models.StoryCreatedBy | Any`
    :   The type of the None singleton.

    `gid: str | Any`
    :   The type of the None singleton.

    `html_text: str | Any`
    :   The type of the None singleton.

    `is_pinned: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `resource_subtype: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

    `target: airbyte_agent_sdk.connectors.asana.models.StoryTarget | Any`
    :   The type of the None singleton.

    `text: str | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

<a id="StoryCreateParams"></a>

`StoryCreateParams(**data: Any)`
:   Parameters for creating a comment (story) on a task
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.StoryCreateParamsData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="StoryCreateParamsData"></a>

`StoryCreateParamsData(**data: Any)`
:   Nested schema for StoryCreateParams.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `html_text: str | Any`
    :   HTML-formatted body of the comment

    `is_pinned: bool | Any`
    :   Whether the story should be pinned on the resource

    `model_config`
    :   The type of the None singleton.

    `text: str | Any`
    :   The plain text body of the comment

<a id="StoryCreatedBy"></a>

`StoryCreatedBy(**data: Any)`
:   Nested schema for Story.created_by
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="StoryResponse"></a>

`StoryResponse(**data: Any)`
:   Story response wrapper
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.Story | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="StoryTarget"></a>

`StoryTarget(**data: Any)`
:   Nested schema for Story.target
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="Tag"></a>

`Tag(**data: Any)`
:   Full tag object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `followers: list[typing.Any] | Any`
    :   The type of the None singleton.

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `notes: str | Any`
    :   The type of the None singleton.

    `permalink_url: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

    `workspace: airbyte_agent_sdk.connectors.asana.models.TagWorkspace | Any`
    :   The type of the None singleton.

<a id="TagCompact"></a>

`TagCompact(**data: Any)`
:   Compact tag object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="TagCreateParams"></a>

`TagCreateParams(**data: Any)`
:   Parameters for creating a new tag in a workspace
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.TagCreateParamsData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TagCreateParamsData"></a>

`TagCreateParamsData(**data: Any)`
:   Nested schema for TagCreateParams.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | Any`
    :   Color of the tag. Must be one of: dark-pink, dark-green, dark-blue, dark-red, dark-teal, dark-brown, dark-orange, dark-purple, dark-warm-gray, light-pink, light-green, light-blue, light-red, light-teal, light-brown, light-orange, light-purple, light-warm-gray, none, null

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Name of the tag

    `notes: str | Any`
    :   Free-form textual description of the tag

<a id="TagResponse"></a>

`TagResponse(**data: Any)`
:   Tag response wrapper
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.Tag | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TagTasksListResultMeta"></a>

`TagTasksListResultMeta(**data: Any)`
:   Metadata for tag_tasks.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="TagUpdateParams"></a>

`TagUpdateParams(**data: Any)`
:   Parameters for updating an existing tag
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.TagUpdateParamsData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TagUpdateParamsData"></a>

`TagUpdateParamsData(**data: Any)`
:   Nested schema for TagUpdateParams.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | Any`
    :   Color of the tag

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Name of the tag

    `notes: str | Any`
    :   Free-form textual description of the tag

<a id="TagWorkspace"></a>

`TagWorkspace(**data: Any)`
:   Nested schema for Tag.workspace
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="TagsList"></a>

`TagsList(**data: Any)`
:   Paginated list of tags containing compact tag objects
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.asana.models.TagCompact] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: airbyte_agent_sdk.connectors.asana.models.TagsListNextPage | Any | None`
    :   The type of the None singleton.

<a id="TagsListNextPage"></a>

`TagsListNextPage(**data: Any)`
:   Nested schema for TagsList.next_page
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `offset: str | Any`
    :   The type of the None singleton.

    `path: str | Any`
    :   The type of the None singleton.

    `uri: str | Any`
    :   The type of the None singleton.

<a id="TagsSearchData"></a>

`TagsSearchData(**data: Any)`
:   Search result data for tags entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `followers: list[typing.Any] | None`
    :   The type of the None singleton.

    `gid: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `permalink_url: str | None`
    :   The type of the None singleton.

    `resource_type: str | None`
    :   The type of the None singleton.

    `workspace: dict[str, typing.Any] | None`
    :   The type of the None singleton.

<a id="Task"></a>

`Task(**data: Any)`
:   Full task object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TaskAddTagParams"></a>

`TaskAddTagParams(**data: Any)`
:   Parameters for adding a tag to a task
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.TaskAddTagParamsData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TaskAddTagParamsData"></a>

`TaskAddTagParamsData(**data: Any)`
:   Nested schema for TaskAddTagParams.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `tag: str | Any`
    :   The GID of the tag to add to the task

<a id="TaskCompact"></a>

`TaskCompact(**data: Any)`
:   Compact task object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_by: airbyte_agent_sdk.connectors.asana.models.TaskCompactCreatedBy | Any`
    :   The type of the None singleton.

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_subtype: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="TaskCompactCreatedBy"></a>

`TaskCompactCreatedBy(**data: Any)`
:   User who created the task
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `resource_type: str | Any`
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

    `data: airbyte_agent_sdk.connectors.asana.models.TaskCreateParamsData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TaskCreateParamsData"></a>

`TaskCreateParamsData(**data: Any)`
:   Nested schema for TaskCreateParams.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee: str | Any`
    :   GID of the user to assign the task to, or 'me' for the current user

    `completed: bool | Any`
    :   Whether the task is completed

    `due_at: str | Any`
    :   Due date and time in ISO 8601 format (e.g., 2025-03-20T12:00:00.000Z)

    `due_on: str | Any`
    :   Due date in YYYY-MM-DD format

    `followers: list[str] | Any`
    :   Array of user GIDs to add as followers

    `html_notes: str | Any`
    :   HTML-formatted description of the task

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Name of the task

    `notes: str | Any`
    :   Free-form textual description of the task (plain text, no formatting)

    `parent: str | Any`
    :   GID of the parent task (to create a subtask)

    `projects: list[str] | Any`
    :   Array of project GIDs to add the task to

    `resource_subtype: str | Any`
    :   The subtype of the task: default_task, milestone, section, or approval

    `start_on: str | Any`
    :   Start date in YYYY-MM-DD format

    `tags: list[str] | Any`
    :   Array of tag GIDs to add to the task

    `workspace: str | Any`
    :   GID of the workspace to create the task in

<a id="TaskDependenciesListResultMeta"></a>

`TaskDependenciesListResultMeta(**data: Any)`
:   Metadata for task_dependencies.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="TaskDependentsListResultMeta"></a>

`TaskDependentsListResultMeta(**data: Any)`
:   Metadata for task_dependents.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="TaskProjectsListResultMeta"></a>

`TaskProjectsListResultMeta(**data: Any)`
:   Metadata for task_projects.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="TaskRemoveTagParams"></a>

`TaskRemoveTagParams(**data: Any)`
:   Parameters for removing a tag from a task
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.TaskRemoveTagParamsData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TaskRemoveTagParamsData"></a>

`TaskRemoveTagParamsData(**data: Any)`
:   Nested schema for TaskRemoveTagParams.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `tag: str | Any`
    :   The GID of the tag to remove from the task

<a id="TaskResponse"></a>

`TaskResponse(**data: Any)`
:   Task response wrapper
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.Task | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TaskSubtasksListResultMeta"></a>

`TaskSubtasksListResultMeta(**data: Any)`
:   Metadata for task_subtasks.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="TaskUpdateParams"></a>

`TaskUpdateParams(**data: Any)`
:   Parameters for updating an existing task
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.TaskUpdateParamsData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TaskUpdateParamsData"></a>

`TaskUpdateParamsData(**data: Any)`
:   Nested schema for TaskUpdateParams.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee: str | Any`
    :   GID of the user to assign the task to, or 'me' for the current user

    `completed: bool | Any`
    :   Whether the task is completed

    `due_at: str | Any`
    :   Due date and time in ISO 8601 format (e.g., 2025-03-20T12:00:00.000Z)

    `due_on: str | Any`
    :   Due date in YYYY-MM-DD format

    `html_notes: str | Any`
    :   HTML-formatted description of the task

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Name of the task

    `notes: str | Any`
    :   Free-form textual description of the task (plain text, no formatting)

    `start_on: str | Any`
    :   Start date in YYYY-MM-DD format

<a id="TasksList"></a>

`TasksList(**data: Any)`
:   Paginated list of tasks containing compact task objects
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.asana.models.TaskCompact] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: airbyte_agent_sdk.connectors.asana.models.TasksListNextPage | Any | None`
    :   The type of the None singleton.

<a id="TasksListNextPage"></a>

`TasksListNextPage(**data: Any)`
:   Nested schema for TasksList.next_page
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `offset: str | Any`
    :   The type of the None singleton.

    `path: str | Any`
    :   The type of the None singleton.

    `uri: str | Any`
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

    `next_page: dict[str, typing.Any] | Any | None`
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

    `actual_time_minutes: int | None`
    :   The actual time spent on the task in minutes

    `approval_status: str | None`
    :   The type of the None singleton.

    `assignee: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `completed: bool | None`
    :   The type of the None singleton.

    `completed_at: str | None`
    :   The type of the None singleton.

    `completed_by: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `custom_fields: list[typing.Any] | None`
    :   The type of the None singleton.

    `dependencies: list[typing.Any] | None`
    :   The type of the None singleton.

    `dependents: list[typing.Any] | None`
    :   The type of the None singleton.

    `due_at: str | None`
    :   The type of the None singleton.

    `due_on: str | None`
    :   The type of the None singleton.

    `external: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `followers: list[typing.Any] | None`
    :   The type of the None singleton.

    `gid: str | None`
    :   The type of the None singleton.

    `hearted: bool | None`
    :   The type of the None singleton.

    `hearts: list[typing.Any] | None`
    :   The type of the None singleton.

    `html_notes: str | None`
    :   The type of the None singleton.

    `is_rendered_as_separator: bool | None`
    :   The type of the None singleton.

    `liked: bool | None`
    :   The type of the None singleton.

    `likes: list[typing.Any] | None`
    :   The type of the None singleton.

    `memberships: list[typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `modified_at: str | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `notes: str | None`
    :   The type of the None singleton.

    `num_hearts: int | None`
    :   The type of the None singleton.

    `num_likes: int | None`
    :   The type of the None singleton.

    `num_subtasks: int | None`
    :   The type of the None singleton.

    `parent: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `permalink_url: str | None`
    :   The type of the None singleton.

    `projects: list[typing.Any] | None`
    :   The type of the None singleton.

    `resource_subtype: str | None`
    :   The type of the None singleton.

    `resource_type: str | None`
    :   The type of the None singleton.

    `start_on: str | None`
    :   The type of the None singleton.

    `tags: list[typing.Any] | None`
    :   The type of the None singleton.

    `workspace: dict[str, typing.Any] | None`
    :   The type of the None singleton.

<a id="Team"></a>

`Team(**data: Any)`
:   Full team object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `organization: airbyte_agent_sdk.connectors.asana.models.TeamOrganization | Any`
    :   The type of the None singleton.

    `permalink_url: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="TeamCompact"></a>

`TeamCompact(**data: Any)`
:   Compact team object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="TeamOrganization"></a>

`TeamOrganization(**data: Any)`
:   Nested schema for Team.organization
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="TeamProjectsListResultMeta"></a>

`TeamProjectsListResultMeta(**data: Any)`
:   Metadata for team_projects.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="TeamResponse"></a>

`TeamResponse(**data: Any)`
:   Team response wrapper
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.Team | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TeamUsersListResultMeta"></a>

`TeamUsersListResultMeta(**data: Any)`
:   Metadata for team_users.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="TeamsList"></a>

`TeamsList(**data: Any)`
:   Paginated list of teams containing compact team objects
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.asana.models.TeamCompact] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: airbyte_agent_sdk.connectors.asana.models.TeamsListNextPage | Any | None`
    :   The type of the None singleton.

<a id="TeamsListNextPage"></a>

`TeamsListNextPage(**data: Any)`
:   Nested schema for TeamsList.next_page
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `offset: str | Any`
    :   The type of the None singleton.

    `path: str | Any`
    :   The type of the None singleton.

    `uri: str | Any`
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

    `description: str | None`
    :   The type of the None singleton.

    `gid: str | None`
    :   The type of the None singleton.

    `html_description: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `organization: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `permalink_url: str | None`
    :   The type of the None singleton.

    `resource_type: str | None`
    :   The type of the None singleton.

<a id="User"></a>

`User(**data: Any)`
:   Full user object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | Any`
    :   The type of the None singleton.

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `photo: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

    `workspaces: list[airbyte_agent_sdk.connectors.asana.models.UserWorkspacesItem] | Any`
    :   The type of the None singleton.

<a id="UserCompact"></a>

`UserCompact(**data: Any)`
:   Compact user object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="UserResponse"></a>

`UserResponse(**data: Any)`
:   User response wrapper
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.User | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="UserTeamsListResultMeta"></a>

`UserTeamsListResultMeta(**data: Any)`
:   Metadata for user_teams.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="UserWorkspacesItem"></a>

`UserWorkspacesItem(**data: Any)`
:   Nested schema for User.workspaces_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="UsersList"></a>

`UsersList(**data: Any)`
:   Paginated list of users containing compact user objects
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.asana.models.UserCompact] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: airbyte_agent_sdk.connectors.asana.models.UsersListNextPage | Any | None`
    :   The type of the None singleton.

<a id="UsersListNextPage"></a>

`UsersListNextPage(**data: Any)`
:   Nested schema for UsersList.next_page
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `offset: str | Any`
    :   The type of the None singleton.

    `path: str | Any`
    :   The type of the None singleton.

    `uri: str | Any`
    :   The type of the None singleton.

<a id="UsersListResultMeta"></a>

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

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="UsersSearchData"></a>

`UsersSearchData(**data: Any)`
:   Search result data for users entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | None`
    :   The type of the None singleton.

    `gid: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `photo: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `resource_type: str | None`
    :   The type of the None singleton.

    `workspaces: list[typing.Any] | None`
    :   The type of the None singleton.

<a id="Workspace"></a>

`Workspace(**data: Any)`
:   Full workspace object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email_domains: list[str] | Any`
    :   The type of the None singleton.

    `gid: str | Any`
    :   The type of the None singleton.

    `is_organization: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="WorkspaceAddUserParams"></a>

`WorkspaceAddUserParams(**data: Any)`
:   Parameters for adding a user to a workspace or organization
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.WorkspaceAddUserParamsData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="WorkspaceAddUserParamsData"></a>

`WorkspaceAddUserParamsData(**data: Any)`
:   Nested schema for WorkspaceAddUserParams.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `user: str | Any`
    :   A user GID or email address to add to the workspace

<a id="WorkspaceCompact"></a>

`WorkspaceCompact(**data: Any)`
:   Compact workspace object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `gid: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_type: str | Any`
    :   The type of the None singleton.

<a id="WorkspaceProjectsListResultMeta"></a>

`WorkspaceProjectsListResultMeta(**data: Any)`
:   Metadata for workspace_projects.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="WorkspaceResponse"></a>

`WorkspaceResponse(**data: Any)`
:   Workspace response wrapper
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.asana.models.Workspace | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="WorkspaceTagsListResultMeta"></a>

`WorkspaceTagsListResultMeta(**data: Any)`
:   Metadata for workspace_tags.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="WorkspaceTaskSearchListResultMeta"></a>

`WorkspaceTaskSearchListResultMeta(**data: Any)`
:   Metadata for workspace_task_search.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="WorkspaceTeamsListResultMeta"></a>

`WorkspaceTeamsListResultMeta(**data: Any)`
:   Metadata for workspace_teams.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="WorkspaceUsersListResultMeta"></a>

`WorkspaceUsersListResultMeta(**data: Any)`
:   Metadata for workspace_users.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="WorkspacesList"></a>

`WorkspacesList(**data: Any)`
:   Paginated list of workspaces containing compact workspace objects
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.asana.models.WorkspaceCompact] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: airbyte_agent_sdk.connectors.asana.models.WorkspacesListNextPage | Any | None`
    :   The type of the None singleton.

<a id="WorkspacesListNextPage"></a>

`WorkspacesListNextPage(**data: Any)`
:   Nested schema for WorkspacesList.next_page
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `offset: str | Any`
    :   The type of the None singleton.

    `path: str | Any`
    :   The type of the None singleton.

    `uri: str | Any`
    :   The type of the None singleton.

<a id="WorkspacesListResultMeta"></a>

`WorkspacesListResultMeta(**data: Any)`
:   Metadata for workspaces.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="WorkspacesSearchData"></a>

`WorkspacesSearchData(**data: Any)`
:   Search result data for workspaces entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email_domains: list[typing.Any] | None`
    :   The type of the None singleton.

    `gid: str | None`
    :   The type of the None singleton.

    `is_organization: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `resource_type: str | None`
    :   The type of the None singleton.