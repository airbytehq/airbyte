---
id: airbyte_agent_sdk-connectors-github-models
title: airbyte_agent_sdk.connectors.github.models
---

Module airbyte_agent_sdk.connectors.github.models
=================================================
Pydantic models for github connector.

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

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[BranchesSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[CommentsSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[IssuesSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[OrganizationsSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[PullRequestsSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[RepositoriesSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[StargazersSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[TagsSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[TeamsSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.github.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[BranchesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BranchesSearchResult"></a>

`BranchesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CommentsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[IssuesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="IssuesSearchResult"></a>

`IssuesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[OrganizationsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrganizationsSearchResult"></a>

`OrganizationsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[PullRequestsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PullRequestsSearchResult"></a>

`PullRequestsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[RepositoriesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="RepositoriesSearchResult"></a>

`RepositoriesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[StargazersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="StargazersSearchResult"></a>

`StargazersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TagsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TeamsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="BranchesListResultMeta"></a>

`BranchesListResultMeta(**data: Any)`
:   Metadata for branches.Action.LIST operation
    
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

<a id="BranchesSearchData"></a>

`BranchesSearchData(**data: Any)`
:   Search result data for branches entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
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

    `body: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CommentResponse"></a>

`CommentResponse(**data: Any)`
:   CommentResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_association: str | Any`
    :   The type of the None singleton.

    `body: str | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `html_url: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `issue_url: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | Any`
    :   The type of the None singleton.

    `performed_via_github_app: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `reactions: airbyte_agent_sdk.connectors.github.models.CommentResponseReactions | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.github.models.CommentResponseUser | Any | None`
    :   The type of the None singleton.

<a id="CommentResponseReactions"></a>

`CommentResponseReactions(**data: Any)`
:   Reaction counts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `confused: int | Any`
    :   The type of the None singleton.

    `eyes: int | Any`
    :   The type of the None singleton.

    `field_1: int | Any`
    :   The type of the None singleton.

    `heart: int | Any`
    :   The type of the None singleton.

    `hooray: int | Any`
    :   The type of the None singleton.

    `laugh: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rocket: int | Any`
    :   The type of the None singleton.

    `total_count: int | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="CommentResponseUser"></a>

`CommentResponseUser(**data: Any)`
:   The user who created the comment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_url: str | Any`
    :   The type of the None singleton.

    `html_url: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `login: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | Any`
    :   The type of the None singleton.

    `site_admin: bool | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="CommentsListResultMeta"></a>

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

    `model_config`
    :   The type of the None singleton.

<a id="CommitsListResultMeta"></a>

`CommitsListResultMeta(**data: Any)`
:   Metadata for commits.Action.LIST operation
    
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

<a id="DiscussionsApiSearchResultMeta"></a>

`DiscussionsApiSearchResultMeta(**data: Any)`
:   Metadata for discussions.Action.API_SEARCH operation
    
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

    `total_count: int | Any`
    :   The type of the None singleton.

<a id="DiscussionsListResultMeta"></a>

`DiscussionsListResultMeta(**data: Any)`
:   Metadata for discussions.Action.LIST operation
    
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

<a id="GithubCheckResult"></a>

`GithubCheckResult(**data: Any)`
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

<a id="GithubExecuteResult"></a>

`GithubExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult[list[dict[str, Any]]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="GithubExecuteResultWithMeta"></a>

`GithubExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], BranchesListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], CommentsListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], CommitsListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], DiscussionsApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], DiscussionsListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], IssuesApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], IssuesListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], LabelsListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], MilestonesListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], OrgRepositoriesListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], OrganizationsListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], PrCommentsListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], ProjectItemsListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], ProjectsListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], PullRequestsApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], PullRequestsListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], ReleasesListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], RepositoriesApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], RepositoriesListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], ReviewsListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], StargazersListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], TagsListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], TeamsListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], UsersApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], UsersListResultMeta]
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta[list[dict[str, Any]], ViewerRepositoriesListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`GithubExecuteResultWithMeta[list[dict[str, Any]], BranchesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BranchesListResult"></a>

`BranchesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], CommentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CommentsListResult"></a>

`CommentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], CommitsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CommitsListResult"></a>

`CommitsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], DiscussionsApiSearchResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DiscussionsApiSearchResult"></a>

`DiscussionsApiSearchResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], DiscussionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DiscussionsListResult"></a>

`DiscussionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], IssuesApiSearchResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="IssuesApiSearchResult"></a>

`IssuesApiSearchResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], IssuesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="IssuesListResult"></a>

`IssuesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], LabelsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="LabelsListResult"></a>

`LabelsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], MilestonesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MilestonesListResult"></a>

`MilestonesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], OrgRepositoriesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrgRepositoriesListResult"></a>

`OrgRepositoriesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], OrganizationsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrganizationsListResult"></a>

`OrganizationsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], PrCommentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PrCommentsListResult"></a>

`PrCommentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], ProjectItemsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProjectItemsListResult"></a>

`ProjectItemsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], ProjectsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
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

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], PullRequestsApiSearchResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PullRequestsApiSearchResult"></a>

`PullRequestsApiSearchResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], PullRequestsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PullRequestsListResult"></a>

`PullRequestsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], ReleasesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ReleasesListResult"></a>

`ReleasesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], RepositoriesApiSearchResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="RepositoriesApiSearchResult"></a>

`RepositoriesApiSearchResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], RepositoriesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="RepositoriesListResult"></a>

`RepositoriesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], ReviewsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ReviewsListResult"></a>

`ReviewsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], StargazersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="StargazersListResult"></a>

`StargazersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], TagsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TagsListResult"></a>

`TagsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], TeamsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TeamsListResult"></a>

`TeamsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], UsersApiSearchResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UsersApiSearchResult"></a>

`UsersApiSearchResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], UsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
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

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResultWithMeta[list[dict[str, Any]], ViewerRepositoriesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ViewerRepositoriesListResult"></a>

`ViewerRepositoriesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GithubExecuteResult[list[dict[str, Any]]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DirectoryContentListResult"></a>

`DirectoryContentListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.GithubExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GithubOauth2AuthConfig"></a>

`GithubOauth2AuthConfig(**data: Any)`
:   OAuth 2
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   OAuth 2.0 access token

    `model_config`
    :   The type of the None singleton.

<a id="GithubPersonalAccessTokenAuthConfig"></a>

`GithubPersonalAccessTokenAuthConfig(**data: Any)`
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
    :   GitHub personal access token (fine-grained or classic)

<a id="GithubReplicationConfig"></a>

`GithubReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from GitHub.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `repositories: str`
    :   List of GitHub organizations/repositories, e.g. `airbytehq/airbyte` for single repository, `airbytehq/*` for all repositories from organization

<a id="IssueCreateParams"></a>

`IssueCreateParams(**data: Any)`
:   IssueCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignees: list[str] | Any`
    :   The type of the None singleton.

    `body: str | Any`
    :   The type of the None singleton.

    `labels: list[str] | Any`
    :   The type of the None singleton.

    `milestone: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

<a id="IssueResponse"></a>

`IssueResponse(**data: Any)`
:   IssueResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active_lock_reason: str | Any | None`
    :   The type of the None singleton.

    `assignee: airbyte_agent_sdk.connectors.github.models.IssueResponseAssignee | Any | None`
    :   The type of the None singleton.

    `assignees: list[airbyte_agent_sdk.connectors.github.models.IssueResponseAssigneesItem] | Any`
    :   The type of the None singleton.

    `author_association: str | Any`
    :   The type of the None singleton.

    `body: str | Any | None`
    :   The type of the None singleton.

    `closed_at: str | Any | None`
    :   The type of the None singleton.

    `closed_by: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `comments: int | Any`
    :   The type of the None singleton.

    `comments_url: str | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `events_url: str | Any`
    :   The type of the None singleton.

    `html_url: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `issue_dependencies_summary: airbyte_agent_sdk.connectors.github.models.IssueResponseIssueDependenciesSummary | Any`
    :   The type of the None singleton.

    `issue_field_values: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `labels: list[airbyte_agent_sdk.connectors.github.models.IssueResponseLabelsItem] | Any`
    :   The type of the None singleton.

    `labels_url: str | Any`
    :   The type of the None singleton.

    `locked: bool | Any`
    :   The type of the None singleton.

    `milestone: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | Any`
    :   The type of the None singleton.

    `number: int | Any`
    :   The type of the None singleton.

    `performed_via_github_app: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `pinned_comment: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `reactions: airbyte_agent_sdk.connectors.github.models.IssueResponseReactions | Any`
    :   The type of the None singleton.

    `repository_url: str | Any`
    :   The type of the None singleton.

    `state: str | Any`
    :   The type of the None singleton.

    `state_reason: str | Any | None`
    :   The type of the None singleton.

    `sub_issues_summary: airbyte_agent_sdk.connectors.github.models.IssueResponseSubIssuesSummary | Any`
    :   The type of the None singleton.

    `timeline_url: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `type_: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.github.models.IssueResponseUser | Any | None`
    :   The type of the None singleton.

<a id="IssueResponseAssignee"></a>

`IssueResponseAssignee(**data: Any)`
:   Primary user assigned to this issue
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_url: str | Any`
    :   The type of the None singleton.

    `html_url: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `login: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | Any`
    :   The type of the None singleton.

    `site_admin: bool | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="IssueResponseAssigneesItem"></a>

`IssueResponseAssigneesItem(**data: Any)`
:   Nested schema for IssueResponse.assignees_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_url: str | Any`
    :   The type of the None singleton.

    `html_url: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `login: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | Any`
    :   The type of the None singleton.

    `site_admin: bool | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="IssueResponseIssueDependenciesSummary"></a>

`IssueResponseIssueDependenciesSummary(**data: Any)`
:   Summary of issue dependencies
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `blocked_by: int | Any`
    :   The type of the None singleton.

    `blocking: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_blocked_by: int | Any`
    :   The type of the None singleton.

    `total_blocking: int | Any`
    :   The type of the None singleton.

<a id="IssueResponseLabelsItem"></a>

`IssueResponseLabelsItem(**data: Any)`
:   Nested schema for IssueResponse.labels_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | Any`
    :   The type of the None singleton.

    `default: bool | Any`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `node_id: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="IssueResponseReactions"></a>

`IssueResponseReactions(**data: Any)`
:   Reaction counts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `confused: int | Any`
    :   The type of the None singleton.

    `eyes: int | Any`
    :   The type of the None singleton.

    `field_1: int | Any`
    :   The type of the None singleton.

    `heart: int | Any`
    :   The type of the None singleton.

    `hooray: int | Any`
    :   The type of the None singleton.

    `laugh: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rocket: int | Any`
    :   The type of the None singleton.

    `total_count: int | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="IssueResponseSubIssuesSummary"></a>

`IssueResponseSubIssuesSummary(**data: Any)`
:   Summary of sub-issues
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `completed: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `percent_completed: int | Any`
    :   The type of the None singleton.

    `total: int | Any`
    :   The type of the None singleton.

<a id="IssueResponseUser"></a>

`IssueResponseUser(**data: Any)`
:   The user who created the issue
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_url: str | Any`
    :   The type of the None singleton.

    `html_url: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `login: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | Any`
    :   The type of the None singleton.

    `site_admin: bool | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="IssueUpdateParams"></a>

`IssueUpdateParams(**data: Any)`
:   IssueUpdateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignees: list[str] | Any`
    :   The type of the None singleton.

    `body: str | Any`
    :   The type of the None singleton.

    `labels: list[str] | Any`
    :   The type of the None singleton.

    `milestone: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `state: str | Any`
    :   The type of the None singleton.

    `state_reason: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

<a id="IssuesApiSearchResultMeta"></a>

`IssuesApiSearchResultMeta(**data: Any)`
:   Metadata for issues.Action.API_SEARCH operation
    
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

    `total_count: int | Any`
    :   The type of the None singleton.

<a id="IssuesListResultMeta"></a>

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

<a id="IssuesSearchData"></a>

`IssuesSearchData(**data: Any)`
:   Search result data for issues entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="LabelsListResultMeta"></a>

`LabelsListResultMeta(**data: Any)`
:   Metadata for labels.Action.LIST operation
    
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

<a id="MilestonesListResultMeta"></a>

`MilestonesListResultMeta(**data: Any)`
:   Metadata for milestones.Action.LIST operation
    
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

<a id="OrgRepositoriesListResultMeta"></a>

`OrgRepositoriesListResultMeta(**data: Any)`
:   Metadata for org_repositories.Action.LIST operation
    
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

<a id="OrganizationsListResultMeta"></a>

`OrganizationsListResultMeta(**data: Any)`
:   Metadata for organizations.Action.LIST operation
    
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

<a id="OrganizationsSearchData"></a>

`OrganizationsSearchData(**data: Any)`
:   Search result data for organizations entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PrCommentsListResultMeta"></a>

`PrCommentsListResultMeta(**data: Any)`
:   Metadata for pr_comments.Action.LIST operation
    
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

<a id="ProjectItemsListResultMeta"></a>

`ProjectItemsListResultMeta(**data: Any)`
:   Metadata for project_items.Action.LIST operation
    
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

    `end_cursor: str | Any | None`
    :   The type of the None singleton.

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="PullRequestCreateParams"></a>

`PullRequestCreateParams(**data: Any)`
:   PullRequestCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `base: str | Any`
    :   The type of the None singleton.

    `body: str | Any`
    :   The type of the None singleton.

    `draft: bool | Any`
    :   The type of the None singleton.

    `head: str | Any`
    :   The type of the None singleton.

    `maintainer_can_modify: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

<a id="PullRequestResponse"></a>

`PullRequestResponse(**data: Any)`
:   PullRequestResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `additions: int | Any`
    :   The type of the None singleton.

    `assignees: list[airbyte_agent_sdk.connectors.github.models.PullRequestResponseAssigneesItem] | Any`
    :   The type of the None singleton.

    `author_association: str | Any`
    :   The type of the None singleton.

    `base: airbyte_agent_sdk.connectors.github.models.PullRequestResponseBase | Any`
    :   The type of the None singleton.

    `body: str | Any | None`
    :   The type of the None singleton.

    `changed_files: int | Any`
    :   The type of the None singleton.

    `closed_at: str | Any | None`
    :   The type of the None singleton.

    `comments: int | Any`
    :   The type of the None singleton.

    `commits: int | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `deletions: int | Any`
    :   The type of the None singleton.

    `diff_url: str | Any`
    :   The type of the None singleton.

    `draft: bool | Any`
    :   The type of the None singleton.

    `head: airbyte_agent_sdk.connectors.github.models.PullRequestResponseHead | Any`
    :   The type of the None singleton.

    `html_url: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `labels: list[airbyte_agent_sdk.connectors.github.models.PullRequestResponseLabelsItem] | Any`
    :   The type of the None singleton.

    `locked: bool | Any`
    :   The type of the None singleton.

    `merge_commit_sha: str | Any | None`
    :   The type of the None singleton.

    `merged_at: str | Any | None`
    :   The type of the None singleton.

    `milestone: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | Any`
    :   The type of the None singleton.

    `number: int | Any`
    :   The type of the None singleton.

    `patch_url: str | Any`
    :   The type of the None singleton.

    `requested_reviewers: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `review_comments: int | Any`
    :   The type of the None singleton.

    `state: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.github.models.PullRequestResponseUser | Any | None`
    :   The type of the None singleton.

<a id="PullRequestResponseAssigneesItem"></a>

`PullRequestResponseAssigneesItem(**data: Any)`
:   Nested schema for PullRequestResponse.assignees_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_url: str | Any`
    :   The type of the None singleton.

    `html_url: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `login: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | Any`
    :   The type of the None singleton.

    `site_admin: bool | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="PullRequestResponseBase"></a>

`PullRequestResponseBase(**data: Any)`
:   The base branch
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `label: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ref: str | Any`
    :   The type of the None singleton.

    `sha: str | Any`
    :   The type of the None singleton.

<a id="PullRequestResponseHead"></a>

`PullRequestResponseHead(**data: Any)`
:   The head branch
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `label: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ref: str | Any`
    :   The type of the None singleton.

    `sha: str | Any`
    :   The type of the None singleton.

<a id="PullRequestResponseLabelsItem"></a>

`PullRequestResponseLabelsItem(**data: Any)`
:   Nested schema for PullRequestResponse.labels_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | Any`
    :   The type of the None singleton.

    `default: bool | Any`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `node_id: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="PullRequestResponseUser"></a>

`PullRequestResponseUser(**data: Any)`
:   The user who created the pull request
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_url: str | Any`
    :   The type of the None singleton.

    `html_url: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `login: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | Any`
    :   The type of the None singleton.

    `site_admin: bool | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="PullRequestsApiSearchResultMeta"></a>

`PullRequestsApiSearchResultMeta(**data: Any)`
:   Metadata for pull_requests.Action.API_SEARCH operation
    
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

    `total_count: int | Any`
    :   The type of the None singleton.

<a id="PullRequestsListResultMeta"></a>

`PullRequestsListResultMeta(**data: Any)`
:   Metadata for pull_requests.Action.LIST operation
    
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

<a id="PullRequestsSearchData"></a>

`PullRequestsSearchData(**data: Any)`
:   Search result data for pull_requests entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ReleasesListResultMeta"></a>

`ReleasesListResultMeta(**data: Any)`
:   Metadata for releases.Action.LIST operation
    
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

<a id="RepositoriesApiSearchResultMeta"></a>

`RepositoriesApiSearchResultMeta(**data: Any)`
:   Metadata for repositories.Action.API_SEARCH operation
    
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

    `total_count: int | Any`
    :   The type of the None singleton.

<a id="RepositoriesListResultMeta"></a>

`RepositoriesListResultMeta(**data: Any)`
:   Metadata for repositories.Action.LIST operation
    
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

<a id="RepositoriesSearchData"></a>

`RepositoriesSearchData(**data: Any)`
:   Search result data for repositories entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ReviewsListResultMeta"></a>

`ReviewsListResultMeta(**data: Any)`
:   Metadata for reviews.Action.LIST operation
    
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

<a id="StargazersListResultMeta"></a>

`StargazersListResultMeta(**data: Any)`
:   Metadata for stargazers.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `end_cursor: str | Any`
    :   The type of the None singleton.

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="StargazersSearchData"></a>

`StargazersSearchData(**data: Any)`
:   Search result data for stargazers entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TagsListResultMeta"></a>

`TagsListResultMeta(**data: Any)`
:   Metadata for tags.Action.LIST operation
    
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

    `model_config`
    :   The type of the None singleton.

<a id="TeamsListResultMeta"></a>

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

    `model_config`
    :   The type of the None singleton.

<a id="UsersApiSearchResultMeta"></a>

`UsersApiSearchResultMeta(**data: Any)`
:   Metadata for users.Action.API_SEARCH operation
    
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

    `total_count: int | Any`
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

    `end_cursor: str | Any | None`
    :   The type of the None singleton.

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
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

    `model_config`
    :   The type of the None singleton.

<a id="ViewerRepositoriesListResultMeta"></a>

`ViewerRepositoriesListResultMeta(**data: Any)`
:   Metadata for viewer_repositories.Action.LIST operation
    
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