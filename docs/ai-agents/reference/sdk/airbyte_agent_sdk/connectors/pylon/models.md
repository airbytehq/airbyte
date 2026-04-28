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

    `channels: list[airbyte_agent_sdk.connectors.pylon.models.AccountChannel] | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `custom_fields: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `domain: str | Any | None`
    :   The type of the None singleton.

    `domains: list[str] | Any | None`
    :   The type of the None singleton.

    `external_ids: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_disabled: bool | Any | None`
    :   The type of the None singleton.

    `latest_customer_activity_time: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `owner: Any`
    :   The type of the None singleton.

    `primary_domain: str | Any | None`
    :   The type of the None singleton.

    `tags: list[str] | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
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

    `channel_id: str | Any | None`
    :   The type of the None singleton.

    `is_primary: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `source: str | Any | None`
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

    `domains: list[str] | Any`
    :   The type of the None singleton.

    `logo_url: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `owner_id: str | Any`
    :   The type of the None singleton.

    `primary_domain: str | Any`
    :   The type of the None singleton.

    `tags: list[str] | Any`
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

    `data: airbyte_agent_sdk.connectors.pylon.models.Account | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `domains: list[str] | Any`
    :   The type of the None singleton.

    `is_disabled: bool | Any`
    :   The type of the None singleton.

    `logo_url: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `owner_id: str | Any`
    :   The type of the None singleton.

    `primary_domain: str | Any`
    :   The type of the None singleton.

    `tags: list[str] | Any`
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

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
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

    `data: list[airbyte_agent_sdk.connectors.pylon.models.Account] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

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

    `author_user_id: str | Any | None`
    :   The type of the None singleton.

    `body_html: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_published: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
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

    `author_user_id: str | Any`
    :   The type of the None singleton.

    `body_html: str | Any`
    :   The type of the None singleton.

    `is_published: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `slug: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
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

    `data: airbyte_agent_sdk.connectors.pylon.models.Article | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `body_html: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | Any`
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

    `comment: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `score: int | Any | None`
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

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
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

    `description: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `slug: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
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

    `data: airbyte_agent_sdk.connectors.pylon.models.Collection | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `account: Any`
    :   The type of the None singleton.

    `avatar_url: str | Any | None`
    :   The type of the None singleton.

    `custom_fields: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `emails: list[str] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `integration_user_ids: list[airbyte_agent_sdk.connectors.pylon.models.IntegrationUserId] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `phone_numbers: list[str] | Any | None`
    :   The type of the None singleton.

    `portal_role: str | Any | None`
    :   The type of the None singleton.

    `portal_role_id: str | Any | None`
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

    `account_id: str | Any`
    :   The type of the None singleton.

    `avatar_url: str | Any`
    :   The type of the None singleton.

    `email: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
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

    `data: airbyte_agent_sdk.connectors.pylon.models.Contact | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `account_id: str | Any`
    :   The type of the None singleton.

    `email: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
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

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
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

    `data: list[airbyte_agent_sdk.connectors.pylon.models.Contact] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

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

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `default_value: str | Any | None`
    :   The type of the None singleton.

    `default_values: list[str] | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_read_only: bool | Any | None`
    :   The type of the None singleton.

    `label: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `number_metadata: Any`
    :   The type of the None singleton.

    `object_type: str | Any | None`
    :   The type of the None singleton.

    `select_metadata: Any`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

    `source: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
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

    `data: airbyte_agent_sdk.connectors.pylon.models.CustomField | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `slug: str | Any | None`
    :   The type of the None singleton.

    `value: str | Any | None`
    :   The type of the None singleton.

    `values: list[str] | Any | None`
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

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
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

    `data: list[airbyte_agent_sdk.connectors.pylon.models.CustomField] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `bcc_emails: list[str] | Any | None`
    :   The type of the None singleton.

    `cc_emails: list[str] | Any | None`
    :   The type of the None singleton.

    `from_email: str | Any | None`
    :   The type of the None singleton.

    `message_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `to_emails: list[str] | Any | None`
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

    `external_id: str | Any | None`
    :   The type of the None singleton.

    `link: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `source: str | Any | None`
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

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `source: str | Any | None`
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

    `account: Any`
    :   The type of the None singleton.

    `assignee: Any`
    :   The type of the None singleton.

    `attachment_urls: list[str] | Any | None`
    :   The type of the None singleton.

    `author_unverified: bool | Any | None`
    :   The type of the None singleton.

    `body_html: str | Any | None`
    :   The type of the None singleton.

    `business_hours_first_response_seconds: int | Any | None`
    :   The type of the None singleton.

    `business_hours_resolution_seconds: int | Any | None`
    :   The type of the None singleton.

    `chat_widget_info: Any`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `csat_responses: list[airbyte_agent_sdk.connectors.pylon.models.CSATResponse] | Any | None`
    :   The type of the None singleton.

    `custom_fields: dict[str, airbyte_agent_sdk.connectors.pylon.models.CustomFieldValue] | Any | None`
    :   The type of the None singleton.

    `customer_portal_visible: bool | Any | None`
    :   The type of the None singleton.

    `external_issues: list[airbyte_agent_sdk.connectors.pylon.models.ExternalIssue] | Any | None`
    :   The type of the None singleton.

    `first_response_seconds: int | Any | None`
    :   The type of the None singleton.

    `first_response_time: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `latest_message_time: str | Any | None`
    :   The type of the None singleton.

    `link: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `number: int | Any | None`
    :   The type of the None singleton.

    `number_of_touches: int | Any | None`
    :   The type of the None singleton.

    `requester: Any`
    :   The type of the None singleton.

    `resolution_seconds: int | Any | None`
    :   The type of the None singleton.

    `resolution_time: str | Any | None`
    :   The type of the None singleton.

    `slack: Any`
    :   The type of the None singleton.

    `snoozed_until_time: str | Any | None`
    :   The type of the None singleton.

    `source: Any`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

    `tags: list[str] | Any | None`
    :   The type of the None singleton.

    `team: Any`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `type_: Any`
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

    `page_url: str | Any | None`
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

    `account_id: str | Any`
    :   The type of the None singleton.

    `assignee_id: str | Any`
    :   The type of the None singleton.

    `body_html: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `priority: str | Any`
    :   The type of the None singleton.

    `requester_email: str | Any`
    :   The type of the None singleton.

    `requester_name: str | Any`
    :   The type of the None singleton.

    `tags: list[str] | Any`
    :   The type of the None singleton.

    `team_id: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
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

    `body_html: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `timestamp: str | Any | None`
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

    `body_html: str | Any`
    :   The type of the None singleton.

    `message_id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `thread_id: str | Any`
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

    `data: airbyte_agent_sdk.connectors.pylon.models.IssueNote | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `data: airbyte_agent_sdk.connectors.pylon.models.Issue | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
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

    `name: str | Any`
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

    `data: airbyte_agent_sdk.connectors.pylon.models.IssueThread | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `account_id: str | Any`
    :   The type of the None singleton.

    `assignee_id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `state: str | Any`
    :   The type of the None singleton.

    `tags: list[str] | Any`
    :   The type of the None singleton.

    `team_id: str | Any`
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

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
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

    `data: list[airbyte_agent_sdk.connectors.pylon.models.Issue] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

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

    `data: airbyte_agent_sdk.connectors.pylon.models.User | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `author: Any`
    :   The type of the None singleton.

    `email_info: Any`
    :   The type of the None singleton.

    `file_urls: list[str] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_private: bool | Any | None`
    :   The type of the None singleton.

    `message_html: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `source: str | Any | None`
    :   The type of the None singleton.

    `thread_id: str | Any | None`
    :   The type of the None singleton.

    `timestamp: str | Any | None`
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

    `avatar_url: str | Any | None`
    :   The type of the None singleton.

    `contact: Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `user: Any`
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

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
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

    `data: list[airbyte_agent_sdk.connectors.pylon.models.Message] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `due_date: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `project_id: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
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

    `due_date: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `project_id: str | Any`
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

    `data: airbyte_agent_sdk.connectors.pylon.models.Milestone | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `due_date: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
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

    `id: str | Any | None`
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

    `email: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
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

    `id: str | Any | None`
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

    `email: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
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

    `currency: str | Any | None`
    :   The type of the None singleton.

    `decimal_places: int | Any | None`
    :   The type of the None singleton.

    `format: str | Any | None`
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

    `cursor: str | Any | None`
    :   The type of the None singleton.

    `has_next_page: bool | Any`
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

    `account_id: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `description_html: str | Any | None`
    :   The type of the None singleton.

    `end_date: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_archived: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `owner_id: str | Any | None`
    :   The type of the None singleton.

    `start_date: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
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

    `account_id: str | Any`
    :   The type of the None singleton.

    `description_html: str | Any`
    :   The type of the None singleton.

    `end_date: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `start_date: str | Any`
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

    `data: airbyte_agent_sdk.connectors.pylon.models.Project | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `description_html: str | Any`
    :   The type of the None singleton.

    `is_archived: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
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

    `meta: ~S`
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

    `options: list[airbyte_agent_sdk.connectors.pylon.models.SelectOption] | Any | None`
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

    `label: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `slug: str | Any | None`
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

    `channel_id: str | Any | None`
    :   The type of the None singleton.

    `message_ts: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `workspace_id: str | Any | None`
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

    `hex_color: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_type: str | Any | None`
    :   The type of the None singleton.

    `value: str | Any | None`
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

    `hex_color: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `object_type: str | Any`
    :   The type of the None singleton.

    `value: str | Any`
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

    `data: airbyte_agent_sdk.connectors.pylon.models.Tag | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `hex_color: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `value: str | Any`
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

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
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

    `data: list[airbyte_agent_sdk.connectors.pylon.models.Tag] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `assignee_id: str | Any | None`
    :   The type of the None singleton.

    `body_html: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `due_date: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `milestone_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `project_id: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
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

    `assignee_id: str | Any`
    :   The type of the None singleton.

    `body_html: str | Any`
    :   The type of the None singleton.

    `due_date: str | Any`
    :   The type of the None singleton.

    `milestone_id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `project_id: str | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
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

    `data: airbyte_agent_sdk.connectors.pylon.models.Task | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `assignee_id: str | Any`
    :   The type of the None singleton.

    `body_html: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
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

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `users: list[airbyte_agent_sdk.connectors.pylon.models.MiniUser] | Any | None`
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

    `name: str | Any`
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

    `data: airbyte_agent_sdk.connectors.pylon.models.Team | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `name: str | Any`
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

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
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

    `data: list[airbyte_agent_sdk.connectors.pylon.models.Team] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.

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

    `description_html: str | Any | None`
    :   The type of the None singleton.

    `fields: list[airbyte_agent_sdk.connectors.pylon.models.TicketFormField] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_public: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

    `url: str | Any | None`
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

    `description_html: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
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

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
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

    `data: list[airbyte_agent_sdk.connectors.pylon.models.TicketForm] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `avatar_url: str | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `emails: list[str] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `role_id: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
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

    `data: airbyte_agent_sdk.connectors.pylon.models.User | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `slug: str | Any | None`
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

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
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

    `data: list[airbyte_agent_sdk.connectors.pylon.models.UserRole] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
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

    `has_next_page: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_cursor: str | Any | None`
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

    `data: list[airbyte_agent_sdk.connectors.pylon.models.User] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pagination: airbyte_agent_sdk.connectors.pylon.models.Pagination | Any`
    :   The type of the None singleton.

    `request_id: str | Any`
    :   The type of the None singleton.