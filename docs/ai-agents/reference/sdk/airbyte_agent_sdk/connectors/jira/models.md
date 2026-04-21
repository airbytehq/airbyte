---
id: airbyte_agent_sdk-connectors-jira-models
title: airbyte_agent_sdk.connectors.jira.models
---

Module airbyte_agent_sdk.connectors.jira.models
===============================================
Pydantic models for jira connector.

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

    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult[IssueCommentsSearchData]
    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult[IssueFieldsSearchData]
    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult[IssueWorklogsSearchData]
    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult[IssuesSearchData]
    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult[ProjectsSearchData]
    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.jira.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[IssueCommentsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IssueCommentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[IssueFieldsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IssueFieldsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[IssueWorklogsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IssueWorklogsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[IssuesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ProjectsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.jira.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`CommentCreateParams(**data: Any)`
:   Parameters for creating a comment on an issue
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body: airbyte_agent_sdk.connectors.jira.models.CommentCreateParamsBody | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `visibility: airbyte_agent_sdk.connectors.jira.models.CommentCreateParamsVisibility | Any`
    :   The type of the None singleton.

`CommentCreateParamsBody(**data: Any)`
:   Comment content in Atlassian Document Format (ADF)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.models.CommentCreateParamsBodyContentItem] | Any`
    :   Array of content blocks

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Document type (always 'doc')

    `version: int | Any`
    :   ADF version

`CommentCreateParamsBodyContentItem(**data: Any)`
:   Nested schema for CommentCreateParamsBody.content_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.models.CommentCreateParamsBodyContentItemContentItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Block type (e.g., 'paragraph')

`CommentCreateParamsBodyContentItemContentItem(**data: Any)`
:   Nested schema for CommentCreateParamsBodyContentItem.content_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `text: str | Any`
    :   Text content

    `type_: str | Any`
    :   Content type (e.g., 'text')

`CommentCreateParamsVisibility(**data: Any)`
:   Restrict comment visibility to a group or role
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `identifier: str | Any`
    :   The ID of the group or role

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of visibility restriction

    `value: str | Any`
    :   The name of the group or role

`CommentUpdateParams(**data: Any)`
:   Parameters for updating a comment. Only fields included are updated.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body: airbyte_agent_sdk.connectors.jira.models.CommentUpdateParamsBody | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `visibility: airbyte_agent_sdk.connectors.jira.models.CommentUpdateParamsVisibility | Any`
    :   The type of the None singleton.

`CommentUpdateParamsBody(**data: Any)`
:   Updated comment content in Atlassian Document Format (ADF)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.models.CommentUpdateParamsBodyContentItem] | Any`
    :   Array of content blocks

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Document type (always 'doc')

    `version: int | Any`
    :   ADF version

`CommentUpdateParamsBodyContentItem(**data: Any)`
:   Nested schema for CommentUpdateParamsBody.content_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.models.CommentUpdateParamsBodyContentItemContentItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Block type (e.g., 'paragraph')

`CommentUpdateParamsBodyContentItemContentItem(**data: Any)`
:   Nested schema for CommentUpdateParamsBodyContentItem.content_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `text: str | Any`
    :   Text content

    `type_: str | Any`
    :   Content type (e.g., 'text')

`CommentUpdateParamsVisibility(**data: Any)`
:   Restrict comment visibility to a group or role
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `identifier: str | Any`
    :   The ID of the group or role

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of visibility restriction

    `value: str | Any`
    :   The name of the group or role

`EmptyResponse(**data: Any)`
:   Empty response object (returned for 204 No Content responses)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`Issue(**data: Any)`
:   Jira issue object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `expand: str | Any | None`
    :   The type of the None singleton.

    `fields: airbyte_agent_sdk.connectors.jira.models.IssueFields | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `key: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

`IssueAssigneeParams(**data: Any)`
:   Parameters for assigning an issue to a user
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`IssueComment(**data: Any)`
:   Jira issue comment object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author: airbyte_agent_sdk.connectors.jira.models.IssueCommentAuthor | Any`
    :   The type of the None singleton.

    `body: airbyte_agent_sdk.connectors.jira.models.IssueCommentBody | Any`
    :   The type of the None singleton.

    `created: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `jsd_public: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `rendered_body: str | Any | None`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

    `update_author: airbyte_agent_sdk.connectors.jira.models.IssueCommentUpdateauthor | Any`
    :   The type of the None singleton.

    `updated: str | Any`
    :   The type of the None singleton.

    `visibility: airbyte_agent_sdk.connectors.jira.models.IssueCommentVisibility | Any | None`
    :   The type of the None singleton.

`IssueCommentAuthor(**data: Any)`
:   Comment author user information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any`
    :   The type of the None singleton.

    `account_type: str | Any`
    :   The type of the None singleton.

    `active: bool | Any`
    :   The type of the None singleton.

    `avatar_urls: airbyte_agent_sdk.connectors.jira.models.IssueCommentAuthorAvatarurls | Any`
    :   URLs for user avatars in different sizes

    `display_name: str | Any`
    :   The type of the None singleton.

    `email_address: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

    `time_zone: str | Any`
    :   The type of the None singleton.

`IssueCommentAuthorAvatarurls(**data: Any)`
:   URLs for user avatars in different sizes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_16x16: str | Any`
    :   The type of the None singleton.

    `field_24x24: str | Any`
    :   The type of the None singleton.

    `field_32x32: str | Any`
    :   The type of the None singleton.

    `field_48x48: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`IssueCommentBody(**data: Any)`
:   Comment content in ADF (Atlassian Document Format)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.models.IssueCommentBodyContentItem] | Any`
    :   Array of content blocks

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Document type (always 'doc')

    `version: int | Any`
    :   ADF version

`IssueCommentBodyContentItem(**data: Any)`
:   Nested schema for IssueCommentBody.content_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.models.IssueCommentBodyContentItemContentItem] | Any`
    :   Nested content items

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Block type (e.g., 'paragraph')

`IssueCommentBodyContentItemContentItem(**data: Any)`
:   Nested schema for IssueCommentBodyContentItem.content_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `text: str | Any`
    :   Text content

    `type_: str | Any`
    :   Content type (e.g., 'text')

`IssueCommentUpdateauthor(**data: Any)`
:   User who last updated the comment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any`
    :   The type of the None singleton.

    `account_type: str | Any`
    :   The type of the None singleton.

    `active: bool | Any`
    :   The type of the None singleton.

    `avatar_urls: airbyte_agent_sdk.connectors.jira.models.IssueCommentUpdateauthorAvatarurls | Any`
    :   URLs for user avatars in different sizes

    `display_name: str | Any`
    :   The type of the None singleton.

    `email_address: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

    `time_zone: str | Any`
    :   The type of the None singleton.

`IssueCommentUpdateauthorAvatarurls(**data: Any)`
:   URLs for user avatars in different sizes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_16x16: str | Any`
    :   The type of the None singleton.

    `field_24x24: str | Any`
    :   The type of the None singleton.

    `field_32x32: str | Any`
    :   The type of the None singleton.

    `field_48x48: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`IssueCommentVisibility(**data: Any)`
:   Visibility restrictions for the comment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `identifier: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `value: str | Any`
    :   The type of the None singleton.

`IssueCommentsList(**data: Any)`
:   Paginated list of issue comments
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `comments: list[airbyte_agent_sdk.connectors.jira.models.IssueComment] | Any`
    :   The type of the None singleton.

    `max_results: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start_at: int | Any`
    :   The type of the None singleton.

    `total: int | Any`
    :   The type of the None singleton.

`IssueCommentsListResultMeta(**data: Any)`
:   Metadata for issue_comments.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `max_results: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_offset: int | Any`
    :   The type of the None singleton.

    `total: int | Any`
    :   The type of the None singleton.

`IssueCommentsSearchData(**data: Any)`
:   Search result data for issue_comments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author: dict[str, typing.Any] | None`
    :   The ID of the user who created the comment

    `body: dict[str, typing.Any]`
    :   The comment text in Atlassian Document Format

    `created: str`
    :   The date and time at which the comment was created

    `id: str`
    :   The ID of the comment

    `issue_id: str | None`
    :   Id of the related issue

    `jsd_public: bool`
    :   Whether the comment is visible in Jira Service Desk

    `model_config`
    :   The type of the None singleton.

    `properties: list[typing.Any]`
    :   A list of comment properties

    `rendered_body: str | None`
    :   The rendered version of the comment

    `self: str`
    :   The URL of the comment

    `update_author: dict[str, typing.Any] | None`
    :   The ID of the user who updated the comment last

    `updated: str`
    :   The date and time at which the comment was updated last

    `visibility: dict[str, typing.Any] | None`
    :   The group or role to which this item is visible

`IssueCreateParams(**data: Any)`
:   Parameters for creating a new issue
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `fields: airbyte_agent_sdk.connectors.jira.models.IssueCreateParamsFields | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `update: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

`IssueCreateParamsFields(**data: Any)`
:   The issue fields to set
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee: airbyte_agent_sdk.connectors.jira.models.IssueCreateParamsFieldsAssignee | Any`
    :   The user to assign the issue to

    `description: airbyte_agent_sdk.connectors.jira.models.IssueCreateParamsFieldsDescription | Any`
    :   Issue description in Atlassian Document Format (ADF)

    `issuetype: airbyte_agent_sdk.connectors.jira.models.IssueCreateParamsFieldsIssuetype | Any`
    :   The type of issue (e.g., Bug, Task, Story)

    `labels: list[str] | Any`
    :   Labels to add to the issue

    `model_config`
    :   The type of the None singleton.

    `parent: airbyte_agent_sdk.connectors.jira.models.IssueCreateParamsFieldsParent | Any`
    :   Parent issue for subtasks

    `priority: airbyte_agent_sdk.connectors.jira.models.IssueCreateParamsFieldsPriority | Any`
    :   Issue priority

    `project: airbyte_agent_sdk.connectors.jira.models.IssueCreateParamsFieldsProject | Any`
    :   The project to create the issue in

    `summary: str | Any`
    :   A brief summary of the issue (title)

`IssueCreateParamsFieldsAssignee(**data: Any)`
:   The user to assign the issue to
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any`
    :   The account ID of the user

    `model_config`
    :   The type of the None singleton.

`IssueCreateParamsFieldsDescription(**data: Any)`
:   Issue description in Atlassian Document Format (ADF)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.models.IssueCreateParamsFieldsDescriptionContentItem] | Any`
    :   Array of content blocks

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Document type (always 'doc')

    `version: int | Any`
    :   ADF version

`IssueCreateParamsFieldsDescriptionContentItem(**data: Any)`
:   Nested schema for IssueCreateParamsFieldsDescription.content_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.models.IssueCreateParamsFieldsDescriptionContentItemContentItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Block type (e.g., 'paragraph')

`IssueCreateParamsFieldsDescriptionContentItemContentItem(**data: Any)`
:   Nested schema for IssueCreateParamsFieldsDescriptionContentItem.content_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `text: str | Any`
    :   Text content

    `type_: str | Any`
    :   Content type (e.g., 'text')

`IssueCreateParamsFieldsIssuetype(**data: Any)`
:   The type of issue (e.g., Bug, Task, Story)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   Issue type ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Issue type name (e.g., 'Bug', 'Task', 'Story')

`IssueCreateParamsFieldsParent(**data: Any)`
:   Parent issue for subtasks
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `key: str | Any`
    :   Parent issue key

    `model_config`
    :   The type of the None singleton.

`IssueCreateParamsFieldsPriority(**data: Any)`
:   Issue priority
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   Priority ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Priority name (e.g., 'Highest', 'High', 'Medium', 'Low', 'Lowest')

`IssueCreateParamsFieldsProject(**data: Any)`
:   The project to create the issue in
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   Project ID

    `key: str | Any`
    :   Project key (e.g., 'PROJ')

    `model_config`
    :   The type of the None singleton.

`IssueCreateResponse(**data: Any)`
:   Response from creating an issue
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `key: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

`IssueField(**data: Any)`
:   Jira issue field object (custom or system field)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `clause_names: list[str] | Any | None`
    :   The type of the None singleton.

    `contexts_count: int | Any | None`
    :   The type of the None singleton.

    `custom: bool | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_locked: bool | Any | None`
    :   The type of the None singleton.

    `key: str | Any | None`
    :   The type of the None singleton.

    `last_used: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `navigable: bool | Any | None`
    :   The type of the None singleton.

    `orderable: bool | Any | None`
    :   The type of the None singleton.

    `schema_: airbyte_agent_sdk.connectors.jira.models.IssueFieldSchema | Any | None`
    :   The type of the None singleton.

    `screens_count: int | Any | None`
    :   The type of the None singleton.

    `searchable: bool | Any | None`
    :   The type of the None singleton.

    `searcher_key: str | Any | None`
    :   The type of the None singleton.

    `type_display_name: str | Any | None`
    :   The type of the None singleton.

    `untranslated_name: str | Any | None`
    :   The type of the None singleton.

`IssueFieldSchema(**data: Any)`
:   Schema information for the field
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `configuration: dict[str, typing.Any] | Any | None`
    :   Field configuration

    `custom: str | Any | None`
    :   Custom field type identifier

    `custom_id: int | Any | None`
    :   Custom field ID

    `items: str | Any | None`
    :   Type of items in array fields

    `model_config`
    :   The type of the None singleton.

    `system: str | Any | None`
    :   System field identifier

    `type_: str | Any`
    :   Field type (e.g., string, number, array)

`IssueFieldSearchResults(**data: Any)`
:   Paginated search results for issue fields
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `is_last: bool | Any`
    :   The type of the None singleton.

    `max_results: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start_at: int | Any`
    :   The type of the None singleton.

    `total: int | Any`
    :   The type of the None singleton.

    `values: list[airbyte_agent_sdk.connectors.jira.models.IssueField] | Any`
    :   The type of the None singleton.

`IssueFields(**data: Any)`
:   Issue fields (actual fields depend on 'fields' parameter in request)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee: airbyte_agent_sdk.connectors.jira.models.IssueFieldsAssignee | Any | None`
    :   Issue assignee user information (null if unassigned)

    `created: str | Any`
    :   Issue creation timestamp

    `issuetype: airbyte_agent_sdk.connectors.jira.models.IssueFieldsIssuetype | Any`
    :   Issue type information

    `model_config`
    :   The type of the None singleton.

    `priority: airbyte_agent_sdk.connectors.jira.models.IssueFieldsPriority | Any | None`
    :   Issue priority information

    `project: airbyte_agent_sdk.connectors.jira.models.IssueFieldsProject | Any`
    :   Project information

    `reporter: airbyte_agent_sdk.connectors.jira.models.IssueFieldsReporter | Any | None`
    :   Issue reporter user information

    `status: airbyte_agent_sdk.connectors.jira.models.IssueFieldsStatus | Any`
    :   Issue status information

    `summary: str | Any`
    :   Issue summary/title

    `updated: str | Any`
    :   Issue last update timestamp

`IssueFieldsAssignee(**data: Any)`
:   Issue assignee user information (null if unassigned)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any`
    :   The type of the None singleton.

    `account_type: str | Any`
    :   The type of the None singleton.

    `active: bool | Any`
    :   The type of the None singleton.

    `avatar_urls: airbyte_agent_sdk.connectors.jira.models.IssueFieldsAssigneeAvatarurls | Any`
    :   URLs for user avatars in different sizes

    `display_name: str | Any`
    :   The type of the None singleton.

    `email_address: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

    `time_zone: str | Any`
    :   The type of the None singleton.

`IssueFieldsAssigneeAvatarurls(**data: Any)`
:   URLs for user avatars in different sizes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_16x16: str | Any`
    :   The type of the None singleton.

    `field_24x24: str | Any`
    :   The type of the None singleton.

    `field_32x32: str | Any`
    :   The type of the None singleton.

    `field_48x48: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`IssueFieldsIssuetype(**data: Any)`
:   Issue type information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_id: int | Any | None`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `hierarchy_level: int | Any | None`
    :   The type of the None singleton.

    `icon_url: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

    `subtask: bool | Any`
    :   The type of the None singleton.

`IssueFieldsPriority(**data: Any)`
:   Issue priority information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `icon_url: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

`IssueFieldsProject(**data: Any)`
:   Project information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_urls: airbyte_agent_sdk.connectors.jira.models.IssueFieldsProjectAvatarurls | Any`
    :   URLs for user avatars in different sizes

    `id: str | Any`
    :   The type of the None singleton.

    `key: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `project_category: airbyte_agent_sdk.connectors.jira.models.IssueFieldsProjectProjectcategory | Any | None`
    :   The type of the None singleton.

    `project_type_key: str | Any`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

    `simplified: bool | Any`
    :   The type of the None singleton.

`IssueFieldsProjectAvatarurls(**data: Any)`
:   URLs for user avatars in different sizes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_16x16: str | Any`
    :   The type of the None singleton.

    `field_24x24: str | Any`
    :   The type of the None singleton.

    `field_32x32: str | Any`
    :   The type of the None singleton.

    `field_48x48: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`IssueFieldsProjectProjectcategory(**data: Any)`
:   Nested schema for IssueFieldsProject.projectCategory
    
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

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

`IssueFieldsReporter(**data: Any)`
:   Issue reporter user information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any`
    :   The type of the None singleton.

    `account_type: str | Any`
    :   The type of the None singleton.

    `active: bool | Any`
    :   The type of the None singleton.

    `avatar_urls: airbyte_agent_sdk.connectors.jira.models.IssueFieldsReporterAvatarurls | Any`
    :   URLs for user avatars in different sizes

    `display_name: str | Any`
    :   The type of the None singleton.

    `email_address: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

    `time_zone: str | Any`
    :   The type of the None singleton.

`IssueFieldsReporterAvatarurls(**data: Any)`
:   URLs for user avatars in different sizes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_16x16: str | Any`
    :   The type of the None singleton.

    `field_24x24: str | Any`
    :   The type of the None singleton.

    `field_32x32: str | Any`
    :   The type of the None singleton.

    `field_48x48: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`IssueFieldsSearchData(**data: Any)`
:   Search result data for issue_fields entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `clause_names: list[typing.Any]`
    :   The names that can be used to reference the field in an advanced search

    `custom: bool`
    :   Whether the field is a custom field

    `id: str`
    :   The ID of the field

    `key: str | None`
    :   The key of the field

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The name of the field

    `navigable: bool`
    :   Whether the field can be used as a column on the issue navigator

    `orderable: bool`
    :   Whether the content of the field can be used to order lists

    `schema_: dict[str, typing.Any] | None`
    :   The data schema for the field

    `scope: dict[str, typing.Any] | None`
    :   The scope of the field

    `searchable: bool`
    :   Whether the content of the field can be searched

    `untranslated_name: str | None`
    :   The untranslated name of the field

`IssueFieldsStatus(**data: Any)`
:   Issue status information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | Any`
    :   The type of the None singleton.

    `icon_url: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

    `status_category: airbyte_agent_sdk.connectors.jira.models.IssueFieldsStatusStatuscategory | Any`
    :   The type of the None singleton.

`IssueFieldsStatusStatuscategory(**data: Any)`
:   Nested schema for IssueFieldsStatus.statusCategory
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `color_name: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `key: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

`IssueUpdateParams(**data: Any)`
:   Parameters for updating an issue. Only fields included are updated.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `fields: airbyte_agent_sdk.connectors.jira.models.IssueUpdateParamsFields | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `transition: airbyte_agent_sdk.connectors.jira.models.IssueUpdateParamsTransition | Any`
    :   The type of the None singleton.

    `update: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

`IssueUpdateParamsFields(**data: Any)`
:   The issue fields to update
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee: airbyte_agent_sdk.connectors.jira.models.IssueUpdateParamsFieldsAssignee | Any`
    :   The user to assign the issue to

    `description: airbyte_agent_sdk.connectors.jira.models.IssueUpdateParamsFieldsDescription | Any`
    :   Issue description in Atlassian Document Format (ADF)

    `labels: list[str] | Any`
    :   Labels for the issue

    `model_config`
    :   The type of the None singleton.

    `priority: airbyte_agent_sdk.connectors.jira.models.IssueUpdateParamsFieldsPriority | Any`
    :   Issue priority

    `summary: str | Any`
    :   A brief summary of the issue (title)

`IssueUpdateParamsFieldsAssignee(**data: Any)`
:   The user to assign the issue to
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any`
    :   The account ID of the user (use null to unassign)

    `model_config`
    :   The type of the None singleton.

`IssueUpdateParamsFieldsDescription(**data: Any)`
:   Issue description in Atlassian Document Format (ADF)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.models.IssueUpdateParamsFieldsDescriptionContentItem] | Any`
    :   Array of content blocks

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Document type (always 'doc')

    `version: int | Any`
    :   ADF version

`IssueUpdateParamsFieldsDescriptionContentItem(**data: Any)`
:   Nested schema for IssueUpdateParamsFieldsDescription.content_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.models.IssueUpdateParamsFieldsDescriptionContentItemContentItem] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Block type (e.g., 'paragraph')

`IssueUpdateParamsFieldsDescriptionContentItemContentItem(**data: Any)`
:   Nested schema for IssueUpdateParamsFieldsDescriptionContentItem.content_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `text: str | Any`
    :   Text content

    `type_: str | Any`
    :   Content type (e.g., 'text')

`IssueUpdateParamsFieldsPriority(**data: Any)`
:   Issue priority
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   Priority ID

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   Priority name (e.g., 'Highest', 'High', 'Medium', 'Low', 'Lowest')

`IssueUpdateParamsTransition(**data: Any)`
:   Transition the issue to a new status
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The ID of the transition to perform

    `model_config`
    :   The type of the None singleton.

`IssueWorklogsListResultMeta(**data: Any)`
:   Metadata for issue_worklogs.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `max_results: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_offset: int | Any`
    :   The type of the None singleton.

    `total: int | Any`
    :   The type of the None singleton.

`IssueWorklogsSearchData(**data: Any)`
:   Search result data for issue_worklogs entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author: dict[str, typing.Any]`
    :   Details of the user who created the worklog

    `comment: dict[str, typing.Any] | None`
    :   A comment about the worklog in Atlassian Document Format

    `created: str`
    :   The datetime on which the worklog was created

    `id: str`
    :   The ID of the worklog record

    `issue_id: str`
    :   The ID of the issue this worklog is for

    `model_config`
    :   The type of the None singleton.

    `properties: list[typing.Any]`
    :   Details of properties for the worklog

    `self: str`
    :   The URL of the worklog item

    `started: str`
    :   The datetime on which the worklog effort was started

    `time_spent: str | None`
    :   The time spent working on the issue as days, hours, or minutes

    `time_spent_seconds: int`
    :   The time in seconds spent working on the issue

    `update_author: dict[str, typing.Any] | None`
    :   Details of the user who last updated the worklog

    `updated: str`
    :   The datetime on which the worklog was last updated

    `visibility: dict[str, typing.Any] | None`
    :   Details about any restrictions in the visibility of the worklog

`IssuesApiSearchResultMeta(**data: Any)`
:   Metadata for issues.Action.API_SEARCH operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `is_last: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any | None`
    :   The type of the None singleton.

    `total: int | Any`
    :   The type of the None singleton.

`IssuesList(**data: Any)`
:   Paginated list of issues from JQL search
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `is_last: bool | Any | None`
    :   The type of the None singleton.

    `issues: list[airbyte_agent_sdk.connectors.jira.models.Issue] | Any`
    :   The type of the None singleton.

    `max_results: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page_token: str | Any | None`
    :   The type of the None singleton.

    `start_at: int | Any | None`
    :   The type of the None singleton.

    `total: int | Any`
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

    `changelog: dict[str, typing.Any] | None`
    :   Details of changelogs associated with the issue

    `created: str | None`
    :   The timestamp when the issue was created

    `editmeta: dict[str, typing.Any] | None`
    :   The metadata for the fields on the issue that can be amended

    `expand: str`
    :   Expand options that include additional issue details in the response

    `fields: dict[str, typing.Any]`
    :   Details of various fields associated with the issue

    `fields_to_include: dict[str, typing.Any]`
    :   Specify the fields to include in the fetched issues data

    `id: str`
    :   The unique ID of the issue

    `key: str`
    :   The unique key of the issue

    `model_config`
    :   The type of the None singleton.

    `names: dict[str, typing.Any]`
    :   The ID and name of each field present on the issue

    `operations: dict[str, typing.Any] | None`
    :   The operations that can be performed on the issue

    `project_id: str`
    :   The ID of the project containing the issue

    `project_key: str`
    :   The key of the project containing the issue

    `properties: dict[str, typing.Any]`
    :   Details of the issue properties identified in the request

    `rendered_fields: dict[str, typing.Any]`
    :   The rendered value of each field present on the issue

    `schema_: dict[str, typing.Any]`
    :   The schema describing each field present on the issue

    `self: str`
    :   The URL of the issue details

    `transitions: list[typing.Any]`
    :   The transitions that can be performed on the issue

    `updated: str | None`
    :   The timestamp when the issue was last updated

    `versioned_representations: dict[str, typing.Any]`
    :   The versions of each field on the issue

`JiraAuthConfig(**data: Any)`
:   Jira API Token Authentication - Authenticate using your Atlassian account email and API token
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `password: str`
    :   Your Jira API token from https://id.atlassian.com/manage-profile/security/api-tokens

    `username: str`
    :   Your Atlassian account email address

`JiraCheckResult(**data: Any)`
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

`JiraExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult[IssueFieldSearchResults]
    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult[list[IssueField]]
    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult[list[User]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

`JiraExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResultWithMeta[list[IssueComment], IssueCommentsListResultMeta]
    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResultWithMeta[list[Issue], IssuesApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResultWithMeta[list[Project], ProjectsApiSearchResultMeta]
    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResultWithMeta[list[Worklog], IssueWorklogsListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`JiraExecuteResultWithMeta[list[IssueComment], IssueCommentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IssueCommentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`JiraExecuteResultWithMeta[list[Issue], IssuesApiSearchResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IssuesApiSearchResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`JiraExecuteResultWithMeta[list[Project], ProjectsApiSearchResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`ProjectsApiSearchResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`JiraExecuteResultWithMeta[list[Worklog], IssueWorklogsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IssueWorklogsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`JiraExecuteResult[IssueFieldSearchResults](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IssueFieldsApiSearchResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`JiraExecuteResult[list[IssueField]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`IssueFieldsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`JiraExecuteResult[list[User]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`UsersListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

`UsersApiSearchResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.jira.models.JiraExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`Project(**data: Any)`
:   Jira project object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee_type: str | Any | None`
    :   The type of the None singleton.

    `avatar_urls: airbyte_agent_sdk.connectors.jira.models.ProjectAvatarurls | Any`
    :   The type of the None singleton.

    `components: list[airbyte_agent_sdk.connectors.jira.models.ProjectComponentsItem] | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `entity_id: str | Any | None`
    :   The type of the None singleton.

    `expand: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_private: bool | Any`
    :   The type of the None singleton.

    `issue_types: list[airbyte_agent_sdk.connectors.jira.models.ProjectIssuetypesItem] | Any | None`
    :   The type of the None singleton.

    `key: str | Any`
    :   The type of the None singleton.

    `lead: airbyte_agent_sdk.connectors.jira.models.ProjectLead | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `project_category: airbyte_agent_sdk.connectors.jira.models.ProjectProjectcategory | Any | None`
    :   The type of the None singleton.

    `project_type_key: str | Any`
    :   The type of the None singleton.

    `properties: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `roles: dict[str, str] | Any | None`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

    `simplified: bool | Any`
    :   The type of the None singleton.

    `style: str | Any`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

    `uuid: str | Any | None`
    :   The type of the None singleton.

    `versions: list[airbyte_agent_sdk.connectors.jira.models.ProjectVersionsItem] | Any | None`
    :   The type of the None singleton.

`ProjectAvatarurls(**data: Any)`
:   URLs for project avatars in different sizes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_16x16: str | Any`
    :   The type of the None singleton.

    `field_24x24: str | Any`
    :   The type of the None singleton.

    `field_32x32: str | Any`
    :   The type of the None singleton.

    `field_48x48: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`ProjectComponentsItem(**data: Any)`
:   Nested schema for Project.components_item
    
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

    `is_assignee_type_valid: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

`ProjectIssuetypesItem(**data: Any)`
:   Nested schema for Project.issueTypes_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_id: int | Any | None`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `hierarchy_level: int | Any | None`
    :   The type of the None singleton.

    `icon_url: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

    `subtask: bool | Any`
    :   The type of the None singleton.

`ProjectLead(**data: Any)`
:   Project lead user (available with expand=lead)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any`
    :   The type of the None singleton.

    `account_type: str | Any`
    :   The type of the None singleton.

    `active: bool | Any`
    :   The type of the None singleton.

    `avatar_urls: airbyte_agent_sdk.connectors.jira.models.ProjectLeadAvatarurls | Any`
    :   URLs for user avatars in different sizes

    `display_name: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

`ProjectLeadAvatarurls(**data: Any)`
:   URLs for user avatars in different sizes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_16x16: str | Any`
    :   The type of the None singleton.

    `field_24x24: str | Any`
    :   The type of the None singleton.

    `field_32x32: str | Any`
    :   The type of the None singleton.

    `field_48x48: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`ProjectProjectcategory(**data: Any)`
:   Project category information
    
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

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

`ProjectVersionsItem(**data: Any)`
:   Nested schema for Project.versions_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | Any`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `overdue: bool | Any | None`
    :   The type of the None singleton.

    `project_id: int | Any`
    :   The type of the None singleton.

    `release_date: str | Any | None`
    :   The type of the None singleton.

    `released: bool | Any`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

    `start_date: str | Any | None`
    :   The type of the None singleton.

    `user_release_date: str | Any | None`
    :   The type of the None singleton.

    `user_start_date: str | Any | None`
    :   The type of the None singleton.

`ProjectsApiSearchResultMeta(**data: Any)`
:   Metadata for projects.Action.API_SEARCH operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `total: int | Any`
    :   The type of the None singleton.

`ProjectsList(**data: Any)`
:   Paginated list of projects from search results
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `is_last: bool | Any`
    :   The type of the None singleton.

    `max_results: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

    `start_at: int | Any`
    :   The type of the None singleton.

    `total: int | Any`
    :   The type of the None singleton.

    `values: list[airbyte_agent_sdk.connectors.jira.models.Project] | Any`
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

    `archived: bool`
    :   Whether the project is archived

    `archived_by: dict[str, typing.Any] | None`
    :   The user who archived the project

    `archived_date: str | None`
    :   The date when the project was archived

    `assignee_type: str | None`
    :   The default assignee when creating issues for this project

    `avatar_urls: dict[str, typing.Any]`
    :   The URLs of the project's avatars

    `components: list[typing.Any]`
    :   List of the components contained in the project

    `deleted: bool`
    :   Whether the project is marked as deleted

    `deleted_by: dict[str, typing.Any] | None`
    :   The user who marked the project as deleted

    `deleted_date: str | None`
    :   The date when the project was marked as deleted

    `description: str | None`
    :   A brief description of the project

    `email: str | None`
    :   An email address associated with the project

    `entity_id: str | None`
    :   The unique identifier of the project entity

    `expand: str | None`
    :   Expand options that include additional project details in the response

    `favourite: bool`
    :   Whether the project is selected as a favorite

    `id: str`
    :   The ID of the project

    `insight: dict[str, typing.Any] | None`
    :   Insights about the project

    `is_private: bool`
    :   Whether the project is private

    `issue_type_hierarchy: dict[str, typing.Any] | None`
    :   The issue type hierarchy for the project

    `issue_types: list[typing.Any]`
    :   List of the issue types available in the project

    `key: str`
    :   The key of the project

    `lead: dict[str, typing.Any] | None`
    :   The username of the project lead

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The name of the project

    `permissions: dict[str, typing.Any] | None`
    :   User permissions on the project

    `project_category: dict[str, typing.Any] | None`
    :   The category the project belongs to

    `project_type_key: str | None`
    :   The project type of the project

    `properties: dict[str, typing.Any]`
    :   Map of project properties

    `retention_till_date: str | None`
    :   The date when the project is deleted permanently

    `roles: dict[str, typing.Any]`
    :   The name and self URL for each role defined in the project

    `self: str`
    :   The URL of the project details

    `simplified: bool`
    :   Whether the project is simplified

    `style: str | None`
    :   The type of the project

    `url: str | None`
    :   A link to information about this project

    `uuid: str | None`
    :   Unique ID for next-gen projects

    `versions: list[typing.Any]`
    :   The versions defined in the project

`User(**data: Any)`
:   Jira user object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any`
    :   The type of the None singleton.

    `account_type: str | Any`
    :   The type of the None singleton.

    `active: bool | Any`
    :   The type of the None singleton.

    `application_roles: airbyte_agent_sdk.connectors.jira.models.UserApplicationroles | Any | None`
    :   The type of the None singleton.

    `avatar_urls: airbyte_agent_sdk.connectors.jira.models.UserAvatarurls | Any`
    :   The type of the None singleton.

    `display_name: str | Any`
    :   The type of the None singleton.

    `email_address: str | Any | None`
    :   The type of the None singleton.

    `expand: str | Any | None`
    :   The type of the None singleton.

    `groups: airbyte_agent_sdk.connectors.jira.models.UserGroups | Any | None`
    :   The type of the None singleton.

    `locale: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

    `time_zone: str | Any | None`
    :   The type of the None singleton.

`UserApplicationroles(**data: Any)`
:   User application roles (available with expand=applicationRoles)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `items: list[airbyte_agent_sdk.connectors.jira.models.UserApplicationrolesItemsItem] | Any`
    :   Array of application role objects

    `model_config`
    :   The type of the None singleton.

    `size: int | Any`
    :   Number of application roles

`UserApplicationrolesItemsItem(**data: Any)`
:   Nested schema for UserApplicationroles.items_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `default_groups: list[str] | Any`
    :   The type of the None singleton.

    `default_groups_details: list[airbyte_agent_sdk.connectors.jira.models.UserApplicationrolesItemsItemDefaultgroupsdetailsItem] | Any`
    :   The type of the None singleton.

    `defined: bool | Any`
    :   The type of the None singleton.

    `group_details: list[airbyte_agent_sdk.connectors.jira.models.UserApplicationrolesItemsItemGroupdetailsItem] | Any`
    :   The type of the None singleton.

    `groups: list[str] | Any`
    :   The type of the None singleton.

    `has_unlimited_seats: bool | Any`
    :   The type of the None singleton.

    `key: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `number_of_seats: int | Any`
    :   The type of the None singleton.

    `platform: bool | Any`
    :   The type of the None singleton.

    `remaining_seats: int | Any`
    :   The type of the None singleton.

    `selected_by_default: bool | Any`
    :   The type of the None singleton.

    `user_count: int | Any`
    :   The type of the None singleton.

    `user_count_description: str | Any`
    :   The type of the None singleton.

`UserApplicationrolesItemsItemDefaultgroupsdetailsItem(**data: Any)`
:   Nested schema for UserApplicationrolesItemsItem.defaultGroupsDetails_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `group_id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

`UserApplicationrolesItemsItemGroupdetailsItem(**data: Any)`
:   Nested schema for UserApplicationrolesItemsItem.groupDetails_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `group_id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

`UserAvatarurls(**data: Any)`
:   URLs for user avatars in different sizes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_16x16: str | Any`
    :   The type of the None singleton.

    `field_24x24: str | Any`
    :   The type of the None singleton.

    `field_32x32: str | Any`
    :   The type of the None singleton.

    `field_48x48: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`UserGroups(**data: Any)`
:   User groups (available with expand=groups)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `items: list[airbyte_agent_sdk.connectors.jira.models.UserGroupsItemsItem] | Any`
    :   Array of group objects

    `model_config`
    :   The type of the None singleton.

    `size: int | Any`
    :   Number of groups

`UserGroupsItemsItem(**data: Any)`
:   Nested schema for UserGroups.items_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `group_id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `self: str | Any`
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

    `account_id: str`
    :   The account ID of the user, uniquely identifying the user across all Atlassian products

    `account_type: str | None`
    :   The user account type (atlassian, app, or customer)

    `active: bool`
    :   Indicates whether the user is active

    `application_roles: dict[str, typing.Any] | None`
    :   The application roles assigned to the user

    `avatar_urls: dict[str, typing.Any]`
    :   The avatars of the user

    `display_name: str | None`
    :   The display name of the user

    `email_address: str | None`
    :   The email address of the user

    `expand: str | None`
    :   Options to include additional user details in the response

    `groups: dict[str, typing.Any] | None`
    :   The groups to which the user belongs

    `key: str | None`
    :   Deprecated property

    `locale: str | None`
    :   The locale of the user

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Deprecated property

    `self: str`
    :   The URL of the user

    `time_zone: str | None`
    :   The time zone specified in the user's profile

`Worklog(**data: Any)`
:   Jira worklog object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author: airbyte_agent_sdk.connectors.jira.models.WorklogAuthor | Any`
    :   The type of the None singleton.

    `comment: airbyte_agent_sdk.connectors.jira.models.WorklogComment | Any`
    :   The type of the None singleton.

    `created: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `issue_id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `properties: list[dict[str, typing.Any]] | Any | None`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

    `started: str | Any`
    :   The type of the None singleton.

    `time_spent: str | Any`
    :   The type of the None singleton.

    `time_spent_seconds: int | Any`
    :   The type of the None singleton.

    `update_author: airbyte_agent_sdk.connectors.jira.models.WorklogUpdateauthor | Any`
    :   The type of the None singleton.

    `updated: str | Any`
    :   The type of the None singleton.

    `visibility: airbyte_agent_sdk.connectors.jira.models.WorklogVisibility | Any | None`
    :   The type of the None singleton.

`WorklogAuthor(**data: Any)`
:   Worklog author user information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any`
    :   The type of the None singleton.

    `account_type: str | Any`
    :   The type of the None singleton.

    `active: bool | Any`
    :   The type of the None singleton.

    `avatar_urls: airbyte_agent_sdk.connectors.jira.models.WorklogAuthorAvatarurls | Any`
    :   URLs for user avatars in different sizes

    `display_name: str | Any`
    :   The type of the None singleton.

    `email_address: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

    `time_zone: str | Any`
    :   The type of the None singleton.

`WorklogAuthorAvatarurls(**data: Any)`
:   URLs for user avatars in different sizes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_16x16: str | Any`
    :   The type of the None singleton.

    `field_24x24: str | Any`
    :   The type of the None singleton.

    `field_32x32: str | Any`
    :   The type of the None singleton.

    `field_48x48: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`WorklogComment(**data: Any)`
:   Comment associated with the worklog (ADF format)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.models.WorklogCommentContentItem] | Any`
    :   Array of content blocks

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Document type (always 'doc')

    `version: int | Any`
    :   ADF version

`WorklogCommentContentItem(**data: Any)`
:   Nested schema for WorklogComment.content_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content: list[airbyte_agent_sdk.connectors.jira.models.WorklogCommentContentItemContentItem] | Any`
    :   Nested content items

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   Block type (e.g., 'paragraph')

`WorklogCommentContentItemContentItem(**data: Any)`
:   Nested schema for WorklogCommentContentItem.content_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `text: str | Any`
    :   Text content

    `type_: str | Any`
    :   Content type (e.g., 'text')

`WorklogUpdateauthor(**data: Any)`
:   User who last updated the worklog
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | Any`
    :   The type of the None singleton.

    `account_type: str | Any`
    :   The type of the None singleton.

    `active: bool | Any`
    :   The type of the None singleton.

    `avatar_urls: airbyte_agent_sdk.connectors.jira.models.WorklogUpdateauthorAvatarurls | Any`
    :   URLs for user avatars in different sizes

    `display_name: str | Any`
    :   The type of the None singleton.

    `email_address: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

    `time_zone: str | Any`
    :   The type of the None singleton.

`WorklogUpdateauthorAvatarurls(**data: Any)`
:   URLs for user avatars in different sizes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `field_16x16: str | Any`
    :   The type of the None singleton.

    `field_24x24: str | Any`
    :   The type of the None singleton.

    `field_32x32: str | Any`
    :   The type of the None singleton.

    `field_48x48: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

`WorklogVisibility(**data: Any)`
:   Visibility restrictions for the worklog
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `identifier: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `value: str | Any`
    :   The type of the None singleton.

`WorklogsList(**data: Any)`
:   Paginated list of issue worklogs
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `max_results: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `start_at: int | Any`
    :   The type of the None singleton.

    `total: int | Any`
    :   The type of the None singleton.

    `worklogs: list[airbyte_agent_sdk.connectors.jira.models.Worklog] | Any`
    :   The type of the None singleton.