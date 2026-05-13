---
id: airbyte_agent_sdk-connectors-github-index
title: airbyte_agent_sdk.connectors.github.index
---

Module airbyte_agent_sdk.connectors.github
==========================================
Github connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.github.connector
* airbyte_agent_sdk.connectors.github.connector_model
* airbyte_agent_sdk.connectors.github.models
* airbyte_agent_sdk.connectors.github.types

Classes
-------

<a id="AirbyteAuthConfig"></a>

`AirbyteAuthConfig(**data: Any)`
:   Authentication configuration for Airbyte hosted mode execution.
    
    Pass this to the connector's `auth_config` parameter to use hosted mode,
    where API credentials are stored securely in Airbyte Cloud.
    
    For hosted mode execution, provide client credentials with either:
    - `connector_id`: Direct connector/source ID (skips lookup)
    - `workspace_name`: Workspace name for connector lookup
    
    Attributes:
        workspace_name: Workspace name for hosted mode connector lookup
        organization_id: Optional Airbyte organization ID for multi-org selection
        airbyte_client_id: Airbyte OAuth client ID (required for hosted mode)
        airbyte_client_secret: Airbyte OAuth client secret (required for hosted mode)
        connector_id: Specific connector/source ID (skips lookup if provided)
    
    Examples:
        # Hosted mode with connector_id (no lookup needed)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with workspace_name (lookup by workspace)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `airbyte_client_id: str | None`
    :   The type of the None singleton.

    `airbyte_client_secret: str | None`
    :   The type of the None singleton.

    `connector_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organization_id: str | None`
    :   The type of the None singleton.

    `workspace_name: str | None`
    :   The type of the None singleton.

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

<a id="GithubConnector"></a>

`GithubConnector(auth_config: GithubAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None)`
:   Type-safe Github API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new github connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., GithubAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)
    Examples:
        # Local mode (direct API calls)
        connector = GithubConnector(auth_config=GithubAuthConfig(access_token="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = GithubConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = GithubConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )

    ### Class variables

    `connector_name`
    :   The type of the None singleton.

    `connector_version`
    :   The type of the None singleton.

    `sdk_version`
    :   The type of the None singleton.

    ### Static methods

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000, framework: FrameworkName | None = None, internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Composes :func:`airbyte_agent_sdk.translation.translate_exceptions` for
        runtime wrapping (sync/async branch + output-size check + framework
        signal translation + optional internal retry loop), and adds
        connector-specific docstring augmentation on top of it.
        
        Usage:
            @mcp.tool()
            @GithubConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @GithubConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @GithubConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
            async def execute(entity: str, action: str, params: dict):
                ...
        
        Args:
            update_docstring: When True, append connector capabilities to __doc__.
            max_output_chars: Max serialized output size before raising. Use None to disable.
            framework: One of ``"pydantic_ai" | "langchain" | "openai_agents" | "mcp"``.
                Defaults to None → auto-detect by attempting each framework's canonical
                import in order. Explicit always wins.
            internal_retries: How many transient runtime failures (429/5xx, network,
                timeout) to retry silently before surfacing. Default 0. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            should_internal_retry: Optional predicate ``(error, args, kwargs) -> bool``
                further restricting which retryable errors are safe for this specific
                tool. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            exhausted_runtime_failure_message: Optional callback
                ``(error, args, kwargs) -> str | None``. Invoked after internal retries
                are exhausted OR were skipped via ``should_internal_retry`` returning
                False. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.github.models.GithubCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            GithubCheckResult with status ("healthy" or "unhealthy") and optional error message
        
        Example:
            result = await connector.check()
            if result.status == "healthy":
                print("Connection verified!")
            else:
                print(f"Check failed: \{result.error\}")

    `close(self)`
    :   Close the connector and release resources.

    `entity_schema(self, entity: str) ‑> dict[str, typing.Any] | None`
    :   Get the JSON schema for an entity.
        
        Args:
            entity: Entity name (e.g., "contacts", "companies")
        
        Returns:
            JSON schema dict describing the entity structure, or None if not found.
        
        Example:
            schema = connector.entity_schema("contacts")
            if schema:
                print(f"Contact properties: \{list(schema.get('properties', \{\}).keys())\}")

    `execute(self, entity: str, action: "Literal['get', 'list', 'api_search', 'create', 'update', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
    :   Execute an entity operation with full type safety.
        
        This is the recommended interface for blessed connectors as it:
        - Uses the same signature as non-blessed connectors
        - Provides full IDE autocomplete for entity/action/params
        - Makes migration from generic to blessed connectors seamless
        
        Args:
            entity: Entity name (e.g., "customers")
            action: Operation action (e.g., "create", "get", "list")
            params: Operation parameters (typed based on entity+action)
        
        Returns:
            Typed response based on the operation
        
        Example:
            customer = await connector.execute(
                entity="customers",
                action="get",
                params=\{"id": "cus_123"\}
            )

    `list_entities(self) ‑> list[dict[str, typing.Any]]`
    :   Get structured data about available entities, actions, and parameters.
        
        Returns a list of entity descriptions with:
        - entity_name: Name of the entity (e.g., "contacts", "deals")
        - description: Entity description from the first endpoint
        - available_actions: List of actions (e.g., ["list", "get", "create"])
        - parameters: Dict mapping action -> list of parameter dicts
        
        Example:
            entities = connector.list_entities()
            for entity in entities:
                print(f"\{entity['entity_name']\}: \{entity['available_actions']\}")

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

    `start_date: str`
    :   UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data.

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