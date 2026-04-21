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