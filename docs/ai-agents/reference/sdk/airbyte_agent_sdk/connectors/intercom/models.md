---
id: airbyte_agent_sdk-connectors-intercom-models
title: airbyte_agent_sdk.connectors.intercom.models
---

Module airbyte_agent_sdk.connectors.intercom.models
===================================================
Pydantic models for intercom connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="Admin"></a>

`Admin(**data: Any)`
:   Admin object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avatar: Any`
    :   The type of the None singleton.

    `away_mode_enabled: bool | Any | None`
    :   The type of the None singleton.

    `away_mode_reassign: bool | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `email_verified: bool | Any | None`
    :   The type of the None singleton.

    `has_inbox_seat: bool | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `job_title: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `team_ids: list[int] | Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="AdminPriorityLevel"></a>

`AdminPriorityLevel(**data: Any)`
:   Admin priority level settings
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `primary_admin_ids: list[int] | Any`
    :   The type of the None singleton.

    `secondary_admin_ids: list[int] | Any`
    :   The type of the None singleton.

<a id="AdminReference"></a>

`AdminReference(**data: Any)`
:   Admin reference
    
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

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="AdminsList"></a>

`AdminsList(**data: Any)`
:   List of admins
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admins: list[airbyte_agent_sdk.connectors.intercom.models.Admin] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
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

    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult[CompaniesSearchData]
    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult[ContactsSearchData]
    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult[ConversationsSearchData]
    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult[TeamsSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[CompaniesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CompaniesSearchResult"></a>

`CompaniesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ContactsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ConversationsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ConversationsSearchResult"></a>

`ConversationsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TeamsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.intercom.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Attachment"></a>

`Attachment(**data: Any)`
:   Message attachment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content_type: str | Any | None`
    :   The type of the None singleton.

    `filesize: int | Any | None`
    :   The type of the None singleton.

    `height: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

    `width: int | Any | None`
    :   The type of the None singleton.

<a id="Author"></a>

`Author(**data: Any)`
:   Message author
    
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

    `name: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="Avatar"></a>

`Avatar(**data: Any)`
:   Avatar image
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `image_url: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="CompaniesList"></a>

`CompaniesList(**data: Any)`
:   Paginated list of companies
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.intercom.models.Company] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pages: airbyte_agent_sdk.connectors.intercom.models.CompaniesListPages | Any | None`
    :   The type of the None singleton.

    `total_count: int | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="CompaniesListPages"></a>

`CompaniesListPages(**data: Any)`
:   Pagination metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: airbyte_agent_sdk.connectors.intercom.models.CompaniesListPagesNext | Any | None`
    :   Cursor for next page

    `page: int | Any | None`
    :   Current page number

    `per_page: int | Any | None`
    :   Number of items per page

    `total_pages: int | Any | None`
    :   Total number of pages

    `type_: str | Any | None`
    :   Type of pagination

<a id="CompaniesListPagesNext"></a>

`CompaniesListPagesNext(**data: Any)`
:   Cursor for next page
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   Next page number

    `starting_after: str | Any | None`
    :   Cursor for next page

<a id="CompaniesListResultMeta"></a>

`CompaniesListResultMeta(**data: Any)`
:   Metadata for companies.Action.LIST operation
    
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

<a id="CompaniesSearchData"></a>

