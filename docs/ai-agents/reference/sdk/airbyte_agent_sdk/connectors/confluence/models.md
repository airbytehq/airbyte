---
id: airbyte_agent_sdk-connectors-confluence-models
title: airbyte_agent_sdk.connectors.confluence.models
---

Module airbyte_agent_sdk.connectors.confluence.models
=====================================================
Pydantic models for confluence connector.

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

    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult[AuditSearchData]
    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult[BlogPostsSearchData]
    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult[GroupsSearchData]
    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult[PagesSearchData]
    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult[SpacesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[AuditSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AuditSearchResult"></a>

`AuditSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[BlogPostsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BlogPostsSearchResult"></a>

`BlogPostsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[GroupsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[PagesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PagesSearchResult"></a>

`PagesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SpacesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.confluence.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AuditListResultMeta"></a>

`AuditListResultMeta(**data: Any)`
:   Metadata for audit.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `limit: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next: str | Any`
    :   The type of the None singleton.

    `size: int | Any`
    :   The type of the None singleton.

    `start: int | Any`
    :   The type of the None singleton.

<a id="AuditRecord"></a>

`AuditRecord(**data: Any)`
:   Confluence audit record
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `affected_object: airbyte_agent_sdk.connectors.confluence.models.AuditRecordAffectedobject | Any`
    :   The type of the None singleton.

    `associated_objects: list[airbyte_agent_sdk.connectors.confluence.models.AuditRecordAssociatedobjectsItem] | Any`
    :   The type of the None singleton.

    `author: airbyte_agent_sdk.connectors.confluence.models.AuditRecordAuthor | Any`
    :   The type of the None singleton.

    `category: str | Any`
    :   The type of the None singleton.

    `changed_values: list[typing.Any] | Any`
    :   The type of the None singleton.

    `creation_date: int | Any`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `remote_address: str | Any`
    :   The type of the None singleton.

    `summary: str | Any`
    :   The type of the None singleton.

    `super_admin: bool | Any`
    :   The type of the None singleton.

    `sys_admin: bool | Any`
    :   The type of the None singleton.

<a id="AuditRecordAffectedobject"></a>

`AuditRecordAffectedobject(**data: Any)`
:   Object affected by the audit event
    
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
    :   Name of the affected object

    `object_type: str | Any`
    :   Type of the affected object

<a id="AuditRecordAssociatedobjectsItem"></a>

`AuditRecordAssociatedobjectsItem(**data: Any)`
:   Nested schema for AuditRecord.associatedObjects_item
    
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
    :   Name of the associated object

    `object_type: str | Any`
    :   Type of the associated object

<a id="AuditRecordAuthor"></a>

`AuditRecordAuthor(**data: Any)`
:   User who triggered the audit event
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_type: str | Any`
    :   Account type

    `display_name: str | Any`
    :   Display name of the author

    `external_collaborator: bool | Any`
    :   Whether the author is an external collaborator

    `is_external_collaborator: bool | Any`
    :   Whether the author is an external collaborator

    `model_config`
    :   The type of the None singleton.

    `operations: Any`
    :   Operations available for the author

    `public_name: str | Any`
    :   Public name of the author

    `type_: str | Any`
    :   Author type

<a id="AuditRecordsList"></a>

`AuditRecordsList(**data: Any)`
:   Paginated list of audit records
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `limit: int | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.confluence.models.AuditRecordsListLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.confluence.models.AuditRecord] | Any`
    :   The type of the None singleton.

    `size: int | Any`
    :   The type of the None singleton.

    `start: int | Any`
    :   The type of the None singleton.

<a id="AuditRecordsListLinks"></a>

`AuditRecordsListLinks(**data: Any)`
:   Nested schema for AuditRecordsList._links
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `base: str | Any`
    :   The type of the None singleton.

    `context: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next: str | Any`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

<a id="AuditSearchData"></a>

`AuditSearchData(**data: Any)`
:   Search result data for audit entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `affected_object: dict[str, typing.Any] | None`
    :   The object that was affected by the audit event.

    `associated_objects: list[typing.Any] | None`
    :   Any associated objects related to the audit event.

    `author: dict[str, typing.Any] | None`
    :   The user who triggered the audit event.

    `category: str | None`
    :   The category under which the audit event falls.

    `changed_values: list[typing.Any] | None`
    :   Details of the values that were changed during the audit event.

    `creation_date: int | None`
    :   The date and time when the audit event was created.

    `description: str | None`
    :   A detailed description of the audit event.

    `model_config`
    :   The type of the None singleton.

    `remote_address: str | None`
    :   The IP address from which the audit event originated.

    `summary: str | None`
    :   A brief summary or title describing the audit event.

    `super_admin: bool | None`
    :   Indicates if the user triggering the audit event is a super admin.

    `sys_admin: bool | None`
    :   Indicates if the user triggering the audit event is a system admin.

<a id="BlogPost"></a>

`BlogPost(**data: Any)`
:   Confluence blog post object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_id: str | Any`
    :   The type of the None singleton.

    `body: airbyte_agent_sdk.connectors.confluence.models.BlogPostBody | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.confluence.models.BlogPostLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `space_id: str | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `version: airbyte_agent_sdk.connectors.confluence.models.BlogPostVersion | Any`
    :   The type of the None singleton.

<a id="BlogPostBody"></a>

`BlogPostBody(**data: Any)`
:   Blog post body content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `atlas_doc_format: dict[str, typing.Any] | Any`
    :   Atlas doc format body

    `model_config`
    :   The type of the None singleton.

    `storage: dict[str, typing.Any] | Any`
    :   Storage format body

<a id="BlogPostLinks"></a>

`BlogPostLinks(**data: Any)`
:   Links related to the blog post
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `base: str | Any`
    :   Base URL

    `editui: str | Any`
    :   Edit UI link

    `edituiv2: str | Any`
    :   Edit UI v2 link

    `model_config`
    :   The type of the None singleton.

    `tinyui: str | Any`
    :   Tiny UI link

    `webui: str | Any`
    :   Web UI link

<a id="BlogPostVersion"></a>

`BlogPostVersion(**data: Any)`
:   Version information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_id: str | Any`
    :   ID of the version author

    `created_at: str | Any`
    :   Version creation timestamp

    `message: str | Any`
    :   Version message

    `minor_edit: bool | Any`
    :   Whether this was a minor edit

    `model_config`
    :   The type of the None singleton.

    `ncs_step_version: Any`
    :   NCS step version

    `number: int | Any`
    :   Version number

<a id="BlogPostsList"></a>

`BlogPostsList(**data: Any)`
:   Paginated list of blog posts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: airbyte_agent_sdk.connectors.confluence.models.BlogPostsListLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.confluence.models.BlogPost] | Any`
    :   The type of the None singleton.

<a id="BlogPostsListLinks"></a>

`BlogPostsListLinks(**data: Any)`
:   Nested schema for BlogPostsList._links
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `base: str | Any`
    :   Base URL

    `model_config`
    :   The type of the None singleton.

    `next: str | Any`
    :   URL for the next page of results

<a id="BlogPostsListResultMeta"></a>

`BlogPostsListResultMeta(**data: Any)`
:   Metadata for blog_posts.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any`
    :   The type of the None singleton.

<a id="BlogPostsSearchData"></a>

`BlogPostsSearchData(**data: Any)`
:   Search result data for blog_posts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_id: str | None`
    :   ID of the user who created the blog post

    `body: dict[str, typing.Any] | None`
    :   Blog post body content

    `created_at: str | None`
    :   Timestamp when the blog post was created

    `id: str | None`
    :   Unique blog post identifier

    `links: dict[str, typing.Any] | None`
    :   Links related to the blog post

    `model_config`
    :   The type of the None singleton.

    `space_id: str | None`
    :   ID of the space containing this blog post

    `status: str | None`
    :   Blog post status (current, draft, trashed)

    `title: str | None`
    :   Blog post title

    `version: dict[str, typing.Any] | None`
    :   Version information

<a id="ConfluenceAuthConfig"></a>

`ConfluenceAuthConfig(**data: Any)`
:   Confluence API Token Authentication - Authenticate using your Atlassian account email and API token
    
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
    :   Your Confluence API token from https://id.atlassian.com/manage-profile/security/api-tokens

    `username: str`
    :   Your Atlassian account email address

<a id="ConfluenceCheckResult"></a>

`ConfluenceCheckResult(**data: Any)`
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

<a id="ConfluenceExecuteResult"></a>

`ConfluenceExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="ConfluenceExecuteResultWithMeta"></a>

`ConfluenceExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta[list[AuditRecord], AuditListResultMeta]
    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta[list[BlogPost], BlogPostsListResultMeta]
    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta[list[Group], GroupsListResultMeta]
    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta[list[Page], PagesListResultMeta]
    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta[list[Space], SpacesListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`ConfluenceExecuteResultWithMeta[list[AuditRecord], AuditListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AuditListResult"></a>

`AuditListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ConfluenceExecuteResultWithMeta[list[BlogPost], BlogPostsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BlogPostsListResult"></a>

`BlogPostsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ConfluenceExecuteResultWithMeta[list[Group], GroupsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResult
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

    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ConfluenceExecuteResultWithMeta[list[Page], PagesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="PagesListResult"></a>

`PagesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ConfluenceExecuteResultWithMeta[list[Space], SpacesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SpacesListResult"></a>

`SpacesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.confluence.models.ConfluenceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Group"></a>

`Group(**data: Any)`
:   Confluence group object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.confluence.models.GroupLinks | Any`
    :   The type of the None singleton.

    `managed_by: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `resource_ari: str | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `usage_type: str | Any`
    :   The type of the None singleton.

<a id="GroupLinks"></a>

`GroupLinks(**data: Any)`
:   Links related to the group
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | Any`
    :   Self link

<a id="GroupsList"></a>

`GroupsList(**data: Any)`
:   Paginated list of groups
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `limit: int | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.confluence.models.GroupsListLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.confluence.models.Group] | Any`
    :   The type of the None singleton.

    `size: int | Any`
    :   The type of the None singleton.

    `start: int | Any`
    :   The type of the None singleton.

<a id="GroupsListLinks"></a>

`GroupsListLinks(**data: Any)`
:   Nested schema for GroupsList._links
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `base: str | Any`
    :   The type of the None singleton.

    `context: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next: str | Any`
    :   The type of the None singleton.

    `self: str | Any`
    :   The type of the None singleton.

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

    `limit: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next: str | Any`
    :   The type of the None singleton.

    `size: int | Any`
    :   The type of the None singleton.

    `start: int | Any`
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

    `id: str | None`
    :   The unique identifier of the group

    `links: dict[str, typing.Any] | None`
    :   Links related to the group

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the group

    `type_: str | None`
    :   The type of group

<a id="Page"></a>

`Page(**data: Any)`
:   Confluence page object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_id: str | Any`
    :   The type of the None singleton.

    `body: airbyte_agent_sdk.connectors.confluence.models.PageBody | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `last_owner_id: Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.confluence.models.PageLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `owner_id: str | Any`
    :   The type of the None singleton.

    `parent_id: Any`
    :   The type of the None singleton.

    `parent_type: Any`
    :   The type of the None singleton.

    `position: int | Any`
    :   The type of the None singleton.

    `space_id: str | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `version: airbyte_agent_sdk.connectors.confluence.models.PageVersion | Any`
    :   The type of the None singleton.

<a id="PageBody"></a>

`PageBody(**data: Any)`
:   Page body content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `atlas_doc_format: dict[str, typing.Any] | Any`
    :   Atlas doc format body

    `model_config`
    :   The type of the None singleton.

    `storage: dict[str, typing.Any] | Any`
    :   Storage format body

<a id="PageLinks"></a>

`PageLinks(**data: Any)`
:   Links related to the page
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `base: str | Any`
    :   Base URL

    `editui: str | Any`
    :   Edit UI link

    `edituiv2: str | Any`
    :   Edit UI v2 link

    `model_config`
    :   The type of the None singleton.

    `tinyui: str | Any`
    :   Tiny UI link

    `webui: str | Any`
    :   Web UI link

<a id="PageVersion"></a>

`PageVersion(**data: Any)`
:   Version information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_id: str | Any`
    :   ID of the version author

    `created_at: str | Any`
    :   Version creation timestamp

    `message: str | Any`
    :   Version message

    `minor_edit: bool | Any`
    :   Whether this was a minor edit

    `model_config`
    :   The type of the None singleton.

    `ncs_step_version: Any`
    :   NCS step version

    `number: int | Any`
    :   Version number

<a id="PagesList"></a>

`PagesList(**data: Any)`
:   Paginated list of pages
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: airbyte_agent_sdk.connectors.confluence.models.PagesListLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.confluence.models.Page] | Any`
    :   The type of the None singleton.

<a id="PagesListLinks"></a>

`PagesListLinks(**data: Any)`
:   Nested schema for PagesList._links
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `base: str | Any`
    :   Base URL

    `model_config`
    :   The type of the None singleton.

    `next: str | Any`
    :   URL for the next page of results

<a id="PagesListResultMeta"></a>

`PagesListResultMeta(**data: Any)`
:   Metadata for pages.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any`
    :   The type of the None singleton.

<a id="PagesSearchData"></a>

`PagesSearchData(**data: Any)`
:   Search result data for pages entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_id: str | None`
    :   ID of the user who created the page

    `body: dict[str, typing.Any] | None`
    :   Page body content

    `created_at: str | None`
    :   Timestamp when the page was created

    `id: str | None`
    :   Unique page identifier

    `last_owner_id: str | None`
    :   ID of the previous page owner

    `links: dict[str, typing.Any] | None`
    :   Links related to the page

    `model_config`
    :   The type of the None singleton.

    `owner_id: str | None`
    :   ID of the current page owner

    `parent_id: str | None`
    :   ID of the parent page

    `parent_type: str | None`
    :   Type of the parent (page or space)

    `position: int | None`
    :   Position of the page among siblings

    `space_id: str | None`
    :   ID of the space containing this page

    `status: str | None`
    :   Page status (current, archived, trashed, draft)

    `title: str | None`
    :   Page title

    `version: dict[str, typing.Any] | None`
    :   Version information

<a id="Space"></a>

`Space(**data: Any)`
:   Confluence space object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_id: str | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `current_active_alias: str | Any`
    :   The type of the None singleton.

    `description: Any`
    :   The type of the None singleton.

    `homepage_id: str | Any`
    :   The type of the None singleton.

    `icon: Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `key: str | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.confluence.models.SpaceLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `space_owner_id: str | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

<a id="SpaceLinks"></a>

`SpaceLinks(**data: Any)`
:   Links related to the space
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `base: str | Any`
    :   Base URL

    `model_config`
    :   The type of the None singleton.

    `webui: str | Any`
    :   Web UI link

<a id="SpacesList"></a>

`SpacesList(**data: Any)`
:   Paginated list of spaces
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: airbyte_agent_sdk.connectors.confluence.models.SpacesListLinks | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.confluence.models.Space] | Any`
    :   The type of the None singleton.

<a id="SpacesListLinks"></a>

`SpacesListLinks(**data: Any)`
:   Nested schema for SpacesList._links
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `base: str | Any`
    :   Base URL

    `model_config`
    :   The type of the None singleton.

    `next: str | Any`
    :   URL for the next page of results

<a id="SpacesListResultMeta"></a>

`SpacesListResultMeta(**data: Any)`
:   Metadata for spaces.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any`
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

    `author_id: str | None`
    :   ID of the user who created the space

    `created_at: str | None`
    :   Timestamp when the space was created

    `description: dict[str, typing.Any] | None`
    :   Space description in various formats

    `homepage_id: str | None`
    :   ID of the space homepage

    `icon: dict[str, typing.Any] | None`
    :   Space icon information

    `id: str | None`
    :   Unique space identifier

    `key: str | None`
    :   Space key

    `links: dict[str, typing.Any] | None`
    :   Links related to the space

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Space name

    `status: str | None`
    :   Space status (current or archived)

    `type_: str | None`
    :   Space type (global or personal)