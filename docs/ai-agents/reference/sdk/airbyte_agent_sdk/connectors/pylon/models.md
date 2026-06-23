---
id: airbyte_agent_sdk-connectors-pylon-models
title: airbyte_agent_sdk.connectors.pylon.models
---

Module airbyte_agent_sdk.connectors.pylon.models
================================================
Pydantic models for pylon connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="Account"></a>

`Account(**data: Any)`
:   Account type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channels: list[airbyte_agent_sdk.connectors.pylon.models.AccountChannel] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `custom_fields: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `domain: str | None`
    :   The type of the None singleton.

    `domains: list[str] | None`
    :   The type of the None singleton.

    `external_ids: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `is_disabled: bool | None`
    :   The type of the None singleton.

    `latest_customer_activity_time: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `owner: typing.Any | None`
    :   The type of the None singleton.

    `primary_domain: str | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="AccountChannel"></a>

`AccountChannel(**data: Any)`
:   AccountChannel type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel_id: str | None`
    :   The type of the None singleton.

    `is_primary: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `source: str | None`
    :   The type of the None singleton.

<a id="AccountCreateParams"></a>

`AccountCreateParams(**data: Any)`
:   AccountCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `domains: list[str] | None`
    :   The type of the None singleton.

    `logo_url: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `owner_id: str | None`
    :   The type of the None singleton.

    `primary_domain: str | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

<a id="AccountResponse"></a>

`AccountResponse(**data: Any)`
:   AccountResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.pylon.models.Account | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="AccountUpdateParams"></a>

`AccountUpdateParams(**data: Any)`
:   AccountUpdateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `domains: list[str] | None`
    :   The type of the None singleton.

    `is_disabled: bool | None`
    :   The type of the None singleton.

    `logo_url: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `owner_id: str | None`
    :   The type of the None singleton.

    `primary_domain: str | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

<a id="AccountsListResultMeta"></a>

`AccountsListResultMeta(**data: Any)`
:   Metadata for accounts.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

<a id="AccountsResponse"></a>

`AccountsResponse(**data: Any)`
:   AccountsResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.pylon.models.Account] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="AccountsSearchData"></a>

`AccountsSearchData(**data: Any)`
:   Search result data for accounts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the account was created, in ISO 8601 format

    `domain: str | None`
    :   Primary domain associated with the account

    `id: str`
    :   Unique identifier for the account

    `is_disabled: bool | None`
    :   Whether the account has been disabled

    `latest_customer_activity_time: str | None`
    :   Timestamp of the most recent activity from this account, in ISO 8601 format

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the account (customer organization)

    `primary_domain: str | None`
    :   Canonical primary domain for the account

    `type_: str | None`
    :   Classification of the account (e.g. customer, prospect)

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

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[AccountsSearchData]
    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[ContactsSearchData]
    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[CustomFieldsSearchData]
    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[IssuesSearchData]
    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[TagsSearchData]
    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[TeamsSearchData]
    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[TicketFormsSearchData]
    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[UserRolesSearchData]
    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[AccountsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AccountsSearchResult"></a>

`AccountsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ContactsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ContactsSearchResult"></a>

`ContactsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CustomFieldsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CustomFieldsSearchResult"></a>

`CustomFieldsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[IssuesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TagsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TeamsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TicketFormsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TicketFormsSearchResult"></a>

`TicketFormsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UserRolesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UserRolesSearchResult"></a>

`UserRolesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.pylon.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Article"></a>

`Article(**data: Any)`
:   Article type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_user_id: str | None`
    :   The type of the None singleton.

    `body_html: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `is_published: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `slug: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="ArticleCreateParams"></a>

`ArticleCreateParams(**data: Any)`
:   ArticleCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_user_id: str`
    :   The type of the None singleton.

    `body_html: str`
    :   The type of the None singleton.

    `is_published: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `slug: str | None`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="ArticleResponse"></a>

`ArticleResponse(**data: Any)`
:   ArticleResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.pylon.models.Article | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="ArticleUpdateParams"></a>

`ArticleUpdateParams(**data: Any)`
:   ArticleUpdateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body_html: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="CSATResponse"></a>

`CSATResponse(**data: Any)`
:   CSATResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `comment: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `score: int | None`
    :   The type of the None singleton.

<a id="Collection"></a>

`Collection(**data: Any)`
:   Collection type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `slug: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

<a id="CollectionCreateParams"></a>

`CollectionCreateParams(**data: Any)`
:   CollectionCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `slug: str | None`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="CollectionResponse"></a>

`CollectionResponse(**data: Any)`
:   CollectionResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.pylon.models.Collection | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="Contact"></a>

`Contact(**data: Any)`
:   Contact type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: typing.Any | None`
    :   The type of the None singleton.

    `avatar_url: str | None`
    :   The type of the None singleton.

    `custom_fields: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `emails: list[str] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `integration_user_ids: list[airbyte_agent_sdk.connectors.pylon.models.IntegrationUserId] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `phone_numbers: list[str] | None`
    :   The type of the None singleton.

    `portal_role: str | None`
    :   The type of the None singleton.

    `portal_role_id: str | None`
    :   The type of the None singleton.

<a id="ContactCreateParams"></a>

`ContactCreateParams(**data: Any)`
:   ContactCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   The type of the None singleton.

    `avatar_url: str | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="ContactResponse"></a>

`ContactResponse(**data: Any)`
:   ContactResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.pylon.models.Contact | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="ContactUpdateParams"></a>

`ContactUpdateParams(**data: Any)`
:   ContactUpdateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

<a id="ContactsListResultMeta"></a>

`ContactsListResultMeta(**data: Any)`
:   Metadata for contacts.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

<a id="ContactsResponse"></a>

`ContactsResponse(**data: Any)`
:   ContactsResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.pylon.models.Contact] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="ContactsSearchData"></a>