`CompaniesSearchData(**data: Any)`
:   Search result data for companies entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `app_id: str | None`
    :   The ID of the application associated with the company

    `company_id: str | None`
    :   The unique identifier of the company

    `created_at: int | None`
    :   The date and time when the company was created

    `custom_attributes: dict[str, typing.Any] | None`
    :   Custom attributes specific to the company

    `id: str | None`
    :   The ID of the company

    `industry: str | None`
    :   The industry in which the company operates

    `model_config`
    :   The type of the None singleton.

    `monthly_spend: float | None`
    :   The monthly spend of the company

    `name: str | None`
    :   The name of the company

    `plan: dict[str, typing.Any] | None`
    :   Details of the company's subscription plan

    `remote_created_at: int | None`
    :   The remote date and time when the company was created

    `segments: dict[str, typing.Any] | None`
    :   Segments associated with the company

    `session_count: int | None`
    :   The number of sessions related to the company

    `size: int | None`
    :   The size of the company

    `tags: dict[str, typing.Any] | None`
    :   Tags associated with the company

    `type_: str | None`
    :   The type of the company

    `updated_at: int | None`
    :   The date and time when the company was last updated

    `user_count: int | None`
    :   The number of users associated with the company

    `website: str | None`
    :   The website of the company

<a id="Company"></a>

`Company(**data: Any)`
:   Company object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `app_id: str | Any | None`
    :   The type of the None singleton.

    `company_id: str | Any | None`
    :   The type of the None singleton.

    `created_at: int | Any | None`
    :   The type of the None singleton.

    `custom_attributes: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `industry: str | Any | None`
    :   The type of the None singleton.

    `last_request_at: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `monthly_spend: float | Any | None`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `plan: Any`
    :   The type of the None singleton.

    `remote_created_at: int | Any | None`
    :   The type of the None singleton.

    `segments: Any`
    :   The type of the None singleton.

    `session_count: int | Any | None`
    :   The type of the None singleton.

    `size: int | Any | None`
    :   The type of the None singleton.

    `tags: Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `updated_at: int | Any | None`
    :   The type of the None singleton.

    `user_count: int | Any | None`
    :   The type of the None singleton.

    `website: str | Any | None`
    :   The type of the None singleton.

<a id="CompanyCreateParams"></a>

`CompanyCreateParams(**data: Any)`
:   CompanyCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `company_id: str | Any`
    :   The type of the None singleton.

    `custom_attributes: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `industry: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `monthly_spend: float | Any`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `plan: str | Any`
    :   The type of the None singleton.

    `size: int | Any`
    :   The type of the None singleton.

    `website: str | Any`
    :   The type of the None singleton.

<a id="CompanyPlan"></a>

`CompanyPlan(**data: Any)`
:   Company plan
    
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

    `name: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="CompanyReference"></a>

`CompanyReference(**data: Any)`
:   Company reference
    
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

    `type_: str | Any | None`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="CompanySegments"></a>

`CompanySegments(**data: Any)`
:   Segments for company
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `segments: list[airbyte_agent_sdk.connectors.intercom.models.Segment] | Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="CompanyTags"></a>

`CompanyTags(**data: Any)`
:   Tags on company
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `tags: list[airbyte_agent_sdk.connectors.intercom.models.Tag] | Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="CompanyUpdateParams"></a>

`CompanyUpdateParams(**data: Any)`
:   CompanyUpdateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `custom_attributes: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `industry: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `monthly_spend: float | Any`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `plan: str | Any`
    :   The type of the None singleton.

    `size: int | Any`
    :   The type of the None singleton.

    `website: str | Any`
    :   The type of the None singleton.

<a id="Contact"></a>

