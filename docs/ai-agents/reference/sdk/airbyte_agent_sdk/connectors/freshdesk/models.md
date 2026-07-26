---
id: airbyte_agent_sdk-connectors-freshdesk-models
title: airbyte_agent_sdk.connectors.freshdesk.models
---

Module airbyte_agent_sdk.connectors.freshdesk.models
====================================================
Pydantic models for freshdesk connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="Agent"></a>

`Agent(**data: Any)`
:   A Freshdesk agent
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_operational_status: str | None`
    :   The type of the None singleton.

    `availability: typing.Any | None`
    :   The type of the None singleton.

    `available: bool | None`
    :   The type of the None singleton.

    `available_since: str | None`
    :   The type of the None singleton.

    `contact: airbyte_agent_sdk.connectors.freshdesk.models.AgentContact | None`
    :   The type of the None singleton.

    `contribution_group_ids: list[int] | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `deactivated: bool | None`
    :   The type of the None singleton.

    `focus_mode: bool | None`
    :   The type of the None singleton.

    `group_ids: list[int] | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `last_active_at: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `occasional: bool | None`
    :   The type of the None singleton.

    `org_agent_id: str | None`
    :   The type of the None singleton.

    `org_contribution_group_ids: list[str] | None`
    :   The type of the None singleton.

    `org_group_ids: list[str] | None`
    :   The type of the None singleton.

    `role_ids: list[int] | None`
    :   The type of the None singleton.

    `scope: typing.Any | None`
    :   The type of the None singleton.

    `signature: str | None`
    :   The type of the None singleton.

    `skill_ids: list[int] | None`
    :   The type of the None singleton.

    `ticket_scope: int | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="AgentContact"></a>

`AgentContact(**data: Any)`
:   Contact details of the agent
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | None`
    :   Whether the contact is active

    `created_at: str | None`
    :   Contact creation timestamp

    `email: str | None`
    :   Email of the agent

    `job_title: str | None`
    :   Job title

    `language: str | None`
    :   Language

    `last_login_at: str | None`
    :   Last login timestamp

    `mobile: str | None`
    :   Mobile number

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the agent

    `phone: str | None`
    :   Phone number

    `time_zone: str | None`
    :   Time zone

    `updated_at: str | None`
    :   Contact update timestamp

<a id="AgentsListResultMeta"></a>