`ContactsSearchData(**data: Any)`
:   Search result data for contacts entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | None`
    :   Primary email address of the contact

    `id: str`
    :   Unique identifier for the contact

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Full name of the contact

    `portal_role: str | None`
    :   Role the contact has in the customer portal

    `primary_phone_number: str | None`
    :   Primary phone number of the contact

<a id="CustomField"></a>

`CustomField(**data: Any)`
:   CustomField type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `default_value: str | None`
    :   The type of the None singleton.

    `default_values: list[str] | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `is_read_only: bool | None`
    :   The type of the None singleton.

    `label: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `number_metadata: typing.Any | None`
    :   The type of the None singleton.

    `object_type: str | None`
    :   The type of the None singleton.

    `select_metadata: typing.Any | None`
    :   The type of the None singleton.

    `slug: str | None`
    :   The type of the None singleton.

    `source: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="CustomFieldResponse"></a>

`CustomFieldResponse(**data: Any)`
:   CustomFieldResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.pylon.models.CustomField | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="CustomFieldValue"></a>

`CustomFieldValue(**data: Any)`
:   CustomFieldValue type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `slug: str | None`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

    `values: list[str] | None`
    :   The type of the None singleton.

<a id="CustomFieldsListResultMeta"></a>

`CustomFieldsListResultMeta(**data: Any)`
:   Metadata for custom_fields.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

<a id="CustomFieldsResponse"></a>

`CustomFieldsResponse(**data: Any)`
:   CustomFieldsResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.pylon.models.CustomField] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="CustomFieldsSearchData"></a>

`CustomFieldsSearchData(**data: Any)`
:   Search result data for custom_fields entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   Timestamp when the custom field was created, in ISO 8601 format

    `id: str`
    :   Unique identifier for the custom field

    `is_read_only: bool | None`
    :   Whether the custom field is read-only

    `label: str | None`
    :   Display label of the custom field

    `model_config`
    :   The type of the None singleton.

    `object_type: str | None`
    :   Type of object this custom field applies to (e.g. issue, account)

    `slug: str | None`
    :   URL-safe identifier for the custom field

    `type_: str | None`
    :   Data type of the custom field (e.g. text, select)

<a id="DeleteIssueResponse"></a>

`DeleteIssueResponse(**data: Any)`
:   DeleteIssueResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="EmailMessageInfo"></a>

`EmailMessageInfo(**data: Any)`
:   EmailMessageInfo type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bcc_emails: list[str] | None`
    :   The type of the None singleton.

    `cc_emails: list[str] | None`
    :   The type of the None singleton.

    `from_email: str | None`
    :   The type of the None singleton.

    `message_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `to_emails: list[str] | None`
    :   The type of the None singleton.

<a id="ExternalIssue"></a>