`Contact(**data: Any)`
:   Contact object representing a user or lead
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `android_app_name: str | Any | None`
    :   The type of the None singleton.

    `android_app_version: str | Any | None`
    :   The type of the None singleton.

    `android_device: str | Any | None`
    :   The type of the None singleton.

    `android_last_seen_at: int | Any | None`
    :   The type of the None singleton.

    `android_os_version: str | Any | None`
    :   The type of the None singleton.

    `android_sdk_version: str | Any | None`
    :   The type of the None singleton.

    `avatar: str | Any | None`
    :   The type of the None singleton.

    `browser: str | Any | None`
    :   The type of the None singleton.

    `browser_language: str | Any | None`
    :   The type of the None singleton.

    `browser_version: str | Any | None`
    :   The type of the None singleton.

    `companies: Any`
    :   The type of the None singleton.

    `created_at: int | Any | None`
    :   The type of the None singleton.

    `custom_attributes: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `external_id: str | Any | None`
    :   The type of the None singleton.

    `has_hard_bounced: bool | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `ios_app_name: str | Any | None`
    :   The type of the None singleton.

    `ios_app_version: str | Any | None`
    :   The type of the None singleton.

    `ios_device: str | Any | None`
    :   The type of the None singleton.

    `ios_last_seen_at: int | Any | None`
    :   The type of the None singleton.

    `ios_os_version: str | Any | None`
    :   The type of the None singleton.

    `ios_sdk_version: str | Any | None`
    :   The type of the None singleton.

    `language_override: str | Any | None`
    :   The type of the None singleton.

    `last_contacted_at: int | Any | None`
    :   The type of the None singleton.

    `last_email_clicked_at: int | Any | None`
    :   The type of the None singleton.

    `last_email_opened_at: int | Any | None`
    :   The type of the None singleton.

    `last_replied_at: int | Any | None`
    :   The type of the None singleton.

    `last_seen_at: int | Any | None`
    :   The type of the None singleton.

    `location: Any`
    :   The type of the None singleton.

    `marked_email_as_spam: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `notes: Any`
    :   The type of the None singleton.

    `os: str | Any | None`
    :   The type of the None singleton.

    `owner_id: int | Any | None`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `role: str | Any | None`
    :   The type of the None singleton.

    `signed_up_at: int | Any | None`
    :   The type of the None singleton.

    `social_profiles: Any`
    :   The type of the None singleton.

    `tags: Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `unsubscribed_from_emails: bool | Any | None`
    :   The type of the None singleton.

    `updated_at: int | Any | None`
    :   The type of the None singleton.

    `workspace_id: str | Any | None`
    :   The type of the None singleton.

<a id="ContactCompanies"></a>

`ContactCompanies(**data: Any)`
:   Companies associated with contact
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.intercom.models.CompanyReference] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
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

    `avatar: str | Any`
    :   The type of the None singleton.

    `custom_attributes: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `email: str | Any`
    :   The type of the None singleton.

    `external_id: str | Any`
    :   The type of the None singleton.

    `last_seen_at: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `owner_id: int | Any`
    :   The type of the None singleton.

    `phone: str | Any`
    :   The type of the None singleton.

    `role: str | Any`
    :   The type of the None singleton.

    `signed_up_at: int | Any`
    :   The type of the None singleton.

    `unsubscribed_from_emails: bool | Any`
    :   The type of the None singleton.

<a id="ContactNotes"></a>

`ContactNotes(**data: Any)`
:   Notes associated with contact
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.intercom.models.NoteReference] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="ContactReference"></a>

`ContactReference(**data: Any)`
:   Contact reference
    
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

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="ContactTags"></a>

`ContactTags(**data: Any)`
:   Tags associated with contact
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.intercom.models.TagReference] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
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

    `avatar: str | Any`
    :   The type of the None singleton.

    `custom_attributes: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `email: str | Any`
    :   The type of the None singleton.

    `external_id: str | Any`
    :   The type of the None singleton.

    `last_seen_at: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `owner_id: int | Any`
    :   The type of the None singleton.

    `phone: str | Any`
    :   The type of the None singleton.

    `role: str | Any`
    :   The type of the None singleton.

    `signed_up_at: int | Any`
    :   The type of the None singleton.

    `unsubscribed_from_emails: bool | Any`
    :   The type of the None singleton.

<a id="ContactsList"></a>

`ContactsList(**data: Any)`
:   Paginated list of contacts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.intercom.models.Contact] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pages: airbyte_agent_sdk.connectors.intercom.models.ContactsListPages | Any | None`
    :   The type of the None singleton.

    `total_count: int | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="ContactsListPages"></a>

