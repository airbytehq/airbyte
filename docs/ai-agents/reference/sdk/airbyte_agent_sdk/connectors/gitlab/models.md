---
id: airbyte_agent_sdk-connectors-gitlab-models
title: airbyte_agent_sdk.connectors.gitlab.models
---

Module airbyte_agent_sdk.connectors.gitlab.models
=================================================
Pydantic models for gitlab connector.

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

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[BranchesSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[CommitsSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[GroupMembersSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[GroupMilestonesSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[GroupsSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[IssuesSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[MergeRequestsSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[PipelinesSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[ProjectMembersSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[ProjectMilestonesSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[ProjectsSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[ReleasesSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[TagsSearchData]
    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchMeta`
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

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CommitsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CommitsSearchResult"></a>

`CommitsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[GroupMembersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="GroupMembersSearchResult"></a>

`GroupMembersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[GroupMilestonesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="GroupMilestonesSearchResult"></a>

`GroupMilestonesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[GroupsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="GroupsSearchResult"></a>

`GroupsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[IssuesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[MergeRequestsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MergeRequestsSearchResult"></a>

`MergeRequestsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[PipelinesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PipelinesSearchResult"></a>

`PipelinesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ProjectMembersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProjectMembersSearchResult"></a>

`ProjectMembersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ProjectMilestonesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProjectMilestonesSearchResult"></a>

`ProjectMilestonesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ProjectsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ReleasesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ReleasesSearchResult"></a>

`ReleasesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TagsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.gitlab.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Branch"></a>

`Branch(**data: Any)`
:   GitLab branch
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `can_push: bool | Any`
    :   The type of the None singleton.

    `commit: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `default: bool | Any`
    :   The type of the None singleton.

    `developers_can_merge: bool | Any`
    :   The type of the None singleton.

    `developers_can_push: bool | Any`
    :   The type of the None singleton.

    `merged: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `protected: bool | Any`
    :   The type of the None singleton.

    `web_url: str | Any`
    :   The type of the None singleton.

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

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
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

    `can_push: bool | None`
    :   Whether the current user can push

    `commit: dict[str, typing.Any] | None`
    :   Head commit details

    `commit_id: str | None`
    :   SHA of the head commit

    `default: bool | None`
    :   Whether this is the default branch

    `developers_can_merge: bool | None`
    :   Whether developers can merge into the branch

    `developers_can_push: bool | None`
    :   Whether developers can push to the branch

    `merged: bool | None`
    :   Whether the branch is merged

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the branch

    `project_id: int | None`
    :   ID of the project the branch belongs to

    `protected: bool | None`
    :   Whether the branch is protected

    `web_url: str | None`
    :   Web URL of the branch

<a id="Commit"></a>

`Commit(**data: Any)`
:   GitLab commit
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_email: str | Any`
    :   The type of the None singleton.

    `author_name: str | Any`
    :   The type of the None singleton.

    `authored_date: str | Any`
    :   The type of the None singleton.

    `committed_date: str | Any`
    :   The type of the None singleton.

    `committer_email: str | Any`
    :   The type of the None singleton.

    `committer_name: str | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `extended_trailers: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `message: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `parent_ids: list[str] | Any`
    :   The type of the None singleton.

    `short_id: str | Any`
    :   The type of the None singleton.

    `stats: airbyte_agent_sdk.connectors.gitlab.models.CommitStats | Any | None`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `trailers: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `web_url: str | Any`
    :   The type of the None singleton.

<a id="CommitStats"></a>

`CommitStats(**data: Any)`
:   Commit stats
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `additions: int | Any`
    :   Lines added

    `deletions: int | Any`
    :   Lines deleted

    `model_config`
    :   The type of the None singleton.

    `total: int | Any`
    :   Total changes

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

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="CommitsSearchData"></a>

`CommitsSearchData(**data: Any)`
:   Search result data for commits entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_email: str | None`
    :   Email of the commit author

    `author_name: str | None`
    :   Name of the commit author

    `authored_date: str | None`
    :   Date the commit was authored

    `committed_date: str | None`
    :   Date the commit was committed

    `committer_email: str | None`
    :   Email of the committer

    `committer_name: str | None`
    :   Name of the committer

    `created_at: str | None`
    :   Timestamp when the commit was created

    `id: str | None`
    :   SHA of the commit

    `message: str | None`
    :   Full commit message

    `model_config`
    :   The type of the None singleton.

    `parent_ids: list[typing.Any] | None`
    :   SHAs of parent commits

    `project_id: int | None`
    :   ID of the project the commit belongs to

    `short_id: str | None`
    :   Short SHA of the commit

    `stats: dict[str, typing.Any] | None`
    :   Commit statistics

    `title: str | None`
    :   Title of the commit

    `trailers: dict[str, typing.Any] | None`
    :   Git trailers for the commit

    `web_url: str | None`
    :   Web URL of the commit

<a id="GitlabCheckResult"></a>

`GitlabCheckResult(**data: Any)`
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

<a id="GitlabExecuteResult"></a>

`GitlabExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="GitlabExecuteResultWithMeta"></a>

`GitlabExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Branch], BranchesListResultMeta]
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Commit], CommitsListResultMeta]
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Group], GroupsListResultMeta]
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Issue], IssuesListResultMeta]
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Member], GroupMembersListResultMeta]
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Member], ProjectMembersListResultMeta]
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[MergeRequest], MergeRequestsListResultMeta]
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Milestone], GroupMilestonesListResultMeta]
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Milestone], ProjectMilestonesListResultMeta]
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Pipeline], PipelinesListResultMeta]
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Project], ProjectsListResultMeta]
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Release], ReleasesListResultMeta]
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[Tag], TagsListResultMeta]
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta[list[User], UsersListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`GitlabExecuteResultWithMeta[list[Branch], BranchesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
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

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GitlabExecuteResultWithMeta[list[Commit], CommitsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
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

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GitlabExecuteResultWithMeta[list[Group], GroupsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="GroupsListResult"></a>

`GroupsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GitlabExecuteResultWithMeta[list[Issue], IssuesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
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

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GitlabExecuteResultWithMeta[list[Member], GroupMembersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="GroupMembersListResult"></a>

`GroupMembersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GitlabExecuteResultWithMeta[list[Member], ProjectMembersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProjectMembersListResult"></a>

`ProjectMembersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GitlabExecuteResultWithMeta[list[MergeRequest], MergeRequestsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MergeRequestsListResult"></a>

`MergeRequestsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GitlabExecuteResultWithMeta[list[Milestone], GroupMilestonesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="GroupMilestonesListResult"></a>

`GroupMilestonesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GitlabExecuteResultWithMeta[list[Milestone], ProjectMilestonesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProjectMilestonesListResult"></a>

`ProjectMilestonesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GitlabExecuteResultWithMeta[list[Pipeline], PipelinesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PipelinesListResult"></a>

`PipelinesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GitlabExecuteResultWithMeta[list[Project], ProjectsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
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

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GitlabExecuteResultWithMeta[list[Release], ReleasesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
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

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GitlabExecuteResultWithMeta[list[Tag], TagsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
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

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`GitlabExecuteResultWithMeta[list[User], UsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
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

    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.gitlab.models.GitlabExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="GitlabOauth20AuthConfig"></a>

`GitlabOauth20AuthConfig(**data: Any)`
:   OAuth2.0
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   Access Token for making authenticated requests.

    `client_id: str`
    :   The API ID of the GitLab developer application.

    `client_secret: str`
    :   The API Secret of the GitLab developer application.

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   The key to refresh the expired access token.

<a id="GitlabPersonalAccessTokenAuthConfig"></a>

`GitlabPersonalAccessTokenAuthConfig(**data: Any)`
:   Personal Access Token
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   Log into your GitLab account and generate a personal access token.

    `model_config`
    :   The type of the None singleton.

<a id="GitlabReplicationConfig"></a>

`GitlabReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from GitLab.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `start_date: str | None`
    :   UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data. If not set, all data will be replicated.

<a id="Group"></a>

`Group(**data: Any)`
:   GitLab group
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | Any | None`
    :   The type of the None singleton.

    `auto_devops_enabled: bool | Any | None`
    :   The type of the None singleton.

    `avatar_url: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `default_branch: str | Any | None`
    :   The type of the None singleton.

    `default_branch_protection: int | Any | None`
    :   The type of the None singleton.

    `default_branch_protection_defaults: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `duo_namespace_access_rules: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `emails_disabled: bool | Any | None`
    :   The type of the None singleton.

    `emails_enabled: bool | Any | None`
    :   The type of the None singleton.

    `enabled_git_access_protocol: str | Any | None`
    :   The type of the None singleton.

    `extra_shared_runners_minutes_limit: int | Any | None`
    :   The type of the None singleton.

    `full_name: str | Any`
    :   The type of the None singleton.

    `full_path: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `ip_restriction_ranges: str | Any | None`
    :   The type of the None singleton.

    `ldap_access: str | Any | None`
    :   The type of the None singleton.

    `ldap_cn: str | Any | None`
    :   The type of the None singleton.

    `lfs_enabled: bool | Any | None`
    :   The type of the None singleton.

    `lock_math_rendering_limits_enabled: bool | Any | None`
    :   The type of the None singleton.

    `marked_for_deletion_on: str | Any | None`
    :   The type of the None singleton.

    `math_rendering_limits_enabled: bool | Any | None`
    :   The type of the None singleton.

    `max_artifacts_size: int | Any | None`
    :   The type of the None singleton.

    `membership_lock: bool | Any | None`
    :   The type of the None singleton.

    `mentions_disabled: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `organization_id: int | Any | None`
    :   The type of the None singleton.

    `parent_id: int | Any | None`
    :   The type of the None singleton.

    `path: str | Any`
    :   The type of the None singleton.

    `prevent_forking_outside_group: bool | Any | None`
    :   The type of the None singleton.

    `prevent_sharing_groups_outside_hierarchy: bool | Any | None`
    :   The type of the None singleton.

    `project_creation_level: str | Any | None`
    :   The type of the None singleton.

    `projects: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `request_access_enabled: bool | Any | None`
    :   The type of the None singleton.

    `require_two_factor_authentication: bool | Any | None`
    :   The type of the None singleton.

    `runners_token: str | Any | None`
    :   The type of the None singleton.

    `service_access_tokens_expiration_enforced: bool | Any | None`
    :   The type of the None singleton.

    `share_with_group_lock: bool | Any | None`
    :   The type of the None singleton.

    `shared_projects: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `shared_runners_minutes_limit: int | Any | None`
    :   The type of the None singleton.

    `shared_runners_setting: str | Any | None`
    :   The type of the None singleton.

    `shared_with_groups: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `show_diff_preview_in_email: bool | Any | None`
    :   The type of the None singleton.

    `subgroup_creation_level: str | Any | None`
    :   The type of the None singleton.

    `two_factor_grace_period: int | Any | None`
    :   The type of the None singleton.

    `visibility: str | Any`
    :   The type of the None singleton.

    `web_based_commit_signing_enabled: bool | Any | None`
    :   The type of the None singleton.

    `web_url: str | Any`
    :   The type of the None singleton.

    `wiki_access_level: str | Any | None`
    :   The type of the None singleton.

<a id="GroupMembersListResultMeta"></a>

`GroupMembersListResultMeta(**data: Any)`
:   Metadata for group_members.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="GroupMembersSearchData"></a>

`GroupMembersSearchData(**data: Any)`
:   Search result data for group_members entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_level: int | None`
    :   Access level of the member

    `avatar_url: str | None`
    :   URL of the member avatar

    `created_at: str | None`
    :   Timestamp when the member was added

    `created_by: dict[str, typing.Any] | None`
    :   User who added the member

    `expires_at: str | None`
    :   Expiration date of the membership

    `group_id: int | None`
    :   ID of the group

    `id: int | None`
    :   ID of the member

    `locked: bool | None`
    :   Whether the member account is locked

    `membership_state: str | None`
    :   State of the membership

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Full name of the member

    `state: str | None`
    :   State of the member account

    `username: str | None`
    :   Username of the member

    `web_url: str | None`
    :   Web URL of the member profile

<a id="GroupMilestonesListResultMeta"></a>

`GroupMilestonesListResultMeta(**data: Any)`
:   Metadata for group_milestones.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="GroupMilestonesSearchData"></a>

`GroupMilestonesSearchData(**data: Any)`
:   Search result data for group_milestones entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the milestone was created

    `description: str | None`
    :   Description of the milestone

    `due_date: str | None`
    :   Due date of the milestone

    `expired: bool | None`
    :   Whether the milestone is expired

    `group_id: int | None`
    :   ID of the group

    `id: int | None`
    :   ID of the milestone

    `iid: int | None`
    :   Internal ID of the milestone within the group

    `model_config`
    :   The type of the None singleton.

    `start_date: str | None`
    :   Start date of the milestone

    `state: str | None`
    :   State of the milestone

    `title: str | None`
    :   Title of the milestone

    `updated_at: str | None`
    :   Timestamp when the milestone was last updated

    `web_url: str | None`
    :   Web URL of the milestone

<a id="GroupsListResultMeta"></a>

`GroupsListResultMeta(**data: Any)`
:   Metadata for groups.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="GroupsSearchData"></a>

`GroupsSearchData(**data: Any)`
:   Search result data for groups entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `auto_devops_enabled: bool | None`
    :   Whether Auto DevOps is enabled

    `avatar_url: str | None`
    :   URL of the group avatar

    `created_at: str | None`
    :   Timestamp when the group was created

    `default_branch_protection: int | None`
    :   Default branch protection level

    `description: str | None`
    :   Description of the group

    `emails_disabled: bool | None`
    :   Whether emails are disabled

    `emails_enabled: bool | None`
    :   Whether emails are enabled

    `full_name: str | None`
    :   Full name of the group

    `full_path: str | None`
    :   Full path of the group

    `id: int | None`
    :   ID of the group

    `lfs_enabled: bool | None`
    :   Whether Git LFS is enabled

    `mentions_disabled: bool | None`
    :   Whether mentions are disabled

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the group

    `parent_id: int | None`
    :   ID of the parent group

    `path: str | None`
    :   URL path of the group

    `project_creation_level: str | None`
    :   Level required to create projects

    `projects: list[typing.Any] | None`
    :   Projects in the group

    `request_access_enabled: bool | None`
    :   Whether access requests are enabled

    `require_two_factor_authentication: bool | None`
    :   Whether two-factor authentication is required

    `share_with_group_lock: bool | None`
    :   Whether sharing with other groups is locked

    `shared_with_groups: list[typing.Any] | None`
    :   Groups this group is shared with

    `subgroup_creation_level: str | None`
    :   Level required to create subgroups

    `two_factor_grace_period: int | None`
    :   Grace period for two-factor authentication

    `visibility: str | None`
    :   Visibility level of the group

    `web_url: str | None`
    :   Web URL of the group

<a id="Issue"></a>

`Issue(**data: Any)`
:   GitLab issue
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `assignees: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `author: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `blocking_issues_count: int | Any | None`
    :   The type of the None singleton.

    `closed_at: str | Any | None`
    :   The type of the None singleton.

    `closed_by: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `confidential: bool | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `discussion_locked: bool | Any | None`
    :   The type of the None singleton.

    `downvotes: int | Any`
    :   The type of the None singleton.

    `due_date: str | Any | None`
    :   The type of the None singleton.

    `epic: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `epic_iid: int | Any | None`
    :   The type of the None singleton.

    `has_tasks: bool | Any | None`
    :   The type of the None singleton.

    `health_status: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `iid: int | Any`
    :   The type of the None singleton.

    `imported: bool | Any | None`
    :   The type of the None singleton.

    `imported_from: str | Any | None`
    :   The type of the None singleton.

    `issue_type: str | Any | None`
    :   The type of the None singleton.

    `iteration: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `labels: list[str] | Any`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `merge_requests_count: int | Any | None`
    :   The type of the None singleton.

    `milestone: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `moved_to_id: int | Any | None`
    :   The type of the None singleton.

    `project_id: int | Any`
    :   The type of the None singleton.

    `references: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `service_desk_reply_to: str | Any | None`
    :   The type of the None singleton.

    `severity: str | Any | None`
    :   The type of the None singleton.

    `start_date: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any`
    :   The type of the None singleton.

    `subscribed: bool | Any | None`
    :   The type of the None singleton.

    `task_completion_status: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `task_status: str | Any | None`
    :   The type of the None singleton.

    `time_stats: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `upvotes: int | Any`
    :   The type of the None singleton.

    `user_notes_count: int | Any`
    :   The type of the None singleton.

    `web_url: str | Any`
    :   The type of the None singleton.

    `weight: int | Any | None`
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

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
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

    `assignee: dict[str, typing.Any] | None`
    :   Primary assignee of the issue

    `assignee_id: int | None`
    :   ID of the primary assignee

    `assignees: list[typing.Any] | None`
    :   Users assigned to the issue

    `author: dict[str, typing.Any] | None`
    :   Author of the issue

    `author_id: int | None`
    :   ID of the author

    `blocking_issues_count: int | None`
    :   Number of blocking issues

    `closed_at: str | None`
    :   Timestamp when the issue was closed

    `closed_by: dict[str, typing.Any] | None`
    :   User who closed the issue

    `closed_by_id: int | None`
    :   ID of the user who closed the issue

    `confidential: bool | None`
    :   Whether the issue is confidential

    `created_at: str | None`
    :   Timestamp when the issue was created

    `description: str | None`
    :   Description of the issue

    `discussion_locked: bool | None`
    :   Whether discussion is locked

    `downvotes: int | None`
    :   Number of downvotes

    `due_date: str | None`
    :   Due date for the issue

    `has_tasks: bool | None`
    :   Whether the issue has tasks

    `id: int | None`
    :   ID of the issue

    `iid: int | None`
    :   Internal ID of the issue within the project

    `issue_type: str | None`
    :   Type classification of the issue

    `labels: list[typing.Any] | None`
    :   Labels assigned to the issue

    `links: dict[str, typing.Any] | None`
    :   Related resource links

    `merge_requests_count: int | None`
    :   Number of related merge requests

    `milestone: dict[str, typing.Any] | None`
    :   Milestone the issue belongs to

    `milestone_id: int | None`
    :   ID of the milestone

    `model_config`
    :   The type of the None singleton.

    `project_id: int | None`
    :   ID of the project the issue belongs to

    `references: dict[str, typing.Any] | None`
    :   Issue references

    `severity: str | None`
    :   Severity level of the issue

    `state: str | None`
    :   State of the issue

    `task_completion_status: dict[str, typing.Any] | None`
    :   Task completion status

    `time_stats: dict[str, typing.Any] | None`
    :   Time tracking statistics

    `title: str | None`
    :   Title of the issue

    `type_: str | None`
    :   Type of the issue

    `updated_at: str | None`
    :   Timestamp when the issue was last updated

    `upvotes: int | None`
    :   Number of upvotes

    `user_notes_count: int | None`
    :   Number of user notes on the issue

    `web_url: str | None`
    :   Web URL of the issue

    `weight: int | None`
    :   Weight of the issue

<a id="Member"></a>

`Member(**data: Any)`
:   GitLab group or project member
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_level: int | Any`
    :   The type of the None singleton.

    `avatar_url: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `created_by: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `expires_at: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `locked: bool | Any | None`
    :   The type of the None singleton.

    `membership_state: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `public_email: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any`
    :   The type of the None singleton.

    `username: str | Any`
    :   The type of the None singleton.

    `web_url: str | Any`
    :   The type of the None singleton.

<a id="MergeRequest"></a>

`MergeRequest(**data: Any)`
:   GitLab merge request
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `approvals_before_merge: int | Any | None`
    :   The type of the None singleton.

    `assignee: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `assignees: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `author: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `blocking_discussions_resolved: bool | Any | None`
    :   The type of the None singleton.

    `changes_count: str | Any | None`
    :   The type of the None singleton.

    `closed_at: str | Any | None`
    :   The type of the None singleton.

    `closed_by: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `detailed_merge_status: str | Any | None`
    :   The type of the None singleton.

    `diff_refs: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `discussion_locked: bool | Any | None`
    :   The type of the None singleton.

    `downvotes: int | Any`
    :   The type of the None singleton.

    `draft: bool | Any | None`
    :   The type of the None singleton.

    `first_contribution: bool | Any | None`
    :   The type of the None singleton.

    `first_deployed_to_production_at: str | Any | None`
    :   The type of the None singleton.

    `force_remove_source_branch: bool | Any | None`
    :   The type of the None singleton.

    `has_conflicts: bool | Any | None`
    :   The type of the None singleton.

    `head_pipeline: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `iid: int | Any`
    :   The type of the None singleton.

    `imported: bool | Any | None`
    :   The type of the None singleton.

    `imported_from: str | Any | None`
    :   The type of the None singleton.

    `labels: list[str] | Any`
    :   The type of the None singleton.

    `latest_build_finished_at: str | Any | None`
    :   The type of the None singleton.

    `latest_build_started_at: str | Any | None`
    :   The type of the None singleton.

    `merge_after: str | Any | None`
    :   The type of the None singleton.

    `merge_commit_sha: str | Any | None`
    :   The type of the None singleton.

    `merge_error: str | Any | None`
    :   The type of the None singleton.

    `merge_status: str | Any`
    :   The type of the None singleton.

    `merge_user: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `merge_when_pipeline_succeeds: bool | Any | None`
    :   The type of the None singleton.

    `merged_at: str | Any | None`
    :   The type of the None singleton.

    `merged_by: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `milestone: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pipeline: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `prepared_at: str | Any | None`
    :   The type of the None singleton.

    `project_id: int | Any`
    :   The type of the None singleton.

    `reference: str | Any | None`
    :   The type of the None singleton.

    `references: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `reviewers: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `sha: str | Any | None`
    :   The type of the None singleton.

    `should_remove_source_branch: bool | Any | None`
    :   The type of the None singleton.

    `source_branch: str | Any`
    :   The type of the None singleton.

    `source_project_id: int | Any | None`
    :   The type of the None singleton.

    `squash: bool | Any | None`
    :   The type of the None singleton.

    `squash_commit_sha: str | Any | None`
    :   The type of the None singleton.

    `squash_on_merge: bool | Any | None`
    :   The type of the None singleton.

    `state: str | Any`
    :   The type of the None singleton.

    `subscribed: bool | Any | None`
    :   The type of the None singleton.

    `target_branch: str | Any`
    :   The type of the None singleton.

    `target_project_id: int | Any | None`
    :   The type of the None singleton.

    `task_completion_status: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `time_stats: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `upvotes: int | Any`
    :   The type of the None singleton.

    `user: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `user_notes_count: int | Any`
    :   The type of the None singleton.

    `web_url: str | Any`
    :   The type of the None singleton.

    `work_in_progress: bool | Any | None`
    :   The type of the None singleton.

<a id="MergeRequestsListResultMeta"></a>

`MergeRequestsListResultMeta(**data: Any)`
:   Metadata for merge_requests.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="MergeRequestsSearchData"></a>

`MergeRequestsSearchData(**data: Any)`
:   Search result data for merge_requests entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee: dict[str, typing.Any] | None`
    :   Primary assignee of the merge request

    `assignee_id: int | None`
    :   ID of the primary assignee

    `assignees: list[typing.Any] | None`
    :   Users assigned to the merge request

    `author: dict[str, typing.Any] | None`
    :   Author of the merge request

    `author_id: int | None`
    :   ID of the author

    `blocking_discussions_resolved: bool | None`
    :   Whether blocking discussions are resolved

    `closed_at: str | None`
    :   Timestamp when the merge request was closed

    `closed_by: dict[str, typing.Any] | None`
    :   User who closed the merge request

    `closed_by_id: int | None`
    :   ID of the user who closed it

    `created_at: str | None`
    :   Timestamp when the merge request was created

    `description: str | None`
    :   Description of the merge request

    `detailed_merge_status: str | None`
    :   Detailed merge status

    `discussion_locked: bool | None`
    :   Whether discussion is locked

    `downvotes: int | None`
    :   Number of downvotes

    `draft: bool | None`
    :   Whether the merge request is a draft

    `force_remove_source_branch: bool | None`
    :   Whether to force remove source branch

    `has_conflicts: bool | None`
    :   Whether the merge request has conflicts

    `id: int | None`
    :   ID of the merge request

    `iid: int | None`
    :   Internal ID of the merge request within the project

    `labels: list[typing.Any] | None`
    :   Labels assigned to the merge request

    `merge_commit_sha: str | None`
    :   SHA of the merge commit

    `merge_status: str | None`
    :   Merge status of the merge request

    `merge_user: dict[str, typing.Any] | None`
    :   User who performed the merge

    `merge_when_pipeline_succeeds: bool | None`
    :   Whether to merge when pipeline succeeds

    `merged_at: str | None`
    :   Timestamp when the merge request was merged

    `merged_by: dict[str, typing.Any] | None`
    :   User who merged the merge request

    `merged_by_id: int | None`
    :   ID of the user who merged it

    `milestone: dict[str, typing.Any] | None`
    :   Milestone the merge request belongs to

    `milestone_id: int | None`
    :   ID of the milestone

    `model_config`
    :   The type of the None singleton.

    `project_id: int | None`
    :   ID of the project

    `reference: str | None`
    :   Short reference for the merge request

    `references: dict[str, typing.Any] | None`
    :   Merge request references

    `reviewers: list[typing.Any] | None`
    :   Users assigned as reviewers

    `sha: str | None`
    :   SHA of the head commit

    `should_remove_source_branch: bool | None`
    :   Whether source branch should be removed

    `source_branch: str | None`
    :   Source branch for the merge request

    `source_project_id: int | None`
    :   ID of the source project

    `squash: bool | None`
    :   Whether to squash commits on merge

    `squash_commit_sha: str | None`
    :   SHA of the squash commit

    `state: str | None`
    :   State of the merge request

    `target_branch: str | None`
    :   Target branch for the merge request

    `target_project_id: int | None`
    :   ID of the target project

    `task_completion_status: dict[str, typing.Any] | None`
    :   Task completion status

    `time_stats: dict[str, typing.Any] | None`
    :   Time tracking statistics

    `title: str | None`
    :   Title of the merge request

    `updated_at: str | None`
    :   Timestamp when the merge request was last updated

    `upvotes: int | None`
    :   Number of upvotes

    `user_notes_count: int | None`
    :   Number of user notes

    `web_url: str | None`
    :   Web URL of the merge request

    `work_in_progress: bool | None`
    :   Whether the merge request is a work in progress

<a id="Milestone"></a>

`Milestone(**data: Any)`
:   GitLab milestone
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `due_date: str | Any | None`
    :   The type of the None singleton.

    `expired: bool | Any | None`
    :   The type of the None singleton.

    `group_id: int | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `iid: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `project_id: int | Any | None`
    :   The type of the None singleton.

    `start_date: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `web_url: str | Any`
    :   The type of the None singleton.

<a id="Pipeline"></a>

`Pipeline(**data: Any)`
:   GitLab CI/CD pipeline
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `iid: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `project_id: int | Any`
    :   The type of the None singleton.

    `ref: str | Any`
    :   The type of the None singleton.

    `sha: str | Any`
    :   The type of the None singleton.

    `source: str | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `web_url: str | Any`
    :   The type of the None singleton.

<a id="PipelinesListResultMeta"></a>

`PipelinesListResultMeta(**data: Any)`
:   Metadata for pipelines.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="PipelinesSearchData"></a>

`PipelinesSearchData(**data: Any)`
:   Search result data for pipelines entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the pipeline was created

    `id: int | None`
    :   ID of the pipeline

    `iid: int | None`
    :   Internal ID of the pipeline within the project

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the pipeline

    `project_id: int | None`
    :   ID of the project

    `ref: str | None`
    :   Branch or tag that triggered the pipeline

    `sha: str | None`
    :   SHA of the commit that triggered the pipeline

    `source: str | None`
    :   Source that triggered the pipeline

    `status: str | None`
    :   Status of the pipeline

    `updated_at: str | None`
    :   Timestamp when the pipeline was last updated

    `web_url: str | None`
    :   Web URL of the pipeline

<a id="Project"></a>

`Project(**data: Any)`
:   GitLab project
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allow_merge_on_skipped_pipeline: bool | Any | None`
    :   The type of the None singleton.

    `analytics_access_level: str | Any | None`
    :   The type of the None singleton.

    `archived: bool | Any`
    :   The type of the None singleton.

    `auto_cancel_pending_pipelines: str | Any | None`
    :   The type of the None singleton.

    `auto_devops_deploy_strategy: str | Any | None`
    :   The type of the None singleton.

    `auto_devops_enabled: bool | Any | None`
    :   The type of the None singleton.

    `autoclose_referenced_issues: bool | Any | None`
    :   The type of the None singleton.

    `avatar_url: str | Any | None`
    :   The type of the None singleton.

    `build_git_strategy: str | Any | None`
    :   The type of the None singleton.

    `build_timeout: int | Any | None`
    :   The type of the None singleton.

    `builds_access_level: str | Any | None`
    :   The type of the None singleton.

    `can_create_merge_request_in: bool | Any | None`
    :   The type of the None singleton.

    `ci_allow_fork_pipelines_to_run_in_parent_project: bool | Any | None`
    :   The type of the None singleton.

    `ci_config_path: str | Any | None`
    :   The type of the None singleton.

    `ci_default_git_depth: int | Any | None`
    :   The type of the None singleton.

    `ci_delete_pipelines_in_seconds: int | Any | None`
    :   The type of the None singleton.

    `ci_display_pipeline_variables: bool | Any | None`
    :   The type of the None singleton.

    `ci_forward_deployment_enabled: bool | Any | None`
    :   The type of the None singleton.

    `ci_forward_deployment_rollback_allowed: bool | Any | None`
    :   The type of the None singleton.

    `ci_id_token_sub_claim_components: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `ci_job_token_scope_enabled: bool | Any | None`
    :   The type of the None singleton.

    `ci_pipeline_variables_minimum_override_role: str | Any | None`
    :   The type of the None singleton.

    `ci_push_repository_for_job_token_allowed: bool | Any | None`
    :   The type of the None singleton.

    `ci_separated_caches: bool | Any | None`
    :   The type of the None singleton.

    `compliance_frameworks: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `container_expiration_policy: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `container_registry_access_level: str | Any | None`
    :   The type of the None singleton.

    `container_registry_enabled: bool | Any | None`
    :   The type of the None singleton.

    `container_registry_image_prefix: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `creator_id: int | Any | None`
    :   The type of the None singleton.

    `default_branch: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `description_html: str | Any | None`
    :   The type of the None singleton.

    `emails_disabled: bool | Any | None`
    :   The type of the None singleton.

    `emails_enabled: bool | Any | None`
    :   The type of the None singleton.

    `empty_repo: bool | Any | None`
    :   The type of the None singleton.

    `enforce_auth_checks_on_uploads: bool | Any | None`
    :   The type of the None singleton.

    `environments_access_level: str | Any | None`
    :   The type of the None singleton.

    `external_authorization_classification_label: str | Any | None`
    :   The type of the None singleton.

    `feature_flags_access_level: str | Any | None`
    :   The type of the None singleton.

    `forking_access_level: str | Any | None`
    :   The type of the None singleton.

    `forks_count: int | Any`
    :   The type of the None singleton.

    `group_runners_enabled: bool | Any | None`
    :   The type of the None singleton.

    `http_url_to_repo: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `import_error: str | Any | None`
    :   The type of the None singleton.

    `import_status: str | Any | None`
    :   The type of the None singleton.

    `import_type: str | Any | None`
    :   The type of the None singleton.

    `import_url: str | Any | None`
    :   The type of the None singleton.

    `infrastructure_access_level: str | Any | None`
    :   The type of the None singleton.

    `issue_branch_template: str | Any | None`
    :   The type of the None singleton.

    `issues_access_level: str | Any | None`
    :   The type of the None singleton.

    `issues_enabled: bool | Any | None`
    :   The type of the None singleton.

    `jobs_enabled: bool | Any | None`
    :   The type of the None singleton.

    `keep_latest_artifact: bool | Any | None`
    :   The type of the None singleton.

    `last_activity_at: str | Any`
    :   The type of the None singleton.

    `lfs_enabled: bool | Any | None`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `marked_for_deletion_at: str | Any | None`
    :   The type of the None singleton.

    `marked_for_deletion_on: str | Any | None`
    :   The type of the None singleton.

    `max_artifacts_size: int | Any | None`
    :   The type of the None singleton.

    `merge_commit_template: str | Any | None`
    :   The type of the None singleton.

    `merge_method: str | Any | None`
    :   The type of the None singleton.

    `merge_request_title_regex: str | Any | None`
    :   The type of the None singleton.

    `merge_request_title_regex_description: str | Any | None`
    :   The type of the None singleton.

    `merge_requests_access_level: str | Any | None`
    :   The type of the None singleton.

    `merge_requests_enabled: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `model_experiments_access_level: str | Any | None`
    :   The type of the None singleton.

    `model_registry_access_level: str | Any | None`
    :   The type of the None singleton.

    `monitor_access_level: str | Any | None`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `name_with_namespace: str | Any`
    :   The type of the None singleton.

    `namespace: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `only_allow_merge_if_all_discussions_are_resolved: bool | Any | None`
    :   The type of the None singleton.

    `only_allow_merge_if_pipeline_succeeds: bool | Any | None`
    :   The type of the None singleton.

    `open_issues_count: int | Any`
    :   The type of the None singleton.

    `package_registry_access_level: str | Any | None`
    :   The type of the None singleton.

    `packages_enabled: bool | Any | None`
    :   The type of the None singleton.

    `pages_access_level: str | Any | None`
    :   The type of the None singleton.

    `path: str | Any`
    :   The type of the None singleton.

    `path_with_namespace: str | Any`
    :   The type of the None singleton.

    `permissions: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `printing_merge_request_link_enabled: bool | Any | None`
    :   The type of the None singleton.

    `protect_merge_request_pipelines: bool | Any | None`
    :   The type of the None singleton.

    `public_jobs: bool | Any | None`
    :   The type of the None singleton.

    `readme_url: str | Any | None`
    :   The type of the None singleton.

    `releases_access_level: str | Any | None`
    :   The type of the None singleton.

    `remove_source_branch_after_merge: bool | Any | None`
    :   The type of the None singleton.

    `repository_access_level: str | Any | None`
    :   The type of the None singleton.

    `repository_object_format: str | Any | None`
    :   The type of the None singleton.

    `request_access_enabled: bool | Any | None`
    :   The type of the None singleton.

    `requirements_access_level: str | Any | None`
    :   The type of the None singleton.

    `requirements_enabled: bool | Any | None`
    :   The type of the None singleton.

    `resolve_outdated_diff_discussions: bool | Any | None`
    :   The type of the None singleton.

    `resource_group_default_process_mode: str | Any | None`
    :   The type of the None singleton.

    `restrict_user_defined_variables: bool | Any | None`
    :   The type of the None singleton.

    `runner_token_expiration_interval: str | Any | None`
    :   The type of the None singleton.

    `security_and_compliance_access_level: str | Any | None`
    :   The type of the None singleton.

    `security_and_compliance_enabled: bool | Any | None`
    :   The type of the None singleton.

    `service_desk_address: str | Any | None`
    :   The type of the None singleton.

    `service_desk_enabled: bool | Any | None`
    :   The type of the None singleton.

    `shared_runners_enabled: bool | Any | None`
    :   The type of the None singleton.

    `shared_with_groups: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `show_diff_preview_in_email: bool | Any | None`
    :   The type of the None singleton.

    `snippets_access_level: str | Any | None`
    :   The type of the None singleton.

    `snippets_enabled: bool | Any | None`
    :   The type of the None singleton.

    `squash_commit_template: str | Any | None`
    :   The type of the None singleton.

    `squash_option: str | Any | None`
    :   The type of the None singleton.

    `ssh_url_to_repo: str | Any`
    :   The type of the None singleton.

    `star_count: int | Any`
    :   The type of the None singleton.

    `suggestion_commit_message: str | Any | None`
    :   The type of the None singleton.

    `tag_list: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `topics: list[str] | Any`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `visibility: str | Any`
    :   The type of the None singleton.

    `warn_about_potentially_unwanted_characters: bool | Any | None`
    :   The type of the None singleton.

    `web_based_commit_signing_enabled: bool | Any | None`
    :   The type of the None singleton.

    `web_url: str | Any`
    :   The type of the None singleton.

    `wiki_access_level: str | Any | None`
    :   The type of the None singleton.

    `wiki_enabled: bool | Any | None`
    :   The type of the None singleton.

<a id="ProjectMembersListResultMeta"></a>

`ProjectMembersListResultMeta(**data: Any)`
:   Metadata for project_members.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="ProjectMembersSearchData"></a>

`ProjectMembersSearchData(**data: Any)`
:   Search result data for project_members entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_level: int | None`
    :   Access level of the member

    `avatar_url: str | None`
    :   URL of the member avatar

    `created_at: str | None`
    :   Timestamp when the member was added

    `created_by: dict[str, typing.Any] | None`
    :   User who added the member

    `expires_at: str | None`
    :   Expiration date of the membership

    `id: int | None`
    :   ID of the member

    `locked: bool | None`
    :   Whether the member account is locked

    `membership_state: str | None`
    :   State of the membership

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Full name of the member

    `project_id: int | None`
    :   ID of the project

    `state: str | None`
    :   State of the member account

    `username: str | None`
    :   Username of the member

    `web_url: str | None`
    :   Web URL of the member profile

<a id="ProjectMilestonesListResultMeta"></a>

`ProjectMilestonesListResultMeta(**data: Any)`
:   Metadata for project_milestones.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="ProjectMilestonesSearchData"></a>

`ProjectMilestonesSearchData(**data: Any)`
:   Search result data for project_milestones entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the milestone was created

    `description: str | None`
    :   Description of the milestone

    `due_date: str | None`
    :   Due date of the milestone

    `expired: bool | None`
    :   Whether the milestone is expired

    `id: int | None`
    :   ID of the milestone

    `iid: int | None`
    :   Internal ID of the milestone within the project

    `model_config`
    :   The type of the None singleton.

    `project_id: int | None`
    :   ID of the project

    `start_date: str | None`
    :   Start date of the milestone

    `state: str | None`
    :   State of the milestone

    `title: str | None`
    :   Title of the milestone

    `updated_at: str | None`
    :   Timestamp when the milestone was last updated

    `web_url: str | None`
    :   Web URL of the milestone

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

    `next: str | Any | None`
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

    `allow_merge_on_skipped_pipeline: bool | None`
    :   Whether merge is allowed on skipped pipeline

    `analytics_access_level: str | None`
    :   Access level for analytics

    `archived: bool | None`
    :   Whether the project is archived

    `auto_cancel_pending_pipelines: str | None`
    :   Auto-cancel pending pipelines setting

    `auto_devops_deploy_strategy: str | None`
    :   Auto DevOps deployment strategy

    `auto_devops_enabled: bool | None`
    :   Whether Auto DevOps is enabled

    `autoclose_referenced_issues: bool | None`
    :   Whether referenced issues are auto-closed

    `avatar_url: str | None`
    :   URL of the project avatar

    `build_timeout: int | None`
    :   Build timeout in seconds

    `builds_access_level: str | None`
    :   Access level for builds

    `can_create_merge_request_in: bool | None`
    :   Whether user can create merge requests

    `ci_config_path: str | None`
    :   Path to the CI configuration file

    `ci_default_git_depth: int | None`
    :   Default git depth for CI pipelines

    `ci_forward_deployment_enabled: bool | None`
    :   Whether CI forward deployment is enabled

    `compliance_frameworks: list[typing.Any] | None`
    :   Compliance frameworks for the project

    `container_expiration_policy: dict[str, typing.Any] | None`
    :   Container expiration policy settings

    `container_registry_enabled: bool | None`
    :   Whether container registry is enabled

    `container_registry_image_prefix: str | None`
    :   Prefix for container registry images

    `created_at: str | None`
    :   Timestamp when the project was created

    `creator_id: int | None`
    :   ID of the project creator

    `default_branch: str | None`
    :   Default branch of the project

    `description: str | None`
    :   Description of the project

    `description_html: str | None`
    :   HTML-rendered description of the project

    `emails_disabled: bool | None`
    :   Whether emails are disabled

    `empty_repo: bool | None`
    :   Whether the repository is empty

    `external_authorization_classification_label: str | None`
    :   External authorization classification label

    `forking_access_level: str | None`
    :   Access level for forking

    `forks_count: int | None`
    :   Number of forks

    `http_url_to_repo: str | None`
    :   HTTP URL to the repository

    `id: int | None`
    :   ID of the project

    `import_status: str | None`
    :   Import status of the project

    `issues_access_level: str | None`
    :   Access level for issues

    `issues_enabled: bool | None`
    :   Whether issues are enabled

    `jobs_enabled: bool | None`
    :   Whether jobs are enabled

    `keep_latest_artifact: bool | None`
    :   Whether the latest artifact is kept

    `last_activity_at: str | None`
    :   Timestamp of last activity

    `lfs_enabled: bool | None`
    :   Whether Git LFS is enabled

    `links: dict[str, typing.Any] | None`
    :   Related resource links

    `merge_method: str | None`
    :   Merge method used for the project

    `merge_requests_access_level: str | None`
    :   Access level for merge requests

    `merge_requests_enabled: bool | None`
    :   Whether merge requests are enabled

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the project

    `name_with_namespace: str | None`
    :   Full name including namespace

    `namespace: dict[str, typing.Any] | None`
    :   Namespace the project belongs to

    `only_allow_merge_if_all_discussions_are_resolved: bool | None`
    :   Whether merge requires all discussions resolved

    `only_allow_merge_if_pipeline_succeeds: bool | None`
    :   Whether merge requires pipeline success

    `open_issues_count: int | None`
    :   Number of open issues

    `operations_access_level: str | None`
    :   Access level for operations

    `packages_enabled: bool | None`
    :   Whether packages are enabled

    `pages_access_level: str | None`
    :   Access level for pages

    `path: str | None`
    :   URL path of the project

    `path_with_namespace: str | None`
    :   Full path including namespace

    `permissions: dict[str, typing.Any] | None`
    :   User permissions for the project

    `printing_merge_request_link_enabled: bool | None`
    :   Whether MR link printing is enabled

    `public_jobs: bool | None`
    :   Whether jobs are public

    `readme_url: str | None`
    :   URL to the project README

    `remove_source_branch_after_merge: bool | None`
    :   Whether source branch is removed after merge

    `repository_access_level: str | None`
    :   Access level for the repository

    `request_access_enabled: bool | None`
    :   Whether access requests are enabled

    `requirements_enabled: bool | None`
    :   Whether requirements are enabled

    `resolve_outdated_diff_discussions: bool | None`
    :   Whether outdated diff discussions are auto-resolved

    `restrict_user_defined_variables: bool | None`
    :   Whether user-defined variables are restricted

    `security_and_compliance_enabled: bool | None`
    :   Whether security and compliance is enabled

    `service_desk_address: str | None`
    :   Email address for the service desk

    `service_desk_enabled: bool | None`
    :   Whether service desk is enabled

    `shared_runners_enabled: bool | None`
    :   Whether shared runners are enabled

    `shared_with_groups: list[typing.Any] | None`
    :   Groups the project is shared with

    `snippets_access_level: str | None`
    :   Access level for snippets

    `snippets_enabled: bool | None`
    :   Whether snippets are enabled

    `ssh_url_to_repo: str | None`
    :   SSH URL to the repository

    `star_count: int | None`
    :   Number of stars

    `statistics: dict[str, typing.Any] | None`
    :   Project statistics

    `tag_list: list[typing.Any] | None`
    :   List of tags for the project

    `topics: list[typing.Any] | None`
    :   List of topics for the project

    `updated_at: str | None`
    :   Timestamp when the project was last updated

    `visibility: str | None`
    :   Visibility level of the project

    `web_url: str | None`
    :   Web URL of the project

    `wiki_access_level: str | None`
    :   Access level for the wiki

    `wiki_enabled: bool | None`
    :   Whether wiki is enabled

<a id="Release"></a>

`Release(**data: Any)`
:   GitLab release
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assets: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `author: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `commit: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `commit_path: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `evidences: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `milestones: list[typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `released_at: str | Any`
    :   The type of the None singleton.

    `tag_name: str | Any`
    :   The type of the None singleton.

    `tag_path: str | Any | None`
    :   The type of the None singleton.

    `upcoming_release: bool | Any`
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

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="ReleasesSearchData"></a>

`ReleasesSearchData(**data: Any)`
:   Search result data for releases entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assets: dict[str, typing.Any] | None`
    :   Assets attached to the release

    `author: dict[str, typing.Any] | None`
    :   Author of the release

    `author_id: int | None`
    :   ID of the author

    `commit: dict[str, typing.Any] | None`
    :   Commit associated with the release

    `commit_id: str | None`
    :   SHA of the associated commit

    `commit_path: str | None`
    :   Path to the release commit

    `created_at: str | None`
    :   Timestamp when the release was created

    `description: str | None`
    :   Description of the release

    `evidences: list[typing.Any] | None`
    :   Evidences collected for the release

    `links: dict[str, typing.Any] | None`
    :   Related resource links

    `milestones: list[typing.Any] | None`
    :   Milestones associated with the release

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the release

    `project_id: int | None`
    :   ID of the project

    `released_at: str | None`
    :   Timestamp when the release was published

    `tag_name: str | None`
    :   Tag name associated with the release

    `tag_path: str | None`
    :   Path to the release tag

    `upcoming_release: bool | None`
    :   Whether this is an upcoming release

<a id="Tag"></a>

`Tag(**data: Any)`
:   GitLab repository tag
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `commit: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `message: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `protected: bool | Any`
    :   The type of the None singleton.

    `release: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `target: str | Any`
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

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
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

    `commit: dict[str, typing.Any] | None`
    :   Commit the tag points to

    `commit_id: str | None`
    :   SHA of the tagged commit

    `message: str | None`
    :   Annotation message of the tag

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the tag

    `project_id: int | None`
    :   ID of the project

    `protected: bool | None`
    :   Whether the tag is protected

    `release: dict[str, typing.Any] | None`
    :   Release associated with the tag

    `target: str | None`
    :   SHA the tag points to

<a id="User"></a>

`User(**data: Any)`
:   GitLab user
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_url: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `locked: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `public_email: str | Any | None`
    :   The type of the None singleton.

    `state: str | Any`
    :   The type of the None singleton.

    `username: str | Any`
    :   The type of the None singleton.

    `web_url: str | Any`
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

    `next: str | Any | None`
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

    `avatar_url: str | None`
    :   URL of the user avatar

    `id: int | None`
    :   ID of the user

    `locked: bool | None`
    :   Whether the user account is locked

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Full name of the user

    `state: str | None`
    :   State of the user account

    `username: str | None`
    :   Username of the user

    `web_url: str | None`
    :   Web URL of the user profile