`ExternalIssue(**data: Any)`
:   ExternalIssue type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `external_id: str | None`
    :   The type of the None singleton.

    `link: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `source: str | None`
    :   The type of the None singleton.

<a id="IntegrationUserId"></a>

`IntegrationUserId(**data: Any)`
:   IntegrationUserId type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `source: str | None`
    :   The type of the None singleton.

<a id="Issue"></a>

`Issue(**data: Any)`
:   Issue type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account: typing.Any | None`
    :   The type of the None singleton.

    `assignee: typing.Any | None`
    :   The type of the None singleton.

    `attachment_urls: list[str] | None`
    :   The type of the None singleton.

    `author_unverified: bool | None`
    :   The type of the None singleton.

    `body_html: str | None`
    :   The type of the None singleton.

    `business_hours_first_response_seconds: int | None`
    :   The type of the None singleton.

    `business_hours_resolution_seconds: int | None`
    :   The type of the None singleton.

    `business_hours_time_in_status_seconds: dict[str, int] | None`
    :   The type of the None singleton.

    `chat_widget_info: typing.Any | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `csat_responses: list[airbyte_agent_sdk.connectors.pylon.models.CSATResponse] | None`
    :   The type of the None singleton.

    `custom_fields: dict[str, airbyte_agent_sdk.connectors.pylon.models.CustomFieldValue] | None`
    :   The type of the None singleton.

    `customer_portal_visible: bool | None`
    :   The type of the None singleton.

    `external_issues: list[airbyte_agent_sdk.connectors.pylon.models.ExternalIssue] | None`
    :   The type of the None singleton.

    `first_response_seconds: int | None`
    :   The type of the None singleton.

    `first_response_time: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `latest_message_time: str | None`
    :   The type of the None singleton.

    `link: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `number: int | None`
    :   The type of the None singleton.

    `number_of_touches: int | None`
    :   The type of the None singleton.

    `requester: typing.Any | None`
    :   The type of the None singleton.

    `resolution_seconds: int | None`
    :   The type of the None singleton.

    `resolution_time: str | None`
    :   The type of the None singleton.

    `slack: typing.Any | None`
    :   The type of the None singleton.

    `snoozed_until_time: str | None`
    :   The type of the None singleton.

    `source: typing.Any | None`
    :   The type of the None singleton.

    `state: str | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

    `team: typing.Any | None`
    :   The type of the None singleton.

    `time_in_status_seconds: dict[str, int] | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `type_: typing.Any | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="IssueAssignParams"></a>

`IssueAssignParams(**data: Any)`
:   IssueAssignParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `team_id: str | None`
    :   The type of the None singleton.

<a id="IssueChatWidgetInfo"></a>

`IssueChatWidgetInfo(**data: Any)`
:   IssueChatWidgetInfo type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page_url: str | None`
    :   The type of the None singleton.

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

    `account_id: str | None`
    :   The type of the None singleton.

    `assignee_id: str | None`
    :   The type of the None singleton.

    `body_html: str`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `priority: str | None`
    :   The type of the None singleton.

    `requester_email: str | None`
    :   The type of the None singleton.

    `requester_name: str | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

    `team_id: str | None`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="IssueNote"></a>

`IssueNote(**data: Any)`
:   IssueNote type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body_html: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `timestamp: str | None`
    :   The type of the None singleton.

<a id="IssueNoteCreateParams"></a>

`IssueNoteCreateParams(**data: Any)`
:   IssueNoteCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `body_html: str`
    :   The type of the None singleton.

    `message_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `thread_id: str | None`
    :   The type of the None singleton.

<a id="IssueNoteResponse"></a>

`IssueNoteResponse(**data: Any)`
:   IssueNoteResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.pylon.models.IssueNote | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="IssueReplyCreateParams"></a>

`IssueReplyCreateParams(**data: Any)`
:   IssueReplyCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attachment_urls: list[str] | None`
    :   The type of the None singleton.

    `body_html: str`
    :   The type of the None singleton.

    `contact_id: str | None`
    :   The type of the None singleton.

    `message_id: str`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `user_id: str | None`
    :   The type of the None singleton.

<a id="IssueReplyData"></a>

`IssueReplyData(**data: Any)`
:   IssueReplyData type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The type of the None singleton.

    `issue_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="IssueReplyResponse"></a>

`IssueReplyResponse(**data: Any)`
:   IssueReplyResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.pylon.models.IssueReplyData | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
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

    `data: airbyte_agent_sdk.connectors.pylon.models.Issue | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="IssueStatusUpdateParams"></a>