`ContactsListPages(**data: Any)`
:   Pagination metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: airbyte_agent_sdk.connectors.intercom.models.ContactsListPagesNext | Any | None`
    :   Cursor for next page

    `page: int | Any | None`
    :   Current page number

    `per_page: int | Any | None`
    :   Number of items per page

    `total_pages: int | Any | None`
    :   Total number of pages

    `type_: str | Any | None`
    :   Type of pagination

<a id="ContactsListPagesNext"></a>

`ContactsListPagesNext(**data: Any)`
:   Cursor for next page
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   Next page number

    `starting_after: str | Any | None`
    :   Cursor for next page

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

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
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

    `android_app_name: str | None`
    :   The name of the Android app associated with the contact.

    `android_app_version: str | None`
    :   The version of the Android app associated with the contact.

    `android_device: str | None`
    :   The device used by the contact for Android.

    `android_last_seen_at: str | None`
    :   The date and time when the contact was last seen on Android.

    `android_os_version: str | None`
    :   The operating system version of the Android device.

    `android_sdk_version: str | None`
    :   The SDK version of the Android device.

    `avatar: str | None`
    :   URL pointing to the contact's avatar image.

    `browser: str | None`
    :   The browser used by the contact.

    `browser_language: str | None`
    :   The language preference set in the contact's browser.

    `browser_version: str | None`
    :   The version of the browser used by the contact.

    `companies: dict[str, typing.Any] | None`
    :   Companies associated with the contact.

    `created_at: int | None`
    :   The date and time when the contact was created.

    `custom_attributes: dict[str, typing.Any] | None`
    :   Custom attributes defined for the contact.

    `email: str | None`
    :   The email address of the contact.

    `external_id: str | None`
    :   External identifier for the contact.

    `has_hard_bounced: bool | None`
    :   Flag indicating if the contact has hard bounced.

    `id: str | None`
    :   The unique identifier of the contact.

    `ios_app_name: str | None`
    :   The name of the iOS app associated with the contact.

    `ios_app_version: str | None`
    :   The version of the iOS app associated with the contact.

    `ios_device: str | None`
    :   The device used by the contact for iOS.

    `ios_last_seen_at: int | None`
    :   The date and time when the contact was last seen on iOS.

    `ios_os_version: str | None`
    :   The operating system version of the iOS device.

    `ios_sdk_version: str | None`
    :   The SDK version of the iOS device.

    `language_override: str | None`
    :   Language override set for the contact.

    `last_contacted_at: int | None`
    :   The date and time when the contact was last contacted.

    `last_email_clicked_at: int | None`
    :   The date and time when the contact last clicked an email.

    `last_email_opened_at: int | None`
    :   The date and time when the contact last opened an email.

    `last_replied_at: int | None`
    :   The date and time when the contact last replied.

    `last_seen_at: int | None`
    :   The date and time when the contact was last seen overall.

    `location: dict[str, typing.Any] | None`
    :   Location details of the contact.

    `marked_email_as_spam: bool | None`
    :   Flag indicating if the contact's email was marked as spam.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the contact.

    `notes: dict[str, typing.Any] | None`
    :   Notes associated with the contact.

    `opted_in_subscription_types: dict[str, typing.Any] | None`
    :   Subscription types the contact opted into.

    `opted_out_subscription_types: dict[str, typing.Any] | None`
    :   Subscription types the contact opted out from.

    `os: str | None`
    :   Operating system of the contact's device.

    `owner_id: int | None`
    :   The unique identifier of the contact's owner.

    `phone: str | None`
    :   The phone number of the contact.

    `referrer: str | None`
    :   Referrer information related to the contact.

    `role: str | None`
    :   Role or position of the contact.

    `signed_up_at: int | None`
    :   The date and time when the contact signed up.

    `sms_consent: bool | None`
    :   Consent status for SMS communication.

    `social_profiles: dict[str, typing.Any] | None`
    :   Social profiles associated with the contact.

    `tags: dict[str, typing.Any] | None`
    :   Tags associated with the contact.

    `type_: str | None`
    :   Type of contact.

    `unsubscribed_from_emails: bool | None`
    :   Flag indicating if the contact unsubscribed from emails.

    `unsubscribed_from_sms: bool | None`
    :   Flag indicating if the contact unsubscribed from SMS.

    `updated_at: int | None`
    :   The date and time when the contact was last updated.

    `utm_campaign: str | None`
    :   Campaign data from UTM parameters.

    `utm_content: str | None`
    :   Content data from UTM parameters.

    `utm_medium: str | None`
    :   Medium data from UTM parameters.

    `utm_source: str | None`
    :   Source data from UTM parameters.

    `utm_term: str | None`
    :   Term data from UTM parameters.

    `workspace_id: str | None`
    :   The unique identifier of the workspace associated with the contact.

<a id="Conversation"></a>

`Conversation(**data: Any)`
:   Conversation object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_assignee_id: int | Any | None`
    :   The type of the None singleton.

    `contacts: Any`
    :   The type of the None singleton.

    `conversation_parts: Any`
    :   The type of the None singleton.

    `conversation_rating: Any`
    :   The type of the None singleton.

    `created_at: int | Any | None`
    :   The type of the None singleton.

    `custom_attributes: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `first_contact_reply: Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `open: bool | Any | None`
    :   The type of the None singleton.

    `priority: str | Any | None`
    :   The type of the None singleton.

    `read: bool | Any | None`
    :   The type of the None singleton.

    `sla_applied: Any`
    :   The type of the None singleton.

    `snoozed_until: int | Any | None`
    :   The type of the None singleton.

    `source: Any`
    :   The type of the None singleton.

    `state: str | Any | None`
    :   The type of the None singleton.

    `statistics: Any`
    :   The type of the None singleton.

    `tags: Any`
    :   The type of the None singleton.

    `team_assignee_id: str | Any | None`
    :   The type of the None singleton.

    `teammates: Any`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `updated_at: int | Any | None`
    :   The type of the None singleton.

    `waiting_since: int | Any | None`
    :   The type of the None singleton.

