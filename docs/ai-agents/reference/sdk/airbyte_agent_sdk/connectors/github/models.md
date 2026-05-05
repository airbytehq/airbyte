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
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[CommitsSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[DirectoryContentSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[DiscussionsSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[FileContentSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[IssuesSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[LabelsSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[MilestonesSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[OrgRepositoriesSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[OrganizationsSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[PrCommentsSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[ProjectItemsSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[ProjectsSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[PullRequestsSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[ReleasesSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[RepositoriesSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[ReviewsSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[StargazersSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[TagsSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[TeamsSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[UsersSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[ViewerRepositoriesSearchData]
    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult[ViewerSearchData]

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

`AirbyteSearchResult[CommitsSearchData](**data: Any)`
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

<a id="CommitsSearchResult"></a>

`CommitsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[DirectoryContentSearchData](**data: Any)`
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

<a id="DirectoryContentSearchResult"></a>

`DirectoryContentSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[DiscussionsSearchData](**data: Any)`
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

<a id="DiscussionsSearchResult"></a>

`DiscussionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[FileContentSearchData](**data: Any)`
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

<a id="FileContentSearchResult"></a>

`FileContentSearchResult(**data: Any)`
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

`AirbyteSearchResult[LabelsSearchData](**data: Any)`
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

<a id="LabelsSearchResult"></a>

`LabelsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[MilestonesSearchData](**data: Any)`
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

<a id="MilestonesSearchResult"></a>

`MilestonesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[OrgRepositoriesSearchData](**data: Any)`
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

<a id="OrgRepositoriesSearchResult"></a>

`OrgRepositoriesSearchResult(**data: Any)`
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

`AirbyteSearchResult[PrCommentsSearchData](**data: Any)`
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

<a id="PrCommentsSearchResult"></a>

`PrCommentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ProjectItemsSearchData](**data: Any)`
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

<a id="ProjectItemsSearchResult"></a>

`ProjectItemsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ProjectsSearchData](**data: Any)`
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

<a id="ProjectsSearchResult"></a>

`ProjectsSearchResult(**data: Any)`
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

`AirbyteSearchResult[ReleasesSearchData](**data: Any)`
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

<a id="ReleasesSearchResult"></a>

`ReleasesSearchResult(**data: Any)`
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

`AirbyteSearchResult[ReviewsSearchData](**data: Any)`
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

<a id="ReviewsSearchResult"></a>

`ReviewsSearchResult(**data: Any)`
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

`AirbyteSearchResult[ViewerRepositoriesSearchData](**data: Any)`
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

<a id="ViewerRepositoriesSearchResult"></a>

`ViewerRepositoriesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.github.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ViewerSearchData](**data: Any)`
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

<a id="ViewerSearchResult"></a>

`ViewerSearchResult(**data: Any)`
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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
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

    `name: str | None`
    :   Branch name (e.g. `main`, `feature/foo`)

    `prefix: str | None`
    :   Git ref prefix for the branch (typically `refs/heads/`)

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

    `body: str`
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

    `author_association: str | None`
    :   The type of the None singleton.

    `body: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `html_url: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `issue_url: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | None`
    :   The type of the None singleton.

    `performed_via_github_app: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `reactions: airbyte_agent_sdk.connectors.github.models.CommentResponseReactions | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.github.models.CommentResponseUser | None`
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

    `confused: int | None`
    :   The type of the None singleton.

    `eyes: int | None`
    :   The type of the None singleton.

    `field_1: int | None`
    :   The type of the None singleton.

    `heart: int | None`
    :   The type of the None singleton.

    `hooray: int | None`
    :   The type of the None singleton.

    `laugh: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rocket: int | None`
    :   The type of the None singleton.

    `total_count: int | None`
    :   The type of the None singleton.

    `url: str | None`
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

    `avatar_url: str | None`
    :   The type of the None singleton.

    `html_url: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `login: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | None`
    :   The type of the None singleton.

    `site_admin: bool | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `url: str | None`
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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
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

    `body: str | None`
    :   Markdown body of the comment

    `created_at: str | None`
    :   ISO 8601 timestamp when the comment was created

    `database_id: int | None`
    :   REST API numeric identifier for the comment

    `id: str | None`
    :   GraphQL node ID of the comment

    `is_minimized: bool | None`
    :   Whether the comment has been hidden/collapsed

    `model_config`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   ISO 8601 timestamp when the comment was last updated

    `url: str | None`
    :   Permalink to the comment on GitHub

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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
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

    `abbreviated_oid: str | None`
    :   Abbreviated Git commit SHA (typically 7 characters)

    `additions: int | None`
    :   Number of lines added across all files in the commit

    `authored_date: str | None`
    :   ISO 8601 timestamp when the commit was originally authored

    `changed_files: int | None`
    :   Number of files changed in the commit

    `committed_date: str | None`
    :   ISO 8601 timestamp when the commit was applied to its tree

    `deletions: int | None`
    :   Number of lines deleted across all files in the commit

    `message: str | None`
    :   Full commit message

    `message_headline: str | None`
    :   First line of the commit message

    `model_config`
    :   The type of the None singleton.

    `oid: str | None`
    :   Full Git commit SHA

    `url: str | None`
    :   Permalink to the commit on GitHub

<a id="DirectoryContentSearchData"></a>

`DirectoryContentSearchData(**data: Any)`
:   Search result data for directory_content entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_count: int | None`
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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="DiscussionsSearchData"></a>

`DiscussionsSearchData(**data: Any)`
:   Search result data for discussions entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="FileContentSearchData"></a>

`FileContentSearchData(**data: Any)`
:   Search result data for file_content entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

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

    `assignees: list[str] | None`
    :   The type of the None singleton.

    `body: str | None`
    :   The type of the None singleton.

    `labels: list[str] | None`
    :   The type of the None singleton.

    `milestone: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str`
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

    `active_lock_reason: str | None`
    :   The type of the None singleton.

    `assignee: airbyte_agent_sdk.connectors.github.models.IssueResponseAssignee | None`
    :   The type of the None singleton.

    `assignees: list[airbyte_agent_sdk.connectors.github.models.IssueResponseAssigneesItem] | None`
    :   The type of the None singleton.

    `author_association: str | None`
    :   The type of the None singleton.

    `body: str | None`
    :   The type of the None singleton.

    `closed_at: str | None`
    :   The type of the None singleton.

    `closed_by: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `comments: int | None`
    :   The type of the None singleton.

    `comments_url: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `events_url: str | None`
    :   The type of the None singleton.

    `html_url: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `issue_dependencies_summary: airbyte_agent_sdk.connectors.github.models.IssueResponseIssueDependenciesSummary | None`
    :   The type of the None singleton.

    `issue_field_values: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `labels: list[airbyte_agent_sdk.connectors.github.models.IssueResponseLabelsItem] | None`
    :   The type of the None singleton.

    `labels_url: str | None`
    :   The type of the None singleton.

    `locked: bool | None`
    :   The type of the None singleton.

    `milestone: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | None`
    :   The type of the None singleton.

    `number: int | None`
    :   The type of the None singleton.

    `performed_via_github_app: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `pinned_comment: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `reactions: airbyte_agent_sdk.connectors.github.models.IssueResponseReactions | None`
    :   The type of the None singleton.

    `repository_url: str | None`
    :   The type of the None singleton.

    `state: str | None`
    :   The type of the None singleton.

    `state_reason: str | None`
    :   The type of the None singleton.

    `sub_issues_summary: airbyte_agent_sdk.connectors.github.models.IssueResponseSubIssuesSummary | None`
    :   The type of the None singleton.

    `timeline_url: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `type_: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.github.models.IssueResponseUser | None`
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

    `avatar_url: str | None`
    :   The type of the None singleton.

    `html_url: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `login: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | None`
    :   The type of the None singleton.

    `site_admin: bool | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `url: str | None`
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

    `avatar_url: str | None`
    :   The type of the None singleton.

    `html_url: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `login: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | None`
    :   The type of the None singleton.

    `site_admin: bool | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `url: str | None`
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

    `blocked_by: int | None`
    :   The type of the None singleton.

    `blocking: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_blocked_by: int | None`
    :   The type of the None singleton.

    `total_blocking: int | None`
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

    `color: str | None`
    :   The type of the None singleton.

    `default: bool | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `node_id: str | None`
    :   The type of the None singleton.

    `url: str | None`
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

    `confused: int | None`
    :   The type of the None singleton.

    `eyes: int | None`
    :   The type of the None singleton.

    `field_1: int | None`
    :   The type of the None singleton.

    `heart: int | None`
    :   The type of the None singleton.

    `hooray: int | None`
    :   The type of the None singleton.

    `laugh: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rocket: int | None`
    :   The type of the None singleton.

    `total_count: int | None`
    :   The type of the None singleton.

    `url: str | None`
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

    `completed: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `percent_completed: int | None`
    :   The type of the None singleton.

    `total: int | None`
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

    `avatar_url: str | None`
    :   The type of the None singleton.

    `html_url: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `login: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | None`
    :   The type of the None singleton.

    `site_admin: bool | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `url: str | None`
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

    `assignees: list[str] | None`
    :   The type of the None singleton.

    `body: str | None`
    :   The type of the None singleton.

    `labels: list[str] | None`
    :   The type of the None singleton.

    `milestone: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `state: str | None`
    :   The type of the None singleton.

    `state_reason: str | None`
    :   The type of the None singleton.

    `title: str | None`
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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_count: int | None`
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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
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

    `closed_at: str | None`
    :   ISO 8601 timestamp when the issue was closed, if applicable

    `created_at: str | None`
    :   ISO 8601 timestamp when the issue was created

    `database_id: int | None`
    :   REST API numeric identifier for the issue

    `id: str | None`
    :   GraphQL node ID of the issue

    `locked: bool | None`
    :   Whether the conversation on the issue is locked

    `model_config`
    :   The type of the None singleton.

    `number: int | None`
    :   Repository-scoped issue number

    `state: str | None`
    :   Issue state: `OPEN` or `CLOSED`

    `state_reason: str | None`
    :   Reason the issue is in its current state (e.g. `COMPLETED`, `NOT_PLANNED`)

    `title: str | None`
    :   Issue title

    `updated_at: str | None`
    :   ISO 8601 timestamp when the issue was last updated

    `url: str | None`
    :   Permalink to the issue on GitHub

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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="LabelsSearchData"></a>

`LabelsSearchData(**data: Any)`
:   Search result data for labels entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color: str | None`
    :   Label color as a 6-character hex string without a leading `#`

    `created_at: str | None`
    :   ISO 8601 timestamp when the label was created

    `description: str | None`
    :   Short description of what the label is used for

    `id: str | None`
    :   GraphQL node ID of the label

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Label name

    `url: str | None`
    :   Permalink to the label on GitHub

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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="MilestonesSearchData"></a>

`MilestonesSearchData(**data: Any)`
:   Search result data for milestones entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `closed_at: str | None`
    :   ISO 8601 timestamp when the milestone was closed, if applicable

    `created_at: str | None`
    :   ISO 8601 timestamp when the milestone was created

    `description: str | None`
    :   Milestone description

    `due_on: str | None`
    :   ISO 8601 timestamp for the milestone's due date, if set

    `id: str | None`
    :   GraphQL node ID of the milestone

    `model_config`
    :   The type of the None singleton.

    `number: int | None`
    :   Repository-scoped milestone number

    `progress_percentage: float | None`
    :   Percentage of associated issues/PRs that are closed

    `state: str | None`
    :   Milestone state: `OPEN` or `CLOSED`

    `title: str | None`
    :   Milestone title

    `updated_at: str | None`
    :   ISO 8601 timestamp when the milestone was last updated

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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="OrgRepositoriesSearchData"></a>

`OrgRepositoriesSearchData(**data: Any)`
:   Search result data for org_repositories entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
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

    `created_at: str | None`
    :   ISO 8601 timestamp when the organization was created

    `database_id: int | None`
    :   REST API numeric identifier for the organization

    `description: str | None`
    :   Short public description of the organization

    `email: str | None`
    :   Public contact email for the organization, if set

    `id: str | None`
    :   GraphQL node ID of the organization

    `is_verified: bool | None`
    :   Whether the organization has a verified domain

    `location: str | None`
    :   Public location of the organization, if set

    `login: str | None`
    :   Organization login/handle (unique URL slug)

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Display name of the organization

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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="PrCommentsSearchData"></a>

`PrCommentsSearchData(**data: Any)`
:   Search result data for pr_comments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ProjectItemsSearchData"></a>

`ProjectItemsSearchData(**data: Any)`
:   Search result data for project_items entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
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

    `closed: bool | None`
    :   Whether the project has been closed

    `created_at: str | None`
    :   ISO 8601 timestamp when the project was created

    `id: str | None`
    :   GraphQL node ID of the project

    `model_config`
    :   The type of the None singleton.

    `number: int | None`
    :   Organization- or user-scoped project number

    `public: bool | None`
    :   Whether the project is publicly visible

    `short_description: str | None`
    :   Short description displayed on the project summary

    `title: str | None`
    :   Project title

    `updated_at: str | None`
    :   ISO 8601 timestamp when the project was last updated

    `url: str | None`
    :   Permalink to the project on GitHub

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

    `base: str`
    :   The type of the None singleton.

    `body: str | None`
    :   The type of the None singleton.

    `draft: bool | None`
    :   The type of the None singleton.

    `head: str`
    :   The type of the None singleton.

    `maintainer_can_modify: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str`
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

    `additions: int | None`
    :   The type of the None singleton.

    `assignees: list[airbyte_agent_sdk.connectors.github.models.PullRequestResponseAssigneesItem] | None`
    :   The type of the None singleton.

    `author_association: str | None`
    :   The type of the None singleton.

    `base: airbyte_agent_sdk.connectors.github.models.PullRequestResponseBase | None`
    :   The type of the None singleton.

    `body: str | None`
    :   The type of the None singleton.

    `changed_files: int | None`
    :   The type of the None singleton.

    `closed_at: str | None`
    :   The type of the None singleton.

    `comments: int | None`
    :   The type of the None singleton.

    `commits: int | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `deletions: int | None`
    :   The type of the None singleton.

    `diff_url: str | None`
    :   The type of the None singleton.

    `draft: bool | None`
    :   The type of the None singleton.

    `head: airbyte_agent_sdk.connectors.github.models.PullRequestResponseHead | None`
    :   The type of the None singleton.

    `html_url: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `labels: list[airbyte_agent_sdk.connectors.github.models.PullRequestResponseLabelsItem] | None`
    :   The type of the None singleton.

    `locked: bool | None`
    :   The type of the None singleton.

    `merge_commit_sha: str | None`
    :   The type of the None singleton.

    `merged_at: str | None`
    :   The type of the None singleton.

    `milestone: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | None`
    :   The type of the None singleton.

    `number: int | None`
    :   The type of the None singleton.

    `patch_url: str | None`
    :   The type of the None singleton.

    `requested_reviewers: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `review_comments: int | None`
    :   The type of the None singleton.

    `state: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

    `user: airbyte_agent_sdk.connectors.github.models.PullRequestResponseUser | None`
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

    `avatar_url: str | None`
    :   The type of the None singleton.

    `html_url: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `login: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | None`
    :   The type of the None singleton.

    `site_admin: bool | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `url: str | None`
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

    `label: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ref: str | None`
    :   The type of the None singleton.

    `sha: str | None`
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

    `label: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ref: str | None`
    :   The type of the None singleton.

    `sha: str | None`
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

    `color: str | None`
    :   The type of the None singleton.

    `default: bool | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `node_id: str | None`
    :   The type of the None singleton.

    `url: str | None`
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

    `avatar_url: str | None`
    :   The type of the None singleton.

    `html_url: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `login: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `node_id: str | None`
    :   The type of the None singleton.

    `site_admin: bool | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `url: str | None`
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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_count: int | None`
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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
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

    `base_ref_name: str | None`
    :   Name of the branch being merged into

    `closed_at: str | None`
    :   ISO 8601 timestamp when the pull request was closed, if applicable

    `created_at: str | None`
    :   ISO 8601 timestamp when the pull request was created

    `database_id: int | None`
    :   REST API numeric identifier for the pull request

    `head_ref_name: str | None`
    :   Name of the branch with the proposed changes

    `id: str | None`
    :   GraphQL node ID of the pull request

    `is_draft: bool | None`
    :   Whether the pull request is still a draft

    `merged: bool | None`
    :   Whether the pull request has been merged

    `merged_at: str | None`
    :   ISO 8601 timestamp when the pull request was merged, if applicable

    `model_config`
    :   The type of the None singleton.

    `number: int | None`
    :   Repository-scoped pull request number

    `state: str | None`
    :   Pull request state: `OPEN`, `CLOSED`, or `MERGED`

    `title: str | None`
    :   Pull request title

    `updated_at: str | None`
    :   ISO 8601 timestamp when the pull request was last updated

    `url: str | None`
    :   Permalink to the pull request on GitHub

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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
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

    `created_at: str | None`
    :   ISO 8601 timestamp when the release was created

    `database_id: int | None`
    :   REST API numeric identifier for the release

    `description: str | None`
    :   Markdown body / release notes

    `id: str | None`
    :   GraphQL node ID of the release

    `is_draft: bool | None`
    :   Whether the release is still a draft and not published

    `is_prerelease: bool | None`
    :   Whether the release is marked as a pre-release

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Display name of the release

    `published_at: str | None`
    :   ISO 8601 timestamp when the release was published

    `tag_name: str | None`
    :   Git tag the release points at (e.g. `v1.2.3`)

    `url: str | None`
    :   Permalink to the release on GitHub

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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_count: int | None`
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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
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

    `created_at: str | None`
    :   ISO 8601 timestamp when the repository was created

    `description: str | None`
    :   Short description of the repository

    `fork_count: int | None`
    :   Number of forks of the repository

    `id: str | None`
    :   GraphQL node ID of the repository

    `is_archived: bool | None`
    :   Whether the repository has been archived

    `is_fork: bool | None`
    :   Whether the repository is a fork of another repository

    `is_private: bool | None`
    :   Whether the repository is private

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Short repository name (without owner)

    `name_with_owner: str | None`
    :   Fully-qualified `owner/name` identifier for the repository

    `pushed_at: str | None`
    :   ISO 8601 timestamp of the most recent push to the repository

    `stargazer_count: int | None`
    :   Number of users who have starred the repository

    `updated_at: str | None`
    :   ISO 8601 timestamp when the repository was last updated

    `url: str | None`
    :   Canonical GitHub URL for the repository

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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ReviewsSearchData"></a>

`ReviewsSearchData(**data: Any)`
:   Search result data for reviews entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body: str | None`
    :   Review body text

    `created_at: str | None`
    :   ISO 8601 timestamp when the review was created

    `database_id: int | None`
    :   REST API numeric identifier for the review

    `id: str | None`
    :   GraphQL node ID of the review

    `model_config`
    :   The type of the None singleton.

    `state: str | None`
    :   Review state: `PENDING`, `COMMENTED`, `APPROVED`, `CHANGES_REQUESTED`, or `DISMISSED`

    `submitted_at: str | None`
    :   ISO 8601 timestamp when the review was submitted

    `updated_at: str | None`
    :   ISO 8601 timestamp when the review was last updated

    `url: str | None`
    :   Permalink to the review on GitHub

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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
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

    `starred_at: str | None`
    :   ISO 8601 timestamp when the user starred the repository

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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
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

    `name: str | None`
    :   Tag name (e.g. `v1.2.3`)

    `prefix: str | None`
    :   Git ref prefix for the tag (typically `refs/tags/`)

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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
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

    `created_at: str | None`
    :   ISO 8601 timestamp when the team was created

    `database_id: int | None`
    :   REST API numeric identifier for the team

    `description: str | None`
    :   Short description of the team

    `id: str | None`
    :   GraphQL node ID of the team

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Display name of the team

    `privacy: str | None`
    :   Team visibility: `SECRET` or `VISIBLE`

    `slug: str | None`
    :   URL-friendly slug for the team within its organization

    `updated_at: str | None`
    :   ISO 8601 timestamp when the team was last updated

    `url: str | None`
    :   Permalink to the team on GitHub

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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_count: int | None`
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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
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

    `company: str | None`
    :   Public company affiliation of the user, if set

    `created_at: str | None`
    :   ISO 8601 timestamp when the user account was created

    `database_id: int | None`
    :   REST API numeric identifier for the user

    `email: str | None`
    :   Public email address of the user, if set

    `id: str | None`
    :   GraphQL node ID of the user

    `is_hireable: bool | None`
    :   Whether the user has marked themselves as available for hire

    `location: str | None`
    :   Public location of the user, if set

    `login: str | None`
    :   User login/handle

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Public display name of the user, if set

    `twitter_username: str | None`
    :   Public Twitter/X username of the user, if set

    `url: str | None`
    :   Permalink to the user's profile on GitHub

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

    `end_cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ViewerRepositoriesSearchData"></a>

`ViewerRepositoriesSearchData(**data: Any)`
:   Search result data for viewer_repositories entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ViewerSearchData"></a>

`ViewerSearchData(**data: Any)`
:   Search result data for viewer entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.