`IssueStatusUpdateParams(**data: Any)`
:   IssueStatusUpdateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `state: str`
    :   The type of the None singleton.

<a id="IssueThread"></a>

`IssueThread(**data: Any)`
:   IssueThread type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

<a id="IssueThreadCreateParams"></a>

`IssueThreadCreateParams(**data: Any)`
:   IssueThreadCreateParams type definition
    
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
    :   The type of the None singleton.

<a id="IssueThreadResponse"></a>

`IssueThreadResponse(**data: Any)`
:   IssueThreadResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.pylon.models.IssueThread | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
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

    `account_id: str | None`
    :   The type of the None singleton.

    `assignee_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `state: str | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

    `team_id: str | None`
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

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

<a id="IssuesResponse"></a>

`IssuesResponse(**data: Any)`
:   IssuesResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.pylon.models.Issue] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | None`
    :   The type of the None singleton.

    `request_id: str | None`
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

    `created_at: str | None`
    :   Timestamp when the issue was created, in ISO 8601 format

    `customer_portal_visible: bool | None`
    :   Whether the issue is visible in the customer portal

    `id: str`
    :   Unique identifier for the issue

    `latest_message_time: str | None`
    :   Timestamp of the most recent message on the issue, in ISO 8601 format

    `model_config`
    :   The type of the None singleton.

    `number: int | None`
    :   Human-readable issue number within the workspace

    `resolution_time: str | None`
    :   Timestamp when the issue was resolved, in ISO 8601 format

    `snoozed_until_time: str | None`
    :   Timestamp the issue is snoozed until, in ISO 8601 format

    `source: str | None`
    :   Channel the issue originated from (e.g. email, slack)

    `state: str | None`
    :   Current state of the issue (e.g. new, in_progress, closed)

    `title: str | None`
    :   Title of the issue

    `type_: str | None`
    :   Type classification of the issue

<a id="MeResponse"></a>

`MeResponse(**data: Any)`
:   MeResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.pylon.models.User | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="Message"></a>

`Message(**data: Any)`
:   Message type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author: typing.Any | None`
    :   The type of the None singleton.

    `email_info: typing.Any | None`
    :   The type of the None singleton.

    `file_urls: list[str] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `is_private: bool | None`
    :   The type of the None singleton.

    `message_html: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `source: str | None`
    :   The type of the None singleton.

    `thread_id: str | None`
    :   The type of the None singleton.

    `timestamp: str | None`
    :   The type of the None singleton.

<a id="MessageAuthor"></a>

`MessageAuthor(**data: Any)`
:   MessageAuthor type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar_url: str | None`
    :   The type of the None singleton.

    `contact: typing.Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `user: typing.Any | None`
    :   The type of the None singleton.

<a id="MessagesListResultMeta"></a>

`MessagesListResultMeta(**data: Any)`
:   Metadata for messages.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

<a id="MessagesResponse"></a>

`MessagesResponse(**data: Any)`
:   MessagesResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.pylon.models.Message] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="Milestone"></a>

`Milestone(**data: Any)`
:   Milestone type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   The type of the None singleton.

    `due_date: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `project_id: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="MilestoneCreateParams"></a>

`MilestoneCreateParams(**data: Any)`
:   MilestoneCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `due_date: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `project_id: str`
    :   The type of the None singleton.

<a id="MilestoneResponse"></a>

`MilestoneResponse(**data: Any)`
:   MilestoneResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.pylon.models.Milestone | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="MilestoneUpdateParams"></a>

`MilestoneUpdateParams(**data: Any)`
:   MilestoneUpdateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `due_date: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

<a id="MiniAccount"></a>

`MiniAccount(**data: Any)`
:   MiniAccount type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="MiniContact"></a>

`MiniContact(**data: Any)`
:   MiniContact type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="MiniTeam"></a>

`MiniTeam(**data: Any)`
:   MiniTeam type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="MiniUser"></a>

`MiniUser(**data: Any)`
:   MiniUser type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="NumberMetadata"></a>

`NumberMetadata(**data: Any)`
:   NumberMetadata type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currency: str | None`
    :   The type of the None singleton.

    `decimal_places: int | None`
    :   The type of the None singleton.

    `format: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Pagination"></a>