<a id="ConversationContacts"></a>

`ConversationContacts(**data: Any)`
:   Contacts in conversation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `contacts: list[airbyte_agent_sdk.connectors.intercom.models.ContactReference] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="ConversationPart"></a>

`ConversationPart(**data: Any)`
:   Conversation part (message, note, action)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assigned_to: Any`
    :   The type of the None singleton.

    `attachments: list[airbyte_agent_sdk.connectors.intercom.models.Attachment] | Any`
    :   The type of the None singleton.

    `author: Any`
    :   The type of the None singleton.

    `body: str | Any | None`
    :   The type of the None singleton.

    `created_at: int | Any | None`
    :   The type of the None singleton.

    `external_id: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `notified_at: int | Any | None`
    :   The type of the None singleton.

    `part_type: str | Any | None`
    :   The type of the None singleton.

    `redacted: bool | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `updated_at: int | Any | None`
    :   The type of the None singleton.

<a id="ConversationPartsReference"></a>

`ConversationPartsReference(**data: Any)`
:   Reference to conversation parts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `conversation_parts: list[airbyte_agent_sdk.connectors.intercom.models.ConversationPart] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_count: int | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="ConversationRating"></a>

`ConversationRating(**data: Any)`
:   Conversation rating
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `contact: Any`
    :   The type of the None singleton.

    `created_at: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rating: int | Any | None`
    :   The type of the None singleton.

    `remark: str | Any | None`
    :   The type of the None singleton.

    `teammate: Any`
    :   The type of the None singleton.

<a id="ConversationSource"></a>

`ConversationSource(**data: Any)`
:   Conversation source
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attachments: list[airbyte_agent_sdk.connectors.intercom.models.Attachment] | Any`
    :   The type of the None singleton.

    `author: Any`
    :   The type of the None singleton.

    `body: str | Any | None`
    :   The type of the None singleton.

    `delivered_as: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `redacted: bool | Any | None`
    :   The type of the None singleton.

    `subject: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="ConversationStatistics"></a>

