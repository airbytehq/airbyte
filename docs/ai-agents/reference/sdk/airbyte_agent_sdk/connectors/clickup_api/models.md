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

    `meta: ~S`
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

    `assigned_by: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `assignee: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `comment: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `comment_text: str | Any`
    :   The type of the None singleton.

    `date: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reactions: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `resolved: bool | Any`
    :   The type of the None singleton.

    `user: dict[str, typing.Any] | Any`
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

    `assignee: int | Any`
    :   The type of the None singleton.

    `comment_text: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `notify_all: bool | Any`
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

    `date: int | Any`
    :   The type of the None singleton.

    `hist_id: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `version: dict[str, typing.Any] | Any | None`
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

    `assignee: int | Any`
    :   The type of the None singleton.

    `comment_text: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `resolved: bool | Any`
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

    `comments: list[airbyte_agent_sdk.connectors.clickup_api.models.Comment] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `content: str | Any | None`
    :   The type of the None singleton.

    `creator: int | Any | None`
    :   The type of the None singleton.

    `date_created: int | Any | None`
    :   The type of the None singleton.

    `date_updated: int | Any | None`
    :   The type of the None singleton.

    `deleted: bool | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `parent: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `public: bool | Any | None`
    :   The type of the None singleton.

    `type_: int | Any | None`
    :   The type of the None singleton.

    `workspace_id: int | Any | None`
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

    `docs: list[airbyte_agent_sdk.connectors.clickup_api.models.Doc] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
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

    `next_cursor: str | Any | None`
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

    `archived: bool | Any`
    :   The type of the None singleton.

    `deleted: bool | Any | None`
    :   The type of the None singleton.

    `hidden: bool | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `lists: list[airbyte_agent_sdk.connectors.clickup_api.models.FolderListsItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `orderindex: int | Any | None`
    :   The type of the None singleton.

    `override_statuses: bool | Any`
    :   The type of the None singleton.

    `permission_level: str | Any | None`
    :   The type of the None singleton.

    `space: airbyte_agent_sdk.connectors.clickup_api.models.FolderSpace | Any`
    :   The type of the None singleton.

    `statuses: list[airbyte_agent_sdk.connectors.clickup_api.models.FolderStatusesItem] | Any`
    :   The type of the None singleton.

    `task_count: str | Any | None`
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

    `archived: bool | Any | None`
    :   Whether the list is archived

    `assignee: dict[str, typing.Any] | Any | None`
    :   List assignee

    `content: str | Any | None`
    :   List description

    `due_date: str | Any | None`
    :   Due date (Unix ms)

    `id: str | Any`
    :   List ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   List name

    `orderindex: int | Any | None`
    :   Sort order index

    `override_statuses: bool | Any | None`
    :   Whether list overrides statuses

    `permission_level: str | Any | None`
    :   User permission level

    `priority: dict[str, typing.Any] | Any | None`
    :   List priority

    `space: dict[str, typing.Any] | Any | None`
    :   Parent space reference

    `start_date: str | Any | None`
    :   Start date (Unix ms)

    `status: dict[str, typing.Any] | Any | None`
    :   List status

    `statuses: list[airbyte_agent_sdk.connectors.clickup_api.models.FolderListsItemStatusesItem] | Any`
    :   List statuses

    `task_count: int | Any | None`
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

    `color: str | Any`
    :   Status color hex code

    `id: str | Any`
    :   Status ID

    `model_config`
    :   The type of the None singleton.

    `orderindex: int | Any`
    :   Status order index

    `status: str | Any`
    :   Status name

    `status_group: str | Any | None`
    :   Status group identifier

    `type_: str | Any`
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

    `access: bool | Any | None`
    :   Whether user has access

    `id: str | Any`
    :   Space ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
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

    `color: str | Any`
    :   Status color hex code

    `id: str | Any`
    :   Status ID

    `model_config`
    :   The type of the None singleton.

    `orderindex: int | Any`
    :   Status order index

    `status: str | Any`
    :   Status name

    `type_: str | Any`
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

    `folders: list[airbyte_agent_sdk.connectors.clickup_api.models.Folder] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `archived: bool | Any`
    :   The type of the None singleton.

    `color: str | Any`
    :   The type of the None singleton.

    `creator: int | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `due_date: str | Any | None`
    :   The type of the None singleton.

    `history: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `key_results: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `members: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `multiple_owners: bool | Any`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `owner: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `percent_completed: int | Any | None`
    :   The type of the None singleton.

    `pretty_id: str | Any | None`
    :   The type of the None singleton.

    `pretty_url: str | Any | None`
    :   The type of the None singleton.

    `private: bool | Any`
    :   The type of the None singleton.

    `start_date: str | Any | None`
    :   The type of the None singleton.

    `team_id: str | Any`
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

    `goal: airbyte_agent_sdk.connectors.clickup_api.models.Goal | Any`
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

    `folders: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `goals: list[airbyte_agent_sdk.connectors.clickup_api.models.Goal] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `archived: bool | Any`
    :   The type of the None singleton.

    `assignee: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `content: str | Any | None`
    :   The type of the None singleton.

    `deleted: bool | Any | None`
    :   The type of the None singleton.

    `due_date: str | Any | None`
    :   The type of the None singleton.

    `folder: airbyte_agent_sdk.connectors.clickup_api.models.ListFolder | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `inbound_address: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `orderindex: int | Any | None`
    :   The type of the None singleton.

    `override_statuses: bool | Any | None`
    :   The type of the None singleton.

    `permission_level: str | Any | None`
    :   The type of the None singleton.

    `priority: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `space: airbyte_agent_sdk.connectors.clickup_api.models.ListSpace | Any`
    :   The type of the None singleton.

    `start_date: str | Any | None`
    :   The type of the None singleton.

    `status: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `statuses: list[airbyte_agent_sdk.connectors.clickup_api.models.ListStatusesItem] | Any`
    :   The type of the None singleton.

    `task_count: int | Any | None`
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

    `access: bool | Any | None`
    :   Whether user has access

    `hidden: bool | Any | None`
    :   Whether the folder is hidden

    `id: str | Any`
    :   Folder ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
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

    `access: bool | Any | None`
    :   Whether user has access

    `id: str | Any`
    :   Space ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
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

    `color: str | Any`
    :   Status color hex code

    `id: str | Any`
    :   Status ID

    `model_config`
    :   The type of the None singleton.

    `orderindex: int | Any`
    :   Status order index

    `status: str | Any`
    :   Status name

    `status_group: str | Any | None`
    :   Status group identifier

    `type_: str | Any`
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

    `lists: list[airbyte_agent_sdk.connectors.clickup_api.models.List] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `color: str | Any | None`
    :   The type of the None singleton.

    `email: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `initials: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `profile_picture: str | Any | None`
    :   The type of the None singleton.

    `username: str | Any`
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

    `members: list[airbyte_agent_sdk.connectors.clickup_api.models.Member] | Any`
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

    `admin_can_manage: bool | Any | None`
    :   The type of the None singleton.

    `archived: bool | Any`
    :   The type of the None singleton.

    `avatar: str | Any | None`
    :   The type of the None singleton.

    `color: str | Any | None`
    :   The type of the None singleton.

    `features: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeatures | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `multiple_assignees: bool | Any`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `private: bool | Any`
    :   The type of the None singleton.

    `statuses: list[airbyte_agent_sdk.connectors.clickup_api.models.SpaceStatusesItem] | Any`
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

    `check_unresolved: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesCheckUnresolved | Any`
    :   Check unresolved feature settings

    `custom_fields: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesCustomFields | Any`
    :   Custom fields feature settings

    `custom_items: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesCustomItems | Any`
    :   Custom items feature settings

    `dependency_enforcement: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesDependencyEnforcement | Any`
    :   Dependency enforcement settings

    `dependency_type_enabled: bool | Any`
    :   Whether dependency types are enabled

    `dependency_warning: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesDependencyWarning | Any`
    :   Dependency warning feature settings

    `due_dates: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesDueDates | Any`
    :   Due dates feature settings

    `emails: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesEmails | Any`
    :   Emails feature settings

    `milestones: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesMilestones | Any`
    :   Milestones feature settings

    `model_config`
    :   The type of the None singleton.

    `multiple_assignees: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesMultipleAssignees | Any`
    :   Multiple assignees feature settings

    `points: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesPoints | Any`
    :   Points feature settings

    `priorities: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesPriorities | Any`
    :   Priorities feature settings

    `remap_dependencies: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesRemapDependencies | Any`
    :   Remap dependencies feature settings

    `reschedule_closed_dependencies: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesRescheduleClosedDependencies | Any`
    :   Reschedule closed dependencies settings

    `scheduler_enabled: bool | Any`
    :   Whether scheduler is enabled

    `sprints: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesSprints | Any`
    :   Sprints feature settings

    `status_pies: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesStatusPies | Any`
    :   Status pies feature settings

    `tags: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesTags | Any`
    :   Tags feature settings

    `time_estimates: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesTimeEstimates | Any`
    :   Time estimates feature settings

    `time_tracking: airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesTimeTracking | Any`
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

    `checklists: bool | Any | None`
    :   Check unresolved checklists

    `comments: bool | Any | None`
    :   Check unresolved comments

    `enabled: bool | Any`
    :   Whether check unresolved is enabled

    `model_config`
    :   The type of the None singleton.

    `subtasks: bool | Any | None`
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

    `enabled: bool | Any`
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

    `enabled: bool | Any`
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

    `enforcement_enabled: bool | Any`
    :   Whether enforcement is enabled

    `enforcement_mode: int | Any | None`
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

    `enabled: bool | Any`
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

    `enabled: bool | Any`
    :   Whether due dates are enabled

    `model_config`
    :   The type of the None singleton.

    `remap_closed_due_date: bool | Any`
    :   Whether closed due dates are remapped

    `remap_due_dates: bool | Any`
    :   Whether due dates are remapped

    `start_date: bool | Any`
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

    `enabled: bool | Any`
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

    `enabled: bool | Any`
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

    `enabled: bool | Any`
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

    `enabled: bool | Any`
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

    `enabled: bool | Any`
    :   Whether priorities are enabled

    `model_config`
    :   The type of the None singleton.

    `priorities: list[airbyte_agent_sdk.connectors.clickup_api.models.SpaceFeaturesPrioritiesPrioritiesItem] | Any`
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

    `color: str | Any`
    :   Priority color hex code

    `id: str | Any`
    :   Priority ID

    `model_config`
    :   The type of the None singleton.

    `orderindex: str | Any`
    :   Priority order index

    `priority: str | Any`
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

    `enabled: bool | Any`
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

    `enabled: bool | Any`
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

    `enabled: bool | Any`
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

    `enabled: bool | Any`
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

    `enabled: bool | Any`
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

    `enabled: bool | Any`
    :   Whether time estimates are enabled

    `model_config`
    :   The type of the None singleton.

    `per_assignee: bool | Any`
    :   Whether per-assignee estimates are enabled

    `rollup: bool | Any`
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

    `default_to_billable: int | Any | None`
    :   Default billable setting

    `enabled: bool | Any`
    :   Whether time tracking is enabled

    `harvest: bool | Any`
    :   Whether Harvest integration is enabled

    `model_config`
    :   The type of the None singleton.

    `rollup: bool | Any`
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

    `color: str | Any`
    :   Status color hex code

    `id: str | Any`
    :   Status ID

    `model_config`
    :   The type of the None singleton.

    `orderindex: int | Any`
    :   Status order index

    `status: str | Any`
    :   Status name

    `type_: str | Any`
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

    `spaces: list[airbyte_agent_sdk.connectors.clickup_api.models.Space] | Any`
    :   The type of the None singleton.

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

    `archived: bool | Any`
    :   The type of the None singleton.

    `assignees: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `attachments: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `checklists: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `creator: airbyte_agent_sdk.connectors.clickup_api.models.TaskCreator | Any`
    :   The type of the None singleton.

    `custom_fields: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `custom_id: str | Any | None`
    :   The type of the None singleton.

    `custom_item_id: int | Any | None`
    :   The type of the None singleton.

    `date_closed: str | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_done: str | Any | None`
    :   The type of the None singleton.

    `date_updated: str | Any | None`
    :   The type of the None singleton.

    `dependencies: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `due_date: str | Any | None`
    :   The type of the None singleton.

    `folder: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `group_assignees: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `linked_tasks: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `list_: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `locations: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `orderindex: str | Any | None`
    :   The type of the None singleton.

    `parent: str | Any | None`
    :   The type of the None singleton.

    `permission_level: str | Any | None`
    :   The type of the None singleton.

    `points: float | Any | None`
    :   The type of the None singleton.

    `priority: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `project: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `sharing: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `space: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `start_date: str | Any | None`
    :   The type of the None singleton.

    `status: airbyte_agent_sdk.connectors.clickup_api.models.TaskStatus | Any`
    :   The type of the None singleton.

    `tags: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `team_id: str | Any | None`
    :   The type of the None singleton.

    `text_content: str | Any | None`
    :   The type of the None singleton.

    `time_estimate: int | Any | None`
    :   The type of the None singleton.

    `time_spent: int | Any | None`
    :   The type of the None singleton.

    `top_level_parent: str | Any | None`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

    `watchers: list[airbyte_agent_sdk.connectors.clickup_api.models.TaskWatchersItem] | Any`
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

    `color: str | Any | None`
    :   Creator avatar color

    `email: str | Any`
    :   Creator email

    `id: int | Any`
    :   Creator user ID

    `model_config`
    :   The type of the None singleton.

    `profile_picture: str | Any | None`
    :   Creator profile picture URL

    `username: str | Any`
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

    `color: str | Any | None`
    :   Status color hex code

    `id: str | Any`
    :   Status ID

    `model_config`
    :   The type of the None singleton.

    `orderindex: int | Any`
    :   Status order index

    `status: str | Any`
    :   Status name

    `type_: str | Any`
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

    `color: str | Any | None`
    :   Watcher avatar color

    `email: str | Any`
    :   Watcher email

    `id: int | Any`
    :   Watcher user ID

    `initials: str | Any | None`
    :   Watcher initials

    `model_config`
    :   The type of the None singleton.

    `profile_picture: str | Any | None`
    :   Watcher profile picture URL

    `username: str | Any`
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

    `last_page: bool | Any | None`
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

    `last_page: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `tasks: list[airbyte_agent_sdk.connectors.clickup_api.models.Task] | Any`
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

    `last_page: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `avatar: str | Any | None`
    :   The type of the None singleton.

    `color: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `members: list[airbyte_agent_sdk.connectors.clickup_api.models.TeamMembersItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
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

    `user: airbyte_agent_sdk.connectors.clickup_api.models.TeamMembersItemUser | Any`
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

    `color: str | Any | None`
    :   Avatar color

    `custom_role: dict[str, typing.Any] | Any | None`
    :   Custom role details

    `date_invited: str | Any | None`
    :   Date invited (Unix ms)

    `date_joined: str | Any | None`
    :   Date joined (Unix ms)

    `email: str | Any`
    :   Email address

    `id: int | Any`
    :   User ID

    `initials: str | Any | None`
    :   User initials

    `last_active: str | Any | None`
    :   Last active timestamp (Unix ms)

    `model_config`
    :   The type of the None singleton.

    `profile_picture: str | Any | None`
    :   Profile picture URL

    `role: int | Any | None`
    :   User role ID

    `role_key: str | Any | None`
    :   Role key name

    `role_subtype: int | Any | None`
    :   User role subtype

    `username: str | Any`
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

    `teams: list[airbyte_agent_sdk.connectors.clickup_api.models.Team] | Any`
    :   The type of the None singleton.

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

    `data: list[airbyte_agent_sdk.connectors.clickup_api.models.TimeEntry] | Any`
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

    `at: str | Any | None`
    :   The type of the None singleton.

    `billable: bool | Any`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `duration: str | Any`
    :   The type of the None singleton.

    `end: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start: str | Any`
    :   The type of the None singleton.

    `tags: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `task: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `user: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `wid: str | Any | None`
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

    `data: airbyte_agent_sdk.connectors.clickup_api.models.TimeEntry | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

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

    `color: str | Any | None`
    :   The type of the None singleton.

    `email: str | Any`
    :   The type of the None singleton.

    `global_font_support: bool | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `initials: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `profile_picture: str | Any | None`
    :   The type of the None singleton.

    `timezone: str | Any | None`
    :   The type of the None singleton.

    `username: str | Any`
    :   The type of the None singleton.

    `week_start_day: int | Any | None`
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

    `user: airbyte_agent_sdk.connectors.clickup_api.models.User | Any`
    :   The type of the None singleton.

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

    `columns: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `creator: int | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `date_protected: str | Any | None`
    :   The type of the None singleton.

    `divide: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `filters: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `grouping: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `orderindex: int | Any`
    :   The type of the None singleton.

    `parent: airbyte_agent_sdk.connectors.clickup_api.models.ViewParent | Any`
    :   The type of the None singleton.

    `protected: bool | Any | None`
    :   The type of the None singleton.

    `protected_by: int | Any | None`
    :   The type of the None singleton.

    `protected_note: str | Any | None`
    :   The type of the None singleton.

    `public: bool | Any`
    :   The type of the None singleton.

    `settings: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `sorting: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `team_sidebar: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `visibility: str | Any | None`
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

    `id: Any`
    :   Parent entity ID

    `model_config`
    :   The type of the None singleton.

    `type_: Any`
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

    `view: airbyte_agent_sdk.connectors.clickup_api.models.View | Any`
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

    `last_page: bool | Any | None`
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

    `default_view: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `required_views: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `views: list[airbyte_agent_sdk.connectors.clickup_api.models.View] | Any`
    :   The type of the None singleton.