`Pagination(**data: Any)`
:   Pagination type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cursor: str | None`
    :   The type of the None singleton.

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Project"></a>

`Project(**data: Any)`
:   Project type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `description_html: str | None`
    :   The type of the None singleton.

    `end_date: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `is_archived: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `owner_id: str | None`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="ProjectCreateParams"></a>

`ProjectCreateParams(**data: Any)`
:   ProjectCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str`
    :   The type of the None singleton.

    `description_html: str | None`
    :   The type of the None singleton.

    `end_date: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `start_date: str | None`
    :   The type of the None singleton.

<a id="ProjectResponse"></a>

`ProjectResponse(**data: Any)`
:   ProjectResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.pylon.models.Project | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="ProjectUpdateParams"></a>

`ProjectUpdateParams(**data: Any)`
:   ProjectUpdateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description_html: str | None`
    :   The type of the None singleton.

    `is_archived: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

<a id="PylonAuthConfig"></a>

`PylonAuthConfig(**data: Any)`
:   API Token Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_token: str`
    :   Your Pylon API token. Only admin users can create API tokens.

    `model_config`
    :   The type of the None singleton.

<a id="PylonCheckResult"></a>

`PylonCheckResult(**data: Any)`
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

<a id="PylonExecuteResult"></a>

`PylonExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="PylonExecuteResultWithMeta"></a>

`PylonExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[Account], AccountsListResultMeta]
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[Contact], ContactsListResultMeta]
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[CustomField], CustomFieldsListResultMeta]
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[Issue], IssuesListResultMeta]
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[Message], MessagesListResultMeta]
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[Tag], TagsListResultMeta]
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[Team], TeamsListResultMeta]
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[TicketForm], TicketFormsListResultMeta]
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[UserRole], UserRolesListResultMeta]
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta[list[User], UsersListResultMeta]

    ### Class variables

    `meta: ~S | None`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`PylonExecuteResultWithMeta[list[Account], AccountsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AccountsListResult"></a>

`AccountsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PylonExecuteResultWithMeta[list[Contact], ContactsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ContactsListResult"></a>

`ContactsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PylonExecuteResultWithMeta[list[CustomField], CustomFieldsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CustomFieldsListResult"></a>

`CustomFieldsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PylonExecuteResultWithMeta[list[Issue], IssuesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
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

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PylonExecuteResultWithMeta[list[Message], MessagesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MessagesListResult"></a>

`MessagesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PylonExecuteResultWithMeta[list[Tag], TagsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
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

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PylonExecuteResultWithMeta[list[Team], TeamsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
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

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PylonExecuteResultWithMeta[list[TicketForm], TicketFormsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TicketFormsListResult"></a>

`TicketFormsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PylonExecuteResultWithMeta[list[UserRole], UserRolesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UserRolesListResult"></a>

`UserRolesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`PylonExecuteResultWithMeta[list[User], UsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
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

    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.pylon.models.PylonExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SelectMetadata"></a>

`SelectMetadata(**data: Any)`
:   SelectMetadata type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `options: list[airbyte_agent_sdk.connectors.pylon.models.SelectOption] | None`
    :   The type of the None singleton.

<a id="SelectOption"></a>

`SelectOption(**data: Any)`
:   SelectOption type definition
    
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

    `slug: str | None`
    :   The type of the None singleton.

<a id="SlackInfo"></a>

`SlackInfo(**data: Any)`
:   SlackInfo type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channel_id: str | None`
    :   The type of the None singleton.

    `message_ts: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `workspace_id: str | None`
    :   The type of the None singleton.

<a id="Tag"></a>

`Tag(**data: Any)`
:   Tag type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hex_color: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_type: str | None`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

<a id="TagCreateParams"></a>

`TagCreateParams(**data: Any)`
:   TagCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hex_color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_type: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

<a id="TagResponse"></a>

`TagResponse(**data: Any)`
:   TagResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.pylon.models.Tag | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="TagUpdateParams"></a>

`TagUpdateParams(**data: Any)`
:   TagUpdateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hex_color: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: str | None`
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

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

<a id="TagsResponse"></a>

`TagsResponse(**data: Any)`
:   TagsResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.pylon.models.Tag] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | None`
    :   The type of the None singleton.

    `request_id: str | None`
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

    `id: str`
    :   Unique identifier for the tag

    `model_config`
    :   The type of the None singleton.

    `object_type: str | None`
    :   Type of object this tag applies to (e.g. issue, account)

    `value: str | None`
    :   Display value of the tag

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

    `assignee_id: str | None`
    :   The type of the None singleton.

    `body_html: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `due_date: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `milestone_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `project_id: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="TaskCreateParams"></a>

`TaskCreateParams(**data: Any)`
:   TaskCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee_id: str | None`
    :   The type of the None singleton.

    `body_html: str | None`
    :   The type of the None singleton.

    `due_date: str | None`
    :   The type of the None singleton.

    `milestone_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `project_id: str | None`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `title: str`
    :   The type of the None singleton.

<a id="TaskResponse"></a>

`TaskResponse(**data: Any)`
:   TaskResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.pylon.models.Task | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="TaskUpdateParams"></a>

`TaskUpdateParams(**data: Any)`
:   TaskUpdateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee_id: str | None`
    :   The type of the None singleton.

    `body_html: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `title: str | None`
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

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `users: list[airbyte_agent_sdk.connectors.pylon.models.MiniUser] | None`
    :   The type of the None singleton.

<a id="TeamCreateParams"></a>

`TeamCreateParams(**data: Any)`
:   TeamCreateParams type definition
    
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
    :   The type of the None singleton.

<a id="TeamResponse"></a>

`TeamResponse(**data: Any)`
:   TeamResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.pylon.models.Team | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="TeamUpdateParams"></a>

`TeamUpdateParams(**data: Any)`
:   TeamUpdateParams type definition
    
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

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

<a id="TeamsResponse"></a>

`TeamsResponse(**data: Any)`
:   TeamsResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.pylon.models.Team] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | None`
    :   The type of the None singleton.

    `request_id: str | None`
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

    `id: str`
    :   Unique identifier for the team

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the team

<a id="TicketForm"></a>

`TicketForm(**data: Any)`
:   TicketForm type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description_html: str | None`
    :   The type of the None singleton.

    `fields: list[airbyte_agent_sdk.connectors.pylon.models.TicketFormField] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `is_public: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `slug: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="TicketFormField"></a>

`TicketFormField(**data: Any)`
:   TicketFormField type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description_html: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `slug: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="TicketFormsListResultMeta"></a>

`TicketFormsListResultMeta(**data: Any)`
:   Metadata for ticket_forms.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

<a id="TicketFormsResponse"></a>

`TicketFormsResponse(**data: Any)`
:   TicketFormsResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.pylon.models.TicketForm] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="TicketFormsSearchData"></a>

`TicketFormsSearchData(**data: Any)`
:   Search result data for ticket_forms entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   Unique identifier for the ticket form

    `is_public: bool | None`
    :   Whether the ticket form is publicly accessible

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Display name of the ticket form

    `slug: str | None`
    :   URL-safe identifier for the ticket form

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

    `avatar_url: str | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `emails: list[str] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `role_id: str | None`
    :   The type of the None singleton.

    `status: str | None`
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

    `data: airbyte_agent_sdk.connectors.pylon.models.User | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="UserRole"></a>

`UserRole(**data: Any)`
:   UserRole type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `slug: str | None`
    :   The type of the None singleton.

<a id="UserRolesListResultMeta"></a>

`UserRolesListResultMeta(**data: Any)`
:   Metadata for user_roles.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

<a id="UserRolesResponse"></a>

`UserRolesResponse(**data: Any)`
:   UserRolesResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.pylon.models.UserRole] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | None`
    :   The type of the None singleton.

    `request_id: str | None`
    :   The type of the None singleton.

<a id="UserRolesSearchData"></a>

`UserRolesSearchData(**data: Any)`
:   Search result data for user_roles entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: str`
    :   Unique identifier for the user role

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Display name of the user role

    `slug: str | None`
    :   URL-safe identifier for the user role

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

    `has_next_page: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | None`
    :   The type of the None singleton.

<a id="UsersResponse"></a>

`UsersResponse(**data: Any)`
:   UsersResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.pylon.models.User] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | None`
    :   The type of the None singleton.

    `request_id: str | None`
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
    :   Primary email address of the user

    `id: str`
    :   Unique identifier for the user

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Full name of the user

    `role_id: str | None`
    :   Identifier of the user's role

    `status: str | None`
    :   Current status of the user (e.g. active, disabled)