`AgentsListResultMeta(**data: Any)`
:   Metadata for agents.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | None`
    :   The type of the None singleton.

<a id="AgentsSearchData"></a>

`AgentsSearchData(**data: Any)`
:   Search result data for agents entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `available: bool | None`
    :   Whether the agent is available

    `available_since: str | None`
    :   Timestamp since the agent has been available

    `contact: dict[str, typing.Any] | None`
    :   Contact details of the agent including name, email, phone, and job title

    `created_at: str | None`
    :   Agent creation timestamp

    `id: int | None`
    :   Unique agent ID

    `last_active_at: str | None`
    :   Timestamp of last agent activity

    `model_config`
    :   The type of the None singleton.

    `occasional: bool | None`
    :   Whether the agent is an occasional agent

    `signature: str | None`
    :   Signature of the agent (HTML)

    `ticket_scope: int | None`
    :   Ticket scope: 1=Global, 2=Group, 3=Restricted

    `type_: str | None`
    :   Agent type: support_agent, field_agent, collaborator

    `updated_at: str | None`
    :   Agent last update timestamp

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

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[AgentsSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[CompaniesSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[ContactsSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[GroupsSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[RolesSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[SatisfactionRatingsSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[SurveysSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[TicketFieldsSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[TicketsSearchData]
    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult[TimeEntriesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[AgentsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AgentsSearchResult"></a>

`AgentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CompaniesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ContactsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[GroupsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[RolesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="RolesSearchResult"></a>

`RolesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SatisfactionRatingsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SatisfactionRatingsSearchResult"></a>

`SatisfactionRatingsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SurveysSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SurveysSearchResult"></a>

`SurveysSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TicketFieldsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TicketFieldsSearchResult"></a>

`TicketFieldsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TicketsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TicketsSearchResult"></a>

`TicketsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TimeEntriesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TimeEntriesSearchResult"></a>

`TimeEntriesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

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

    `next: str | None`
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

    `account_tier: str | None`
    :   Account tier of the company

    `created_at: str | None`
    :   Company creation timestamp

    `custom_fields: dict[str, typing.Any] | None`
    :   Custom fields associated with the company

    `description: str | None`
    :   Description of the company

    `domains: list[typing.Any] | None`
    :   Email domains associated with the company

    `health_score: str | None`
    :   Health score of the company

    `id: int | None`
    :   Unique company ID

    `industry: str | None`
    :   Industry of the company

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the company

    `note: str | None`
    :   Notes about the company

    `renewal_date: str | None`
    :   Renewal date

    `updated_at: str | None`
    :   Company last update timestamp

<a id="Company"></a>

`Company(**data: Any)`
:   A Freshdesk company
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_tier: str | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `custom_fields: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `domains: list[str] | None`
    :   The type of the None singleton.

    `health_score: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `industry: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `note: str | None`
    :   The type of the None singleton.

    `org_company_id: typing.Any | None`
    :   The type of the None singleton.

    `org_company_id_str: str | None`
    :   The type of the None singleton.

    `renewal_date: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="Contact"></a>

`Contact(**data: Any)`
:   A Freshdesk contact (customer)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | None`
    :   The type of the None singleton.

    `address: str | None`
    :   The type of the None singleton.

    `avatar: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `company_id: int | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `csat_rating: int | None`
    :   The type of the None singleton.

    `custom_fields: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `deleted: bool | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `facebook_id: str | None`
    :   The type of the None singleton.

    `first_name: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `job_title: str | None`
    :   The type of the None singleton.

    `language: str | None`
    :   The type of the None singleton.

    `last_name: str | None`
    :   The type of the None singleton.

    `mobile: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `org_contact_id: int | None`
    :   The type of the None singleton.

    `org_contact_id_str: str | None`
    :   The type of the None singleton.

    `other_companies: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `other_emails: list[str] | None`
    :   The type of the None singleton.

    `other_phone_numbers: list[str] | None`
    :   The type of the None singleton.

    `phone: str | None`
    :   The type of the None singleton.

    `preferred_source: str | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

    `time_zone: str | None`
    :   The type of the None singleton.

    `twitter_id: str | None`
    :   The type of the None singleton.

    `unique_external_id: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `view_all_tickets: bool | None`
    :   The type of the None singleton.

    `visitor_id: str | None`
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

    `model_config`
    :   The type of the None singleton.

    `next: str | None`
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

    `active: bool | None`
    :   Whether the contact has been verified

    `address: str | None`
    :   Address of the contact

    `company_id: int | None`
    :   ID of the primary company

    `created_at: str | None`
    :   Contact creation timestamp

    `csat_rating: int | None`
    :   CSAT rating of the contact

    `custom_fields: dict[str, typing.Any] | None`
    :   Custom fields associated with the contact

    `description: str | None`
    :   Description of the contact

    `email: str | None`
    :   Primary email address

    `facebook_id: str | None`
    :   Facebook ID of the contact

    `id: int | None`
    :   Unique contact ID

    `job_title: str | None`
    :   Job title of the contact

    `language: str | None`
    :   Language of the contact

    `mobile: str | None`
    :   Mobile number

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the contact

    `phone: str | None`
    :   Phone number

    `preferred_source: str | None`
    :   Preferred contact source

    `time_zone: str | None`
    :   Time zone of the contact

    `twitter_id: str | None`
    :   Twitter ID

    `unique_external_id: str | None`
    :   External ID of the contact

    `updated_at: str | None`
    :   Contact last update timestamp

<a id="FreshdeskAuthConfig"></a>

`FreshdeskAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your Freshdesk API key (found in Profile Settings)

    `model_config`
    :   The type of the None singleton.

<a id="FreshdeskCheckResult"></a>

`FreshdeskCheckResult(**data: Any)`
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

<a id="FreshdeskExecuteResult"></a>

`FreshdeskExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="FreshdeskExecuteResultWithMeta"></a>

`FreshdeskExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[Agent], AgentsListResultMeta]
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[Company], CompaniesListResultMeta]
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[Contact], ContactsListResultMeta]
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[Group], GroupsListResultMeta]
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[Role], RolesListResultMeta]
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[SatisfactionRating], SatisfactionRatingsListResultMeta]
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[Survey], SurveysListResultMeta]
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[TicketField], TicketFieldsListResultMeta]
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[Ticket], TicketsListResultMeta]
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta[list[TimeEntry], TimeEntriesListResultMeta]

    ### Class variables

    `meta: ~S | None`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`FreshdeskExecuteResultWithMeta[list[Agent], AgentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AgentsListResult"></a>

`AgentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FreshdeskExecuteResultWithMeta[list[Company], CompaniesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
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

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FreshdeskExecuteResultWithMeta[list[Contact], ContactsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
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

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FreshdeskExecuteResultWithMeta[list[Group], GroupsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
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

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FreshdeskExecuteResultWithMeta[list[Role], RolesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="RolesListResult"></a>

`RolesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FreshdeskExecuteResultWithMeta[list[SatisfactionRating], SatisfactionRatingsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SatisfactionRatingsListResult"></a>

`SatisfactionRatingsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FreshdeskExecuteResultWithMeta[list[Survey], SurveysListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SurveysListResult"></a>

`SurveysListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FreshdeskExecuteResultWithMeta[list[TicketField], TicketFieldsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TicketFieldsListResult"></a>

`TicketFieldsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FreshdeskExecuteResultWithMeta[list[Ticket], TicketsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TicketsListResult"></a>

`TicketsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`FreshdeskExecuteResultWithMeta[list[TimeEntry], TimeEntriesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TimeEntriesListResult"></a>

`TimeEntriesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.freshdesk.models.FreshdeskExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Group"></a>

`Group(**data: Any)`
:   A Freshdesk group
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_availability_status: bool | None`
    :   The type of the None singleton.

    `agent_ids: list[int] | None`
    :   The type of the None singleton.

    `allow_agents_to_change_availability: bool | None`
    :   The type of the None singleton.

    `auto_ticket_assign: int | None`
    :   The type of the None singleton.

    `business_hour_id: int | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `escalate_to: int | None`
    :   The type of the None singleton.

    `group_type: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `unassigned_for: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
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

    `model_config`
    :   The type of the None singleton.

    `next: str | None`
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

    `auto_ticket_assign: int | None`
    :   Auto ticket assignment: 0=Disabled, 1=Round Robin, 2=Skill Based, 3=Load Based

    `business_hour_id: int | None`
    :   ID of the associated business hour

    `created_at: str | None`
    :   Group creation timestamp

    `description: str | None`
    :   Description of the group

    `escalate_to: int | None`
    :   User ID for escalation

    `group_type: str | None`
    :   Type of the group (e.g., support_agent_group)

    `id: int | None`
    :   Unique group ID

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the group

    `unassigned_for: str | None`
    :   Time after which escalation triggers

    `updated_at: str | None`
    :   Group last update timestamp

<a id="Role"></a>

`Role(**data: Any)`
:   A Freshdesk role
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_type: int | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `default: bool | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="RolesListResultMeta"></a>

`RolesListResultMeta(**data: Any)`
:   Metadata for roles.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | None`
    :   The type of the None singleton.

<a id="RolesSearchData"></a>

`RolesSearchData(**data: Any)`
:   Search result data for roles entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | None`
    :   Role creation timestamp

    `default: bool | None`
    :   Whether this is a default role

    `description: str | None`
    :   Description of the role

    `id: int | None`
    :   Unique role ID

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the role

    `updated_at: str | None`
    :   Role last update timestamp

<a id="SatisfactionRating"></a>

`SatisfactionRating(**data: Any)`
:   A Freshdesk satisfaction rating
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_id: int | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `feedback: str | None`
    :   The type of the None singleton.

    `group_id: int | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ratings: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `survey_id: int | None`
    :   The type of the None singleton.

    `ticket_id: int | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

    `user_id: int | None`
    :   The type of the None singleton.

<a id="SatisfactionRatingsListResultMeta"></a>

`SatisfactionRatingsListResultMeta(**data: Any)`
:   Metadata for satisfaction_ratings.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | None`
    :   The type of the None singleton.

<a id="SatisfactionRatingsSearchData"></a>

`SatisfactionRatingsSearchData(**data: Any)`
:   Search result data for satisfaction_ratings entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_id: int | None`
    :   ID of the agent

    `created_at: str | None`
    :   Rating creation timestamp

    `feedback: str | None`
    :   Feedback text

    `group_id: int | None`
    :   ID of the group

    `id: int | None`
    :   Unique satisfaction rating ID

    `model_config`
    :   The type of the None singleton.

    `ratings: dict[str, typing.Any] | None`
    :   Rating values (question_id to rating mapping)

    `survey_id: int | None`
    :   ID of the survey

    `ticket_id: int | None`
    :   ID of the ticket

    `updated_at: str | None`
    :   Rating last update timestamp

    `user_id: int | None`
    :   ID of the user (requester)

<a id="Survey"></a>

`Survey(**data: Any)`
:   A Freshdesk survey
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `questions: list[airbyte_agent_sdk.connectors.freshdesk.models.SurveyQuestionsItem] | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="SurveyQuestionsItem"></a>

`SurveyQuestionsItem(**data: Any)`
:   Nested schema for Survey.questions_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `accepted_ratings: list[int] | None`
    :   Accepted rating values

    `id: str | None`
    :   Question ID

    `label: str | None`
    :   Question label

    `model_config`
    :   The type of the None singleton.

<a id="SurveysListResultMeta"></a>

`SurveysListResultMeta(**data: Any)`
:   Metadata for surveys.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | None`
    :   The type of the None singleton.

<a id="SurveysSearchData"></a>

`SurveysSearchData(**data: Any)`
:   Search result data for surveys entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | None`
    :   Whether the survey is active

    `created_at: str | None`
    :   Survey creation timestamp

    `id: int | None`
    :   Unique survey ID

    `model_config`
    :   The type of the None singleton.

    `questions: list[typing.Any] | None`
    :   Survey questions

    `title: str | None`
    :   Title of the survey

    `updated_at: str | None`
    :   Survey last update timestamp

<a id="Ticket"></a>

`Ticket(**data: Any)`
:   A Freshdesk support ticket
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `associated_tickets_count: int | None`
    :   The type of the None singleton.

    `association_type: int | None`
    :   The type of the None singleton.

    `attachments: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `cc_emails: list[str] | None`
    :   The type of the None singleton.

    `company_id: int | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `custom_fields: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `deleted: bool | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `description_text: str | None`
    :   The type of the None singleton.

    `due_by: str | None`
    :   The type of the None singleton.

    `email_config_id: int | None`
    :   The type of the None singleton.

    `form_id: int | None`
    :   The type of the None singleton.

    `fr_due_by: str | None`
    :   The type of the None singleton.

    `fr_escalated: bool | None`
    :   The type of the None singleton.

    `fwd_emails: list[str] | None`
    :   The type of the None singleton.

    `group_id: int | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `is_escalated: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `nr_due_by: str | None`
    :   The type of the None singleton.

    `nr_escalated: bool | None`
    :   The type of the None singleton.

    `priority: int | None`
    :   The type of the None singleton.

    `product_id: int | None`
    :   The type of the None singleton.

    `reply_cc_emails: list[str] | None`
    :   The type of the None singleton.

    `requester_id: int | None`
    :   The type of the None singleton.

    `responder_id: int | None`
    :   The type of the None singleton.

    `source: int | None`
    :   The type of the None singleton.

    `source_additional_info: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `spam: bool | None`
    :   The type of the None singleton.

    `status: int | None`
    :   The type of the None singleton.

    `structured_description: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `subject: str | None`
    :   The type of the None singleton.

    `support_email: str | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

    `ticket_bcc_emails: list[str] | None`
    :   The type of the None singleton.

    `ticket_cc_emails: list[str] | None`
    :   The type of the None singleton.

    `to_emails: list[str] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="TicketField"></a>

`TicketField(**data: Any)`
:   A Freshdesk ticket field definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `choices: typing.Any | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `customers_can_edit: bool | None`
    :   The type of the None singleton.

    `customers_can_filter: bool | None`
    :   The type of the None singleton.

    `default: bool | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `displayed_to_customers: bool | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `label: str | None`
    :   The type of the None singleton.

    `label_for_customers: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `portal_cc: bool | None`
    :   The type of the None singleton.

    `portal_cc_to: str | None`
    :   The type of the None singleton.

    `position: int | None`
    :   The type of the None singleton.

    `required_for_agents: bool | None`
    :   The type of the None singleton.

    `required_for_closure: bool | None`
    :   The type of the None singleton.

    `required_for_customers: bool | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="TicketFieldsListResultMeta"></a>

`TicketFieldsListResultMeta(**data: Any)`
:   Metadata for ticket_fields.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | None`
    :   The type of the None singleton.

<a id="TicketFieldsSearchData"></a>

`TicketFieldsSearchData(**data: Any)`
:   Search result data for ticket_fields entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `choices: dict[str, typing.Any] | None`
    :   Available choices for dropdown fields

    `created_at: str | None`
    :   Field creation timestamp

    `customers_can_edit: bool | None`
    :   Whether customers can edit this field

    `default: bool | None`
    :   Whether this is a default (non-custom) field

    `description: str | None`
    :   Description of the field

    `displayed_to_customers: bool | None`
    :   Whether the field is displayed to customers

    `id: int | None`
    :   Unique ticket field ID

    `label: str | None`
    :   Display label for agents

    `label_for_customers: str | None`
    :   Display label in the customer portal

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the field

    `portal_cc: bool | None`
    :   Whether CC is enabled in the portal

    `portal_cc_to: str | None`
    :   CC recipients scope (all or company)

    `position: int | None`
    :   Position of the field in the form

    `required_for_agents: bool | None`
    :   Whether the field is required for agents

    `required_for_closure: bool | None`
    :   Whether the field is required for ticket closure

    `required_for_customers: bool | None`
    :   Whether the field is required for customers

    `type_: str | None`
    :   Field type (e.g., custom_dropdown, custom_text)

    `updated_at: str | None`
    :   Field last update timestamp

<a id="TicketsListResultMeta"></a>

`TicketsListResultMeta(**data: Any)`
:   Metadata for tickets.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | None`
    :   The type of the None singleton.

<a id="TicketsSearchData"></a>

`TicketsSearchData(**data: Any)`
:   Search result data for tickets entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `associated_tickets_count: int | None`
    :   Number of associated tickets

    `association_type: int | None`
    :   Association type for parent/child tickets

    `cc_emails: list[typing.Any] | None`
    :   CC email addresses

    `company_id: int | None`
    :   Company ID of the requester

    `created_at: str | None`
    :   Ticket creation timestamp

    `custom_fields: dict[str, typing.Any] | None`
    :   Custom fields associated with the ticket

    `description: str | None`
    :   HTML content of the ticket

    `description_text: str | None`
    :   Plain text content of the ticket

    `due_by: str | None`
    :   Resolution due by timestamp

    `email_config_id: int | None`
    :   ID of the email config used for the ticket

    `fr_due_by: str | None`
    :   First response due by timestamp

    `fr_escalated: bool | None`
    :   Whether the first response time was breached

    `fwd_emails: list[typing.Any] | None`
    :   Forwarded email addresses

    `group_id: int | None`
    :   ID of the group to which the ticket is assigned

    `id: int | None`
    :   Unique ticket ID

    `is_escalated: bool | None`
    :   Whether the ticket is escalated

    `model_config`
    :   The type of the None singleton.

    `nr_due_by: str | None`
    :   Next response due by timestamp

    `nr_escalated: bool | None`
    :   Whether the next response time was breached

    `priority: int | None`
    :   Priority: 1=Low, 2=Medium, 3=High, 4=Urgent

    `product_id: int | None`
    :   ID of the product associated with the ticket

    `reply_cc_emails: list[typing.Any] | None`
    :   Reply CC email addresses

    `requester: dict[str, typing.Any] | None`
    :   Requester details including name, email, and contact info

    `requester_id: int | None`
    :   ID of the requester

    `responder_id: int | None`
    :   ID of the agent to whom the ticket is assigned

    `source: int | None`
    :   Source: 1=Email, 2=Portal, 3=Phone, 7=Chat, 9=Feedback Widget, 10=Outbound Email

    `spam: bool | None`
    :   Whether the ticket is marked as spam

    `stats: dict[str, typing.Any] | None`
    :   Ticket statistics including response and resolution times

    `status: int | None`
    :   Status: 2=Open, 3=Pending, 4=Resolved, 5=Closed

    `subject: str | None`
    :   Subject of the ticket

    `tags: list[typing.Any] | None`
    :   Tags associated with the ticket

    `ticket_cc_emails: list[typing.Any] | None`
    :   Ticket CC email addresses

    `to_emails: list[typing.Any] | None`
    :   To email addresses

    `type_: str | None`
    :   Ticket type

    `updated_at: str | None`
    :   Ticket last update timestamp

<a id="TimeEntriesListResultMeta"></a>

`TimeEntriesListResultMeta(**data: Any)`
:   Metadata for time_entries.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | None`
    :   The type of the None singleton.

<a id="TimeEntriesSearchData"></a>

`TimeEntriesSearchData(**data: Any)`
:   Search result data for time_entries entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_id: int | None`
    :   ID of the agent

    `billable: bool | None`
    :   Whether the time entry is billable

    `company_id: int | None`
    :   ID of the associated company

    `created_at: str | None`
    :   Time entry creation timestamp

    `executed_at: str | None`
    :   Execution timestamp

    `id: int | None`
    :   Unique time entry ID

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   Description of the time entry

    `start_time: str | None`
    :   Start time of the timer

    `ticket_id: int | None`
    :   ID of the associated ticket

    `time_spent: str | None`
    :   Time spent in hh:mm format

    `timer_running: bool | None`
    :   Whether the timer is running

    `updated_at: str | None`
    :   Time entry last update timestamp

<a id="TimeEntry"></a>

`TimeEntry(**data: Any)`
:   A Freshdesk time entry
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_id: int | None`
    :   The type of the None singleton.

    `billable: bool | None`
    :   The type of the None singleton.

    `company_id: int | None`
    :   The type of the None singleton.

    `created_at: str | None`
    :   The type of the None singleton.

    `executed_at: str | None`
    :   The type of the None singleton.

    `id: int`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `note: str | None`
    :   The type of the None singleton.

    `start_time: str | None`
    :   The type of the None singleton.

    `ticket_id: int | None`
    :   The type of the None singleton.

    `time_spent: str | None`
    :   The type of the None singleton.

    `time_spent_in_seconds: int | None`
    :   The type of the None singleton.

    `timer_running: bool | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.