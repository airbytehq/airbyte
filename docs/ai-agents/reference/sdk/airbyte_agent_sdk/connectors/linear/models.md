---
id: airbyte_agent_sdk-connectors-linear-models
title: airbyte_agent_sdk.connectors.linear.models
---

Module airbyte_agent_sdk.connectors.linear.models
=================================================
Pydantic models for linear connector.

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

    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult[CommentsSearchData]
    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult[IssuesSearchData]
    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult[ProjectsSearchData]
    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult[TeamsSearchData]
    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult[UsersSearchData]
    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult[WorkflowStatesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.linear.models.AirbyteSearchMeta`
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

    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`CommentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[IssuesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IssuesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ProjectsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TeamsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`TeamsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[WorkflowStatesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`WorkflowStatesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`Comment(**data: Any)`
:   Linear comment object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body: str | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `issue: Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `user: Any`
    :   The type of the None singleton.

`CommentCreateParams(**data: Any)`
:   Parameters for creating a comment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body: str | Any`
    :   The type of the None singleton.

    `issue_id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`CommentCreateResponse(**data: Any)`
:   GraphQL response for comment creation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.linear.models.CommentCreateResponseData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`CommentCreateResponseData(**data: Any)`
:   Nested schema for CommentCreateResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `comment_create: airbyte_agent_sdk.connectors.linear.models.CommentMutationPayload | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`CommentMutationPayload(**data: Any)`
:   Comment mutation result
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `comment: airbyte_agent_sdk.connectors.linear.models.Comment | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `success: bool | Any`
    :   The type of the None singleton.

`CommentResponse(**data: Any)`
:   GraphQL response for single comment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.linear.models.CommentResponseData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`CommentResponseData(**data: Any)`
:   Nested schema for CommentResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `comment: airbyte_agent_sdk.connectors.linear.models.Comment | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`CommentUpdateParams(**data: Any)`
:   Parameters for updating a comment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`CommentUpdateResponse(**data: Any)`
:   GraphQL response for comment update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.linear.models.CommentUpdateResponseData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`CommentUpdateResponseData(**data: Any)`
:   Nested schema for CommentUpdateResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `comment_update: airbyte_agent_sdk.connectors.linear.models.CommentMutationPayload | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`CommentsListResponse(**data: Any)`
:   GraphQL response for comments list
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.linear.models.CommentsListResponseData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`CommentsListResponseData(**data: Any)`
:   Nested schema for CommentsListResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `issue: airbyte_agent_sdk.connectors.linear.models.CommentsListResponseDataIssue | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`CommentsListResponseDataIssue(**data: Any)`
:   Nested schema for CommentsListResponseData.issue
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `comments: airbyte_agent_sdk.connectors.linear.models.CommentsListResponseDataIssueComments | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`CommentsListResponseDataIssueComments(**data: Any)`
:   Nested schema for CommentsListResponseDataIssue.comments
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `nodes: list[airbyte_agent_sdk.connectors.linear.models.Comment] | Any`
    :   The type of the None singleton.

    `page_info: airbyte_agent_sdk.connectors.linear.models.CommentsListResponseDataIssueCommentsPageinfo | Any`
    :   Pagination information

`CommentsListResponseDataIssueCommentsPageinfo(**data: Any)`
:   Pagination information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_cursor: str | Any | None`
    :   Cursor to fetch next page

    `has_next_page: bool | Any`
    :   Whether there are more items available

    `model_config`
    :   The type of the None singleton.

`CommentsListResultMeta(**data: Any)`
:   Metadata for comments.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_cursor: str | Any | None`
    :   The type of the None singleton.

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`CommentsSearchData(**data: Any)`
:   Search result data for comments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body: str | None`
    :   The type of the None singleton.

    `body_data: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `edited_at: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `issue: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `issue_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `parent: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `parent_comment_id: str | None`
    :   The type of the None singleton.

    `resolving_comment_id: str | None`
    :   The type of the None singleton.

    `resolving_user_id: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

    `user: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `user_id: str | None`
    :   The type of the None singleton.

`Issue(**data: Any)`
:   Linear issue object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee: Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `description: Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `priority: Any`
    :   The type of the None singleton.

    `project: Any`
    :   The type of the None singleton.

    `state: Any`
    :   The type of the None singleton.

    `team: Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

`IssueCreateParams(**data: Any)`
:   Parameters for creating an issue
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `priority: int | Any`
    :   The type of the None singleton.

    `project_id: str | Any`
    :   The type of the None singleton.

    `state_id: str | Any`
    :   The type of the None singleton.

    `team_id: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

`IssueCreateResponse(**data: Any)`
:   GraphQL response for issue creation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.linear.models.IssueCreateResponseData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`IssueCreateResponseData(**data: Any)`
:   Nested schema for IssueCreateResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `issue_create: airbyte_agent_sdk.connectors.linear.models.IssueMutationPayload | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`IssueMutationPayload(**data: Any)`
:   Issue mutation result
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `issue: airbyte_agent_sdk.connectors.linear.models.IssueWithState | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `success: bool | Any`
    :   The type of the None singleton.

`IssueResponse(**data: Any)`
:   GraphQL response for single issue
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.linear.models.IssueResponseData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`IssueResponseData(**data: Any)`
:   Nested schema for IssueResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `issue: airbyte_agent_sdk.connectors.linear.models.Issue | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`IssueUpdateParams(**data: Any)`
:   Parameters for updating an issue. All fields except id are optional for partial updates.
    To assign a user, provide assigneeId with the user's ID (get user IDs from the users list).
    To unassign the current user, set assigneeId to null.
    Omit assigneeId to leave the current assignee unchanged.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee_id: str | Any`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `priority: int | Any`
    :   The type of the None singleton.

    `project_id: str | Any`
    :   The type of the None singleton.

    `state_id: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

`IssueUpdateResponse(**data: Any)`
:   GraphQL response for issue update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.linear.models.IssueUpdateResponseData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`IssueUpdateResponseData(**data: Any)`
:   Nested schema for IssueUpdateResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `issue_update: airbyte_agent_sdk.connectors.linear.models.IssueMutationPayload | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`IssueWithState(**data: Any)`
:   Issue object with state ID and assignee ID included
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee: Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `description: Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `priority: Any`
    :   The type of the None singleton.

    `project: Any`
    :   The type of the None singleton.

    `state: Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

`IssuesListResponse(**data: Any)`
:   GraphQL response for issues list
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.linear.models.IssuesListResponseData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`IssuesListResponseData(**data: Any)`
:   Nested schema for IssuesListResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `issues: airbyte_agent_sdk.connectors.linear.models.IssuesListResponseDataIssues | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`IssuesListResponseDataIssues(**data: Any)`
:   Nested schema for IssuesListResponseData.issues
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `nodes: list[airbyte_agent_sdk.connectors.linear.models.Issue] | Any`
    :   The type of the None singleton.

    `page_info: airbyte_agent_sdk.connectors.linear.models.IssuesListResponseDataIssuesPageinfo | Any`
    :   Pagination information

`IssuesListResponseDataIssuesPageinfo(**data: Any)`
:   Pagination information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_cursor: str | Any | None`
    :   Cursor to fetch next page

    `has_next_page: bool | Any`
    :   Whether there are more items available

    `model_config`
    :   The type of the None singleton.

`IssuesListResultMeta(**data: Any)`
:   Metadata for issues.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_cursor: str | Any | None`
    :   The type of the None singleton.

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`IssuesSearchData(**data: Any)`
:   Search result data for issues entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `added_to_cycle_at: str | None`
    :   The type of the None singleton.

    `added_to_project_at: str | None`
    :   The type of the None singleton.

    `added_to_team_at: str | None`
    :   The type of the None singleton.

    `assignee: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `assignee_id: str | None`
    :   The type of the None singleton.

    `attachment_ids: list[typing.Any] | None`
    :   The type of the None singleton.

    `attachments: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `branch_name: str | None`
    :   The type of the None singleton.

    `canceled_at: str | None`
    :   The type of the None singleton.

    `completed_at: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `creator: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `creator_id: str | None`
    :   The type of the None singleton.

    `customer_ticket_count: float | None`
    :   The type of the None singleton.

    `cycle: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `cycle_id: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `description_state: str | None`
    :   The type of the None singleton.

    `due_date: str | None`
    :   The type of the None singleton.

    `estimate: float | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `identifier: str | None`
    :   The type of the None singleton.

    `integration_source_type: str | None`
    :   The type of the None singleton.

    `label_ids: list[typing.Any] | None`
    :   The type of the None singleton.

    `labels: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `milestone_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `number: float | None`
    :   The type of the None singleton.

    `parent: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `parent_id: str | None`
    :   The type of the None singleton.

    `previous_identifiers: list[typing.Any] | None`
    :   The type of the None singleton.

    `priority: float | None`
    :   The type of the None singleton.

    `priority_label: str | None`
    :   The type of the None singleton.

    `priority_sort_order: float | None`
    :   The type of the None singleton.

    `project: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `project_id: str | None`
    :   The type of the None singleton.

    `project_milestone: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `reaction_data: list[typing.Any] | None`
    :   The type of the None singleton.

    `relation_ids: list[typing.Any] | None`
    :   The type of the None singleton.

    `relations: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `sla_type: str | None`
    :   The type of the None singleton.

    `sort_order: float | None`
    :   The type of the None singleton.

    `source_comment_id: str | None`
    :   The type of the None singleton.

    `started_at: str | None`
    :   The type of the None singleton.

    `state: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `state_id: str | None`
    :   The type of the None singleton.

    `sub_issue_sort_order: float | None`
    :   The type of the None singleton.

    `subscriber_ids: list[typing.Any] | None`
    :   The type of the None singleton.

    `subscribers: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `team: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `team_id: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

`LinearAuthConfig(**data: Any)`
:   Linear API Key Authentication - Authenticate using your Linear API key
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your Linear API key from Settings > API > Personal API keys

    `model_config`
    :   The type of the None singleton.

`LinearCheckResult(**data: Any)`
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

`LinearExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

`LinearExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta[list[Comment], CommentsListResultMeta]
    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta[list[Issue], IssuesListResultMeta]
    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta[list[Project], ProjectsListResultMeta]
    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta[list[Team], TeamsListResultMeta]
    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta[list[User], UsersListResultMeta]
    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta[list[WorkflowState], WorkflowStatesListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`LinearExecuteResultWithMeta[list[Comment], CommentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`CommentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`LinearExecuteResultWithMeta[list[Issue], IssuesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IssuesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`LinearExecuteResultWithMeta[list[Project], ProjectsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResult
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

    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`LinearExecuteResultWithMeta[list[Team], TeamsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`TeamsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`LinearExecuteResultWithMeta[list[User], UsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResult
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

    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`LinearExecuteResultWithMeta[list[WorkflowState], WorkflowStatesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`WorkflowStatesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.linear.models.LinearExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`Project(**data: Any)`
:   Linear project object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any`
    :   The type of the None singleton.

    `description: Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `lead: Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `start_date: Any`
    :   The type of the None singleton.

    `state: Any`
    :   The type of the None singleton.

    `target_date: Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

`ProjectCreateParams(**data: Any)`
:   Parameters for creating a project
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | Any`
    :   The type of the None singleton.

    `lead_id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `start_date: str | Any`
    :   The type of the None singleton.

    `state: str | Any`
    :   The type of the None singleton.

    `target_date: str | Any`
    :   The type of the None singleton.

    `team_ids: list[str] | Any`
    :   The type of the None singleton.

`ProjectCreateResponse(**data: Any)`
:   GraphQL response for project creation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.linear.models.ProjectCreateResponseData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`ProjectCreateResponseData(**data: Any)`
:   Nested schema for ProjectCreateResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `project_create: airbyte_agent_sdk.connectors.linear.models.ProjectMutationPayload | Any`
    :   The type of the None singleton.

`ProjectMutationPayload(**data: Any)`
:   Project mutation result
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `project: airbyte_agent_sdk.connectors.linear.models.Project | Any`
    :   The type of the None singleton.

    `success: bool | Any`
    :   The type of the None singleton.

`ProjectResponse(**data: Any)`
:   GraphQL response for single project
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.linear.models.ProjectResponseData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`ProjectResponseData(**data: Any)`
:   Nested schema for ProjectResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `project: airbyte_agent_sdk.connectors.linear.models.Project | Any`
    :   The type of the None singleton.

`ProjectUpdateParams(**data: Any)`
:   Parameters for updating a project. All fields except id are optional for partial updates.
    Use this to rename projects, change descriptions, update dates, or change the project state.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `lead_id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `start_date: str | Any`
    :   The type of the None singleton.

    `state: str | Any`
    :   The type of the None singleton.

    `target_date: str | Any`
    :   The type of the None singleton.

`ProjectUpdateResponse(**data: Any)`
:   GraphQL response for project update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.linear.models.ProjectUpdateResponseData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`ProjectUpdateResponseData(**data: Any)`
:   Nested schema for ProjectUpdateResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `project_update: airbyte_agent_sdk.connectors.linear.models.ProjectMutationPayload | Any`
    :   The type of the None singleton.

`ProjectsListResponse(**data: Any)`
:   GraphQL response for projects list
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.linear.models.ProjectsListResponseData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`ProjectsListResponseData(**data: Any)`
:   Nested schema for ProjectsListResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `projects: airbyte_agent_sdk.connectors.linear.models.ProjectsListResponseDataProjects | Any`
    :   The type of the None singleton.

`ProjectsListResponseDataProjects(**data: Any)`
:   Nested schema for ProjectsListResponseData.projects
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `nodes: list[airbyte_agent_sdk.connectors.linear.models.Project] | Any`
    :   The type of the None singleton.

    `page_info: airbyte_agent_sdk.connectors.linear.models.ProjectsListResponseDataProjectsPageinfo | Any`
    :   Pagination information

`ProjectsListResponseDataProjectsPageinfo(**data: Any)`
:   Pagination information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_cursor: str | Any | None`
    :   Cursor to fetch next page

    `has_next_page: bool | Any`
    :   Whether there are more items available

    `model_config`
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

    `end_cursor: str | Any | None`
    :   The type of the None singleton.

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
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

    `canceled_at: str | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `completed_at: str | None`
    :   The type of the None singleton.

    `completed_issue_count_history: list[typing.Any] | None`
    :   The type of the None singleton.

    `completed_scope_history: list[typing.Any] | None`
    :   The type of the None singleton.

    `content: str | None`
    :   The type of the None singleton.

    `content_state: str | None`
    :   The type of the None singleton.

    `converted_from_issue: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `converted_from_issue_id: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `creator: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `creator_id: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `health: str | None`
    :   The type of the None singleton.

    `health_updated_at: str | None`
    :   The type of the None singleton.

    `icon: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `in_progress_scope_history: list[typing.Any] | None`
    :   The type of the None singleton.

    `issue_count_history: list[typing.Any] | None`
    :   The type of the None singleton.

    `lead: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `lead_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `priority: float | None`
    :   The type of the None singleton.

    `priority_sort_order: float | None`
    :   The type of the None singleton.

    `progress: float | None`
    :   The type of the None singleton.

    `scope: float | None`
    :   The type of the None singleton.

    `scope_history: list[typing.Any] | None`
    :   The type of the None singleton.

    `slug_id: str | None`
    :   The type of the None singleton.

    `sort_order: float | None`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The type of the None singleton.

    `started_at: str | None`
    :   The type of the None singleton.

    `status: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `status_id: str | None`
    :   The type of the None singleton.

    `target_date: str | None`
    :   The type of the None singleton.

    `team_ids: list[typing.Any] | None`
    :   The type of the None singleton.

    `teams: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `update_reminders_day: str | None`
    :   The type of the None singleton.

    `update_reminders_hour: float | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

`Team(**data: Any)`
:   Linear team object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any`
    :   The type of the None singleton.

    `description: Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `key: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `timezone: Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

`TeamResponse(**data: Any)`
:   GraphQL response for single team
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.linear.models.TeamResponseData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`TeamResponseData(**data: Any)`
:   Nested schema for TeamResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `team: airbyte_agent_sdk.connectors.linear.models.Team | Any`
    :   The type of the None singleton.

`TeamsListResponse(**data: Any)`
:   GraphQL response for teams list
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.linear.models.TeamsListResponseData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`TeamsListResponseData(**data: Any)`
:   Nested schema for TeamsListResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `teams: airbyte_agent_sdk.connectors.linear.models.TeamsListResponseDataTeams | Any`
    :   The type of the None singleton.

`TeamsListResponseDataTeams(**data: Any)`
:   Nested schema for TeamsListResponseData.teams
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `nodes: list[airbyte_agent_sdk.connectors.linear.models.Team] | Any`
    :   The type of the None singleton.

    `page_info: airbyte_agent_sdk.connectors.linear.models.TeamsListResponseDataTeamsPageinfo | Any`
    :   Pagination information

`TeamsListResponseDataTeamsPageinfo(**data: Any)`
:   Pagination information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_cursor: str | Any | None`
    :   Cursor to fetch next page

    `has_next_page: bool | Any`
    :   Whether there are more items available

    `model_config`
    :   The type of the None singleton.

`TeamsListResultMeta(**data: Any)`
:   Metadata for teams.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_cursor: str | Any | None`
    :   The type of the None singleton.

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`TeamsSearchData(**data: Any)`
:   Search result data for teams entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active_cycle: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `active_cycle_id: str | None`
    :   The type of the None singleton.

    `auto_archive_period: float | None`
    :   The type of the None singleton.

    `auto_close_period: float | None`
    :   The type of the None singleton.

    `auto_close_state_id: str | None`
    :   The type of the None singleton.

    `color: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `cycle_calender_url: str | None`
    :   The type of the None singleton.

    `cycle_cooldown_time: float | None`
    :   The type of the None singleton.

    `cycle_duration: float | None`
    :   The type of the None singleton.

    `cycle_issue_auto_assign_completed: bool | None`
    :   The type of the None singleton.

    `cycle_issue_auto_assign_started: bool | None`
    :   The type of the None singleton.

    `cycle_lock_to_active: bool | None`
    :   The type of the None singleton.

    `cycle_start_day: float | None`
    :   The type of the None singleton.

    `cycles_enabled: bool | None`
    :   The type of the None singleton.

    `default_issue_estimate: float | None`
    :   The type of the None singleton.

    `default_issue_state: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `default_issue_state_id: str | None`
    :   The type of the None singleton.

    `group_issue_history: bool | None`
    :   The type of the None singleton.

    `icon: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `invite_hash: str | None`
    :   The type of the None singleton.

    `issue_count: float | None`
    :   The type of the None singleton.

    `issue_estimation_allow_zero: bool | None`
    :   The type of the None singleton.

    `issue_estimation_extended: bool | None`
    :   The type of the None singleton.

    `issue_estimation_type: str | None`
    :   The type of the None singleton.

    `key: str | None`
    :   The type of the None singleton.

    `marked_as_duplicate_workflow_state: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `marked_as_duplicate_workflow_state_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `parent_team_id: str | None`
    :   The type of the None singleton.

    `private: bool | None`
    :   The type of the None singleton.

    `require_priority_to_leave_triage: bool | None`
    :   The type of the None singleton.

    `scim_managed: bool | None`
    :   The type of the None singleton.

    `set_issue_sort_order_on_state_change: str | None`
    :   The type of the None singleton.

    `timezone: str | None`
    :   The type of the None singleton.

    `triage_enabled: bool | None`
    :   The type of the None singleton.

    `triage_issue_state_id: str | None`
    :   The type of the None singleton.

    `upcoming_cycle_count: float | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

`User(**data: Any)`
:   Linear user object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | Any`
    :   The type of the None singleton.

    `admin: bool | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `display_name: Any`
    :   The type of the None singleton.

    `email: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

`UserResponse(**data: Any)`
:   GraphQL response for single user
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.linear.models.UserResponseData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`UserResponseData(**data: Any)`
:   Nested schema for UserResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.linear.models.User | Any`
    :   The type of the None singleton.

`UsersListResponse(**data: Any)`
:   GraphQL response for users list
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.linear.models.UsersListResponseData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`UsersListResponseData(**data: Any)`
:   Nested schema for UsersListResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `users: airbyte_agent_sdk.connectors.linear.models.UsersListResponseDataUsers | Any`
    :   The type of the None singleton.

`UsersListResponseDataUsers(**data: Any)`
:   Nested schema for UsersListResponseData.users
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `nodes: list[airbyte_agent_sdk.connectors.linear.models.User] | Any`
    :   The type of the None singleton.

    `page_info: airbyte_agent_sdk.connectors.linear.models.UsersListResponseDataUsersPageinfo | Any`
    :   Pagination information

`UsersListResponseDataUsersPageinfo(**data: Any)`
:   Pagination information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_cursor: str | Any | None`
    :   Cursor to fetch next page

    `has_next_page: bool | Any`
    :   Whether there are more items available

    `model_config`
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

    `end_cursor: str | Any | None`
    :   The type of the None singleton.

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
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

    `active: bool | None`
    :   The type of the None singleton.

    `admin: bool | None`
    :   The type of the None singleton.

    `avatar_background_color: str | None`
    :   The type of the None singleton.

    `avatar_url: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `created_issue_count: float | None`
    :   The type of the None singleton.

    `display_name: str | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `guest: bool | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `initials: str | None`
    :   The type of the None singleton.

    `invite_hash: str | None`
    :   The type of the None singleton.

    `is_me: bool | None`
    :   The type of the None singleton.

    `last_seen: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `team_ids: list[typing.Any] | None`
    :   The type of the None singleton.

    `teams: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `timezone: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

`WorkflowState(**data: Any)`
:   Linear workflow state object representing a status in a team's workflow
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `position: Any`
    :   The type of the None singleton.

    `team: Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

`WorkflowStatesListResponse(**data: Any)`
:   GraphQL response for workflow states list
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.linear.models.WorkflowStatesListResponseData | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`WorkflowStatesListResponseData(**data: Any)`
:   Nested schema for WorkflowStatesListResponse.data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `workflow_states: airbyte_agent_sdk.connectors.linear.models.WorkflowStatesListResponseDataWorkflowstates | Any`
    :   The type of the None singleton.

`WorkflowStatesListResponseDataWorkflowstates(**data: Any)`
:   Nested schema for WorkflowStatesListResponseData.workflowStates
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `nodes: list[airbyte_agent_sdk.connectors.linear.models.WorkflowState] | Any`
    :   The type of the None singleton.

    `page_info: airbyte_agent_sdk.connectors.linear.models.WorkflowStatesListResponseDataWorkflowstatesPageinfo | Any`
    :   Pagination information

`WorkflowStatesListResponseDataWorkflowstatesPageinfo(**data: Any)`
:   Pagination information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_cursor: str | Any | None`
    :   Cursor to fetch next page

    `has_next_page: bool | Any`
    :   Whether there are more items available

    `model_config`
    :   The type of the None singleton.

`WorkflowStatesListResultMeta(**data: Any)`
:   Metadata for workflow_states.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_cursor: str | Any | None`
    :   The type of the None singleton.

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`WorkflowStatesSearchData(**data: Any)`
:   Search result data for workflow_states entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `inherited_from_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `position: float | None`
    :   The type of the None singleton.

    `team: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `team_id: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.