`ConversationStatistics(**data: Any)`
:   Conversation statistics
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count_assignments: int | Any | None`
    :   The type of the None singleton.

    `count_conversation_parts: int | Any | None`
    :   The type of the None singleton.

    `count_reopens: int | Any | None`
    :   The type of the None singleton.

    `first_admin_reply_at: int | Any | None`
    :   The type of the None singleton.

    `first_assignment_at: int | Any | None`
    :   The type of the None singleton.

    `first_close_at: int | Any | None`
    :   The type of the None singleton.

    `first_contact_reply_at: int | Any | None`
    :   The type of the None singleton.

    `last_admin_reply_at: int | Any | None`
    :   The type of the None singleton.

    `last_assignment_admin_reply_at: int | Any | None`
    :   The type of the None singleton.

    `last_assignment_at: int | Any | None`
    :   The type of the None singleton.

    `last_close_at: int | Any | None`
    :   The type of the None singleton.

    `last_closed_by_id: str | Any | None`
    :   The type of the None singleton.

    `last_contact_reply_at: int | Any | None`
    :   The type of the None singleton.

    `median_time_to_reply: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `time_to_admin_reply: int | Any | None`
    :   The type of the None singleton.

    `time_to_assignment: int | Any | None`
    :   The type of the None singleton.

    `time_to_first_close: int | Any | None`
    :   The type of the None singleton.

    `time_to_last_close: int | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="ConversationTags"></a>

`ConversationTags(**data: Any)`
:   Tags on conversation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `tags: list[airbyte_agent_sdk.connectors.intercom.models.Tag] | Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="ConversationTeammates"></a>

`ConversationTeammates(**data: Any)`
:   Teammates in conversation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admins: list[airbyte_agent_sdk.connectors.intercom.models.AdminReference] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="ConversationsList"></a>

`ConversationsList(**data: Any)`
:   Paginated list of conversations
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `conversations: list[airbyte_agent_sdk.connectors.intercom.models.Conversation] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `pages: airbyte_agent_sdk.connectors.intercom.models.ConversationsListPages | Any | None`
    :   The type of the None singleton.

    `total_count: int | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="ConversationsListPages"></a>

`ConversationsListPages(**data: Any)`
:   Pagination metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: airbyte_agent_sdk.connectors.intercom.models.ConversationsListPagesNext | Any | None`
    :   Cursor for next page

    `page: int | Any | None`
    :   Current page number

    `per_page: int | Any | None`
    :   Number of items per page

    `total_pages: int | Any | None`
    :   Total number of pages

    `type_: str | Any | None`
    :   Type of pagination

<a id="ConversationsListPagesNext"></a>

`ConversationsListPagesNext(**data: Any)`
:   Cursor for next page
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   Next page number

    `starting_after: str | Any | None`
    :   Cursor for next page

<a id="ConversationsListResultMeta"></a>

`ConversationsListResultMeta(**data: Any)`
:   Metadata for conversations.Action.LIST operation
    
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

<a id="ConversationsSearchData"></a>

`ConversationsSearchData(**data: Any)`
:   Search result data for conversations entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_assignee_id: int | None`
    :   The ID of the administrator assigned to the conversation

    `ai_agent: dict[str, typing.Any] | None`
    :   Data related to AI Agent involvement in the conversation

    `ai_agent_participated: bool | None`
    :   Indicates whether AI Agent participated in the conversation

    `assignee: dict[str, typing.Any] | None`
    :   The assigned user responsible for the conversation.

    `contacts: dict[str, typing.Any] | None`
    :   List of contacts involved in the conversation.

    `conversation_message: dict[str, typing.Any] | None`
    :   The main message content of the conversation.

    `conversation_rating: dict[str, typing.Any] | None`
    :   Ratings given to the conversation by the customer and teammate.

    `created_at: int | None`
    :   The timestamp when the conversation was created

    `custom_attributes: dict[str, typing.Any] | None`
    :   Custom attributes associated with the conversation

    `customer_first_reply: dict[str, typing.Any] | None`
    :   Timestamp indicating when the customer first replied.

    `customers: list[typing.Any] | None`
    :   List of customers involved in the conversation

    `first_contact_reply: dict[str, typing.Any] | None`
    :   Timestamp indicating when the first contact replied.

    `id: str | None`
    :   The unique ID of the conversation

    `linked_objects: dict[str, typing.Any] | None`
    :   Linked objects associated with the conversation

    `model_config`
    :   The type of the None singleton.

    `open: bool | None`
    :   Indicates if the conversation is open or closed

    `priority: str | None`
    :   The priority level of the conversation

    `read: bool | None`
    :   Indicates if the conversation has been read

    `redacted: bool | None`
    :   Indicates if the conversation is redacted

    `sent_at: int | None`
    :   The timestamp when the conversation was sent

    `sla_applied: dict[str, typing.Any] | None`
    :   Service Level Agreement details applied to the conversation.

    `snoozed_until: int | None`
    :   Timestamp until the conversation is snoozed

    `source: dict[str, typing.Any] | None`
    :   Source details of the conversation.

    `state: str | None`
    :   The state of the conversation (e.g., new, in progress)

    `statistics: dict[str, typing.Any] | None`
    :   Statistics related to the conversation.

    `tags: dict[str, typing.Any] | None`
    :   Tags applied to the conversation.

    `team_assignee_id: int | None`
    :   The ID of the team assigned to the conversation

    `teammates: dict[str, typing.Any] | None`
    :   List of teammates involved in the conversation.

    `title: str | None`
    :   The title of the conversation

    `topics: dict[str, typing.Any] | None`
    :   Topics associated with the conversation.

    `type_: str | None`
    :   The type of the conversation

    `updated_at: int | None`
    :   The timestamp when the conversation was last updated

    `user: dict[str, typing.Any] | None`
    :   The user related to the conversation.

    `waiting_since: int | None`
    :   Timestamp since waiting for a response

<a id="FirstContactReply"></a>

`FirstContactReply(**data: Any)`
:   First contact reply info
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="IntercomAuthConfig"></a>

`IntercomAuthConfig(**data: Any)`
:   Access Token Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   Your Intercom API Access Token

    `model_config`
    :   The type of the None singleton.

<a id="IntercomCheckResult"></a>

`IntercomCheckResult(**data: Any)`
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

<a id="IntercomExecuteResult"></a>

`IntercomExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult[list[Admin]]
    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult[list[Segment]]
    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult[list[Tag]]
    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult[list[Team]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="IntercomExecuteResultWithMeta"></a>

`IntercomExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResultWithMeta[list[Company], CompaniesListResultMeta]
    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResultWithMeta[list[Contact], ContactsListResultMeta]
    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResultWithMeta[list[Conversation], ConversationsListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`IntercomExecuteResultWithMeta[list[Company], CompaniesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CompaniesListResult"></a>

`CompaniesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IntercomExecuteResultWithMeta[list[Contact], ContactsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult
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

    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IntercomExecuteResultWithMeta[list[Conversation], ConversationsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ConversationsListResult"></a>

`ConversationsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IntercomExecuteResult[list[Admin]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AdminsListResult"></a>

`AdminsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IntercomExecuteResult[list[Segment]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SegmentsListResult"></a>

`SegmentsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IntercomExecuteResult[list[Tag]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TagsListResult"></a>

`TagsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`IntercomExecuteResult[list[Team]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TeamsListResult"></a>

`TeamsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.intercom.models.IntercomExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="IntercomReplicationConfig"></a>

`IntercomReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Intercom.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `start_date: str`
    :   UTC date and time in the format YYYY-MM-DDTHH:mm:ssZ from which to start replicating data.

<a id="InternalArticle"></a>

`InternalArticle(**data: Any)`
:   Internal article object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_id: int | Any | None`
    :   The type of the None singleton.

    `body: str | Any | None`
    :   The type of the None singleton.

    `created_at: int | Any | None`
    :   The type of the None singleton.

    `id: Any`
    :   The type of the None singleton.

    `locale: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `owner_id: int | Any | None`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `updated_at: int | Any | None`
    :   The type of the None singleton.

<a id="InternalArticleCreateParams"></a>

`InternalArticleCreateParams(**data: Any)`
:   InternalArticleCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_id: int | Any`
    :   The type of the None singleton.

    `body: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `owner_id: int | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

<a id="Location"></a>

`Location(**data: Any)`
:   Location information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `city: str | Any | None`
    :   The type of the None singleton.

    `continent_code: str | Any | None`
    :   The type of the None singleton.

    `country: str | Any | None`
    :   The type of the None singleton.

    `country_code: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `region: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="Note"></a>

`Note(**data: Any)`
:   Note object on a contact
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author: Any`
    :   The type of the None singleton.

    `body: str | Any | None`
    :   The type of the None singleton.

    `contact: Any`
    :   The type of the None singleton.

    `created_at: int | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="NoteCreateParams"></a>

`NoteCreateParams(**data: Any)`
:   NoteCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_id: str | Any`
    :   The type of the None singleton.

    `body: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="NoteReference"></a>

`NoteReference(**data: Any)`
:   Note reference
    
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

    `type_: str | Any | None`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="Pages"></a>

`Pages(**data: Any)`
:   Pagination metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: airbyte_agent_sdk.connectors.intercom.models.PagesNext | Any | None`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   The type of the None singleton.

    `per_page: int | Any | None`
    :   The type of the None singleton.

    `total_pages: int | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="PagesNext"></a>

`PagesNext(**data: Any)`
:   Cursor for next page
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `page: int | Any | None`
    :   Next page number

    `starting_after: str | Any | None`
    :   Cursor for next page

<a id="Segment"></a>

`Segment(**data: Any)`
:   Segment object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any | None`
    :   The type of the None singleton.

    `created_at: int | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `person_type: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `updated_at: int | Any | None`
    :   The type of the None singleton.

<a id="SegmentsList"></a>

`SegmentsList(**data: Any)`
:   List of segments
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `segments: list[airbyte_agent_sdk.connectors.intercom.models.Segment] | Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="SlaApplied"></a>

`SlaApplied(**data: Any)`
:   SLA applied to conversation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `sla_name: str | Any | None`
    :   The type of the None singleton.

    `sla_status: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="SocialProfile"></a>

`SocialProfile(**data: Any)`
:   Social profile
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="SocialProfiles"></a>

`SocialProfiles(**data: Any)`
:   Social profiles
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.intercom.models.SocialProfile] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="Tag"></a>

`Tag(**data: Any)`
:   Tag object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `applied_at: int | Any | None`
    :   The type of the None singleton.

    `applied_by: Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
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

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

<a id="TagReference"></a>

`TagReference(**data: Any)`
:   Tag reference
    
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

    `type_: str | Any | None`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="TagsList"></a>

`TagsList(**data: Any)`
:   List of tags
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.intercom.models.Tag] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="Team"></a>

`Team(**data: Any)`
:   Team object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `admin_ids: list[int] | Any`
    :   The type of the None singleton.

    `admin_priority_level: Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="TeamsList"></a>

`TeamsList(**data: Any)`
:   List of teams
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `teams: list[airbyte_agent_sdk.connectors.intercom.models.Team] | Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
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

    `admin_ids: list[typing.Any] | None`
    :   Array of user IDs representing the admins of the team.

    `id: str | None`
    :   Unique identifier for the team.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the team.

    `type_: str | None`
    :   Type of team (e.g., 'internal', 'external').