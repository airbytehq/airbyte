---
id: airbyte_agent_sdk-connectors-salesforce-models
title: airbyte_agent_sdk.connectors.salesforce.models
---

Module airbyte_agent_sdk.connectors.salesforce.models
=====================================================
Pydantic models for salesforce connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="Account"></a>

`Account(**data: Any)`
:   Salesforce Account object - uses FIELDS(STANDARD) so all standard fields are returned
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.salesforce.models.AccountAttributes | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

<a id="AccountAttributes"></a>

`AccountAttributes(**data: Any)`
:   Nested schema for Account.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="AccountQueryResult"></a>

`AccountQueryResult(**data: Any)`
:   SOQL query result for accounts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

    `records: list[airbyte_agent_sdk.connectors.salesforce.models.Account] | Any`
    :   The type of the None singleton.

    `total_size: int | Any`
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

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
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

    `account_source: str | None`
    :   Source of the account record (e.g., Web, Referral)

    `billing_address: dict[str, typing.Any] | None`
    :   Complete billing address as a compound field

    `billing_city: str | None`
    :   City portion of the billing address

    `billing_country: str | None`
    :   Country portion of the billing address

    `billing_postal_code: str | None`
    :   Postal code portion of the billing address

    `billing_state: str | None`
    :   State or province portion of the billing address

    `billing_street: str | None`
    :   Street address portion of the billing address

    `created_by_id: str | None`
    :   ID of the user who created this account

    `created_date: str | None`
    :   Date and time when the account was created

    `description: str | None`
    :   Text description of the account

    `id: str`
    :   Unique identifier for the account record

    `industry: str | None`
    :   Primary business industry of the account

    `is_deleted: bool | None`
    :   Whether the account has been moved to the Recycle Bin

    `last_activity_date: str | None`
    :   Date of the last activity associated with this account

    `last_modified_by_id: str | None`
    :   ID of the user who last modified this account

    `last_modified_date: str | None`
    :   Date and time when the account was last modified

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the account or company

    `number_of_employees: int | None`
    :   Number of employees at the account

    `owner_id: str | None`
    :   ID of the user who owns this account

    `parent_id: str | None`
    :   ID of the parent account, if this is a subsidiary

    `phone: str | None`
    :   Primary phone number for the account

    `shipping_address: dict[str, typing.Any] | None`
    :   Complete shipping address as a compound field

    `shipping_city: str | None`
    :   City portion of the shipping address

    `shipping_country: str | None`
    :   Country portion of the shipping address

    `shipping_postal_code: str | None`
    :   Postal code portion of the shipping address

    `shipping_state: str | None`
    :   State or province portion of the shipping address

    `shipping_street: str | None`
    :   Street address portion of the shipping address

    `system_modstamp: str | None`
    :   System timestamp when the record was last modified

    `type_: str | None`
    :   Type of account (e.g., Customer, Partner, Competitor)

    `website: str | None`
    :   Website URL for the account

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

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[AccountsSearchData]
    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[ContactsSearchData]
    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[LeadsSearchData]
    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[OpportunitiesSearchData]
    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult[TasksSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchMeta`
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

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ContactsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[LeadsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="LeadsSearchResult"></a>

`LeadsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[OpportunitiesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OpportunitiesSearchResult"></a>

`OpportunitiesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TasksSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TasksSearchResult"></a>

`TasksSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Attachment"></a>

`Attachment(**data: Any)`
:   Salesforce Attachment object - legacy file attachment on a record
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.salesforce.models.AttachmentAttributes | Any`
    :   The type of the None singleton.

    `body_length: int | Any`
    :   The type of the None singleton.

    `content_type: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `parent_id: str | Any`
    :   The type of the None singleton.

<a id="AttachmentAttributes"></a>

`AttachmentAttributes(**data: Any)`
:   Nested schema for Attachment.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="AttachmentQueryResult"></a>

`AttachmentQueryResult(**data: Any)`
:   SOQL query result for attachments
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

    `records: list[airbyte_agent_sdk.connectors.salesforce.models.Attachment] | Any`
    :   The type of the None singleton.

    `total_size: int | Any`
    :   The type of the None singleton.

<a id="AttachmentsListResultMeta"></a>

`AttachmentsListResultMeta(**data: Any)`
:   Metadata for attachments.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

<a id="Campaign"></a>

`Campaign(**data: Any)`
:   Salesforce Campaign object - uses FIELDS(STANDARD) so all standard fields are returned
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.salesforce.models.CampaignAttributes | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

<a id="CampaignAttributes"></a>

`CampaignAttributes(**data: Any)`
:   Nested schema for Campaign.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="CampaignQueryResult"></a>

`CampaignQueryResult(**data: Any)`
:   SOQL query result for campaigns
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

    `records: list[airbyte_agent_sdk.connectors.salesforce.models.Campaign] | Any`
    :   The type of the None singleton.

    `total_size: int | Any`
    :   The type of the None singleton.

<a id="CampaignsListResultMeta"></a>

`CampaignsListResultMeta(**data: Any)`
:   Metadata for campaigns.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

<a id="Case"></a>

`Case(**data: Any)`
:   Salesforce Case object - uses FIELDS(STANDARD) so all standard fields are returned
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.salesforce.models.CaseAttributes | Any`
    :   The type of the None singleton.

    `case_number: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `subject: str | Any`
    :   The type of the None singleton.

<a id="CaseAttributes"></a>

`CaseAttributes(**data: Any)`
:   Nested schema for Case.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="CaseQueryResult"></a>

`CaseQueryResult(**data: Any)`
:   SOQL query result for cases
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

    `records: list[airbyte_agent_sdk.connectors.salesforce.models.Case] | Any`
    :   The type of the None singleton.

    `total_size: int | Any`
    :   The type of the None singleton.

<a id="CasesListResultMeta"></a>

`CasesListResultMeta(**data: Any)`
:   Metadata for cases.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

<a id="Contact"></a>

`Contact(**data: Any)`
:   Salesforce Contact object - uses FIELDS(STANDARD) so all standard fields are returned
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.salesforce.models.ContactAttributes | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

<a id="ContactAttributes"></a>

`ContactAttributes(**data: Any)`
:   Nested schema for Contact.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="ContactQueryResult"></a>

`ContactQueryResult(**data: Any)`
:   SOQL query result for contacts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

    `records: list[airbyte_agent_sdk.connectors.salesforce.models.Contact] | Any`
    :   The type of the None singleton.

    `total_size: int | Any`
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

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
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

    `account_id: str | None`
    :   ID of the account this contact is associated with

    `created_by_id: str | None`
    :   ID of the user who created this contact

    `created_date: str | None`
    :   Date and time when the contact was created

    `department: str | None`
    :   Department within the account where the contact works

    `email: str | None`
    :   Email address of the contact

    `first_name: str | None`
    :   First name of the contact

    `id: str`
    :   Unique identifier for the contact record

    `is_deleted: bool | None`
    :   Whether the contact has been moved to the Recycle Bin

    `last_activity_date: str | None`
    :   Date of the last activity associated with this contact

    `last_modified_by_id: str | None`
    :   ID of the user who last modified this contact

    `last_modified_date: str | None`
    :   Date and time when the contact was last modified

    `last_name: str | None`
    :   Last name of the contact

    `lead_source: str | None`
    :   Source from which this contact originated

    `mailing_address: dict[str, typing.Any] | None`
    :   Complete mailing address as a compound field

    `mailing_city: str | None`
    :   City portion of the mailing address

    `mailing_country: str | None`
    :   Country portion of the mailing address

    `mailing_postal_code: str | None`
    :   Postal code portion of the mailing address

    `mailing_state: str | None`
    :   State or province portion of the mailing address

    `mailing_street: str | None`
    :   Street address portion of the mailing address

    `mobile_phone: str | None`
    :   Mobile phone number of the contact

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Full name of the contact (read-only, concatenation of first and last name)

    `owner_id: str | None`
    :   ID of the user who owns this contact

    `phone: str | None`
    :   Business phone number of the contact

    `reports_to_id: str | None`
    :   ID of the contact this contact reports to

    `system_modstamp: str | None`
    :   System timestamp when the record was last modified

    `title: str | None`
    :   Job title of the contact

<a id="ContentVersion"></a>

`ContentVersion(**data: Any)`
:   Salesforce ContentVersion object - represents a file version in Salesforce Files
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.salesforce.models.ContentVersionAttributes | Any`
    :   The type of the None singleton.

    `content_document_id: str | Any`
    :   The type of the None singleton.

    `content_size: int | Any`
    :   The type of the None singleton.

    `file_extension: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_latest: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `version_number: str | Any`
    :   The type of the None singleton.

<a id="ContentVersionAttributes"></a>

`ContentVersionAttributes(**data: Any)`
:   Nested schema for ContentVersion.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="ContentVersionQueryResult"></a>

`ContentVersionQueryResult(**data: Any)`
:   SOQL query result for content versions
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

    `records: list[airbyte_agent_sdk.connectors.salesforce.models.ContentVersion] | Any`
    :   The type of the None singleton.

    `total_size: int | Any`
    :   The type of the None singleton.

<a id="ContentVersionsListResultMeta"></a>

`ContentVersionsListResultMeta(**data: Any)`
:   Metadata for content_versions.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

<a id="Event"></a>

`Event(**data: Any)`
:   Salesforce Event object - uses FIELDS(STANDARD) so all standard fields are returned
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.salesforce.models.EventAttributes | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `subject: str | Any`
    :   The type of the None singleton.

<a id="EventAttributes"></a>

`EventAttributes(**data: Any)`
:   Nested schema for Event.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="EventQueryResult"></a>

`EventQueryResult(**data: Any)`
:   SOQL query result for events
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

    `records: list[airbyte_agent_sdk.connectors.salesforce.models.Event] | Any`
    :   The type of the None singleton.

    `total_size: int | Any`
    :   The type of the None singleton.

<a id="EventsListResultMeta"></a>

`EventsListResultMeta(**data: Any)`
:   Metadata for events.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

<a id="Lead"></a>

`Lead(**data: Any)`
:   Salesforce Lead object - uses FIELDS(STANDARD) so all standard fields are returned
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.salesforce.models.LeadAttributes | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

<a id="LeadAttributes"></a>

`LeadAttributes(**data: Any)`
:   Nested schema for Lead.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="LeadQueryResult"></a>

`LeadQueryResult(**data: Any)`
:   SOQL query result for leads
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

    `records: list[airbyte_agent_sdk.connectors.salesforce.models.Lead] | Any`
    :   The type of the None singleton.

    `total_size: int | Any`
    :   The type of the None singleton.

<a id="LeadsListResultMeta"></a>

`LeadsListResultMeta(**data: Any)`
:   Metadata for leads.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

<a id="LeadsSearchData"></a>

`LeadsSearchData(**data: Any)`
:   Search result data for leads entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: dict[str, typing.Any] | None`
    :   Complete address as a compound field

    `city: str | None`
    :   City portion of the address

    `company: str | None`
    :   Company or organization the lead works for

    `converted_account_id: str | None`
    :   ID of the account created when lead was converted

    `converted_contact_id: str | None`
    :   ID of the contact created when lead was converted

    `converted_date: str | None`
    :   Date when the lead was converted

    `converted_opportunity_id: str | None`
    :   ID of the opportunity created when lead was converted

    `country: str | None`
    :   Country portion of the address

    `created_by_id: str | None`
    :   ID of the user who created this lead

    `created_date: str | None`
    :   Date and time when the lead was created

    `email: str | None`
    :   Email address of the lead

    `first_name: str | None`
    :   First name of the lead

    `id: str`
    :   Unique identifier for the lead record

    `industry: str | None`
    :   Industry the lead's company operates in

    `is_converted: bool | None`
    :   Whether the lead has been converted to an account, contact, and opportunity

    `is_deleted: bool | None`
    :   Whether the lead has been moved to the Recycle Bin

    `last_activity_date: str | None`
    :   Date of the last activity associated with this lead

    `last_modified_by_id: str | None`
    :   ID of the user who last modified this lead

    `last_modified_date: str | None`
    :   Date and time when the lead was last modified

    `last_name: str | None`
    :   Last name of the lead

    `lead_source: str | None`
    :   Source from which this lead originated

    `mobile_phone: str | None`
    :   Mobile phone number of the lead

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Full name of the lead (read-only, concatenation of first and last name)

    `number_of_employees: int | None`
    :   Number of employees at the lead's company

    `owner_id: str | None`
    :   ID of the user who owns this lead

    `phone: str | None`
    :   Phone number of the lead

    `postal_code: str | None`
    :   Postal code portion of the address

    `rating: str | None`
    :   Rating of the lead (e.g., Hot, Warm, Cold)

    `state: str | None`
    :   State or province portion of the address

    `status: str | None`
    :   Current status of the lead in the sales process

    `street: str | None`
    :   Street address portion of the address

    `system_modstamp: str | None`
    :   System timestamp when the record was last modified

    `title: str | None`
    :   Job title of the lead

    `website: str | None`
    :   Website URL for the lead's company

<a id="Note"></a>

`Note(**data: Any)`
:   Salesforce Note object - uses FIELDS(STANDARD) so all standard fields are returned
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.salesforce.models.NoteAttributes | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

<a id="NoteAttributes"></a>

`NoteAttributes(**data: Any)`
:   Nested schema for Note.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="NoteQueryResult"></a>

`NoteQueryResult(**data: Any)`
:   SOQL query result for notes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

    `records: list[airbyte_agent_sdk.connectors.salesforce.models.Note] | Any`
    :   The type of the None singleton.

    `total_size: int | Any`
    :   The type of the None singleton.

<a id="NotesListResultMeta"></a>

`NotesListResultMeta(**data: Any)`
:   Metadata for notes.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

<a id="OpportunitiesListResultMeta"></a>

`OpportunitiesListResultMeta(**data: Any)`
:   Metadata for opportunities.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

<a id="OpportunitiesSearchData"></a>

`OpportunitiesSearchData(**data: Any)`
:   Search result data for opportunities entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   ID of the account associated with this opportunity

    `amount: float | None`
    :   Estimated total sale amount

    `campaign_id: str | None`
    :   ID of the campaign that generated this opportunity

    `close_date: str | None`
    :   Expected close date for the opportunity

    `contact_id: str | None`
    :   ID of the primary contact for this opportunity

    `created_by_id: str | None`
    :   ID of the user who created this opportunity

    `created_date: str | None`
    :   Date and time when the opportunity was created

    `description: str | None`
    :   Text description of the opportunity

    `expected_revenue: float | None`
    :   Expected revenue based on amount and probability

    `forecast_category: str | None`
    :   Forecast category for this opportunity

    `forecast_category_name: str | None`
    :   Name of the forecast category

    `id: str`
    :   Unique identifier for the opportunity record

    `is_closed: bool | None`
    :   Whether the opportunity is closed

    `is_deleted: bool | None`
    :   Whether the opportunity has been moved to the Recycle Bin

    `is_won: bool | None`
    :   Whether the opportunity was won

    `last_activity_date: str | None`
    :   Date of the last activity associated with this opportunity

    `last_modified_by_id: str | None`
    :   ID of the user who last modified this opportunity

    `last_modified_date: str | None`
    :   Date and time when the opportunity was last modified

    `lead_source: str | None`
    :   Source from which this opportunity originated

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the opportunity

    `next_step: str | None`
    :   Description of the next step in closing the opportunity

    `owner_id: str | None`
    :   ID of the user who owns this opportunity

    `probability: float | None`
    :   Likelihood of closing the opportunity (percentage)

    `stage_name: str | None`
    :   Current stage of the opportunity in the sales process

    `system_modstamp: str | None`
    :   System timestamp when the record was last modified

    `type_: str | None`
    :   Type of opportunity (e.g., New Business, Existing Business)

<a id="Opportunity"></a>

`Opportunity(**data: Any)`
:   Salesforce Opportunity object - uses FIELDS(STANDARD) so all standard fields are returned
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.salesforce.models.OpportunityAttributes | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

<a id="OpportunityAttributes"></a>

`OpportunityAttributes(**data: Any)`
:   Nested schema for Opportunity.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="OpportunityQueryResult"></a>

`OpportunityQueryResult(**data: Any)`
:   SOQL query result for opportunities
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

    `records: list[airbyte_agent_sdk.connectors.salesforce.models.Opportunity] | Any`
    :   The type of the None singleton.

    `total_size: int | Any`
    :   The type of the None singleton.

<a id="QueryListResultMeta"></a>

`QueryListResultMeta(**data: Any)`
:   Metadata for query.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

<a id="QueryResult"></a>

`QueryResult(**data: Any)`
:   Generic SOQL query result
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

    `records: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `total_size: int | Any`
    :   The type of the None singleton.

<a id="Report"></a>

`Report(**data: Any)`
:   Salesforce Report metadata from the Analytics API
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `describe_url: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `instances_url: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `url: str | Any | None`
    :   The type of the None singleton.

<a id="ReportResults"></a>

`ReportResults(**data: Any)`
:   Executed report results including data rows, aggregates, and metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `all_data: bool | Any | None`
    :   The type of the None singleton.

    `attributes: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `fact_map: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `groupings_across: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `groupings_down: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `has_detail_rows: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `report_extended_metadata: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `report_metadata: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="SObject"></a>

`SObject(**data: Any)`
:   Salesforce sObject metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `createable: bool | Any | None`
    :   The type of the None singleton.

    `custom: bool | Any | None`
    :   The type of the None singleton.

    `deletable: bool | Any | None`
    :   The type of the None singleton.

    `key_prefix: str | Any | None`
    :   The type of the None singleton.

    `label: str | Any | None`
    :   The type of the None singleton.

    `label_plural: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `queryable: bool | Any | None`
    :   The type of the None singleton.

    `searchable: bool | Any | None`
    :   The type of the None singleton.

    `updateable: bool | Any | None`
    :   The type of the None singleton.

    `urls: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="SObjectsResponse"></a>

`SObjectsResponse(**data: Any)`
:   Response from the sobjects endpoint listing all available Salesforce objects
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `encoding: str | Any | None`
    :   The type of the None singleton.

    `max_batch_size: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `sobjects: list[airbyte_agent_sdk.connectors.salesforce.models.SObject] | Any`
    :   The type of the None singleton.

<a id="SalesforceAuthConfig"></a>

`SalesforceAuthConfig(**data: Any)`
:   Salesforce OAuth 2.0
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `client_id: str | None`
    :   Connected App Consumer Key

    `client_secret: str | None`
    :   Connected App Consumer Secret

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str`
    :   OAuth refresh token for automatic token renewal

<a id="SalesforceCheckResult"></a>

`SalesforceCheckResult(**data: Any)`
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

<a id="SalesforceExecuteResult"></a>

`SalesforceExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult[SearchResult]
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult[list[Report]]
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult[list[SObject]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="SalesforceExecuteResultWithMeta"></a>

`SalesforceExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Account], AccountsListResultMeta]
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Attachment], AttachmentsListResultMeta]
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Case], CasesListResultMeta]
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Contact], ContactsListResultMeta]
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[ContentVersion], ContentVersionsListResultMeta]
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Event], EventsListResultMeta]
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Lead], LeadsListResultMeta]
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Note], NotesListResultMeta]
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Opportunity], OpportunitiesListResultMeta]
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[Task], TasksListResultMeta]
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta[list[dict[str, Any]], QueryListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`SalesforceExecuteResultWithMeta[list[Account], AccountsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
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

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SalesforceExecuteResultWithMeta[list[Attachment], AttachmentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AttachmentsListResult"></a>

`AttachmentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SalesforceExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CampaignsListResult"></a>

`CampaignsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SalesforceExecuteResultWithMeta[list[Case], CasesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CasesListResult"></a>

`CasesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SalesforceExecuteResultWithMeta[list[Contact], ContactsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
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

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SalesforceExecuteResultWithMeta[list[ContentVersion], ContentVersionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ContentVersionsListResult"></a>

`ContentVersionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SalesforceExecuteResultWithMeta[list[Event], EventsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="EventsListResult"></a>

`EventsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SalesforceExecuteResultWithMeta[list[Lead], LeadsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="LeadsListResult"></a>

`LeadsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SalesforceExecuteResultWithMeta[list[Note], NotesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="NotesListResult"></a>

`NotesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SalesforceExecuteResultWithMeta[list[Opportunity], OpportunitiesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OpportunitiesListResult"></a>

`OpportunitiesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SalesforceExecuteResultWithMeta[list[Task], TasksListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TasksListResult"></a>

`TasksListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SalesforceExecuteResultWithMeta[list[dict[str, Any]], QueryListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="QueryListResult"></a>

`QueryListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SalesforceExecuteResult[SearchResult](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AccountsApiSearchResult"></a>

`AccountsApiSearchResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ContactsApiSearchResult"></a>

`ContactsApiSearchResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="LeadsApiSearchResult"></a>

`LeadsApiSearchResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OpportunitiesApiSearchResult"></a>

`OpportunitiesApiSearchResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TasksApiSearchResult"></a>

`TasksApiSearchResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="EventsApiSearchResult"></a>

`EventsApiSearchResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CampaignsApiSearchResult"></a>

`CampaignsApiSearchResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CasesApiSearchResult"></a>

`CasesApiSearchResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="NotesApiSearchResult"></a>

`NotesApiSearchResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SalesforceExecuteResult[list[Report]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ReportsListResult"></a>

`ReportsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SalesforceExecuteResult[list[SObject]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SobjectsListResult"></a>

`SobjectsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.salesforce.models.SalesforceExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SearchResult"></a>

`SearchResult(**data: Any)`
:   SOSL search result
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `search_records: list[airbyte_agent_sdk.connectors.salesforce.models.SearchResultSearchrecordsItem] | Any`
    :   The type of the None singleton.

<a id="SearchResultSearchrecordsItem"></a>

`SearchResultSearchrecordsItem(**data: Any)`
:   Nested schema for SearchResult.searchRecords_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.salesforce.models.SearchResultSearchrecordsItemAttributes | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SearchResultSearchrecordsItemAttributes"></a>

`SearchResultSearchrecordsItemAttributes(**data: Any)`
:   Nested schema for SearchResultSearchrecordsItem.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="Task"></a>

`Task(**data: Any)`
:   Salesforce Task object - uses FIELDS(STANDARD) so all standard fields are returned
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.salesforce.models.TaskAttributes | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `subject: str | Any`
    :   The type of the None singleton.

<a id="TaskAttributes"></a>

`TaskAttributes(**data: Any)`
:   Nested schema for Task.attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="TaskQueryResult"></a>

`TaskQueryResult(**data: Any)`
:   SOQL query result for tasks
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

    `records: list[airbyte_agent_sdk.connectors.salesforce.models.Task] | Any`
    :   The type of the None singleton.

    `total_size: int | Any`
    :   The type of the None singleton.

<a id="TasksListResultMeta"></a>

`TasksListResultMeta(**data: Any)`
:   Metadata for tasks.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `done: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_records_url: str | Any`
    :   The type of the None singleton.

<a id="TasksSearchData"></a>

`TasksSearchData(**data: Any)`
:   Search result data for tasks entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `account_id: str | None`
    :   ID of the account associated with this task

    `activity_date: str | None`
    :   Due date for the task

    `call_disposition: str | None`
    :   Result of the call, if this task represents a call

    `call_duration_in_seconds: int | None`
    :   Duration of the call in seconds

    `call_type: str | None`
    :   Type of call (Inbound, Outbound, Internal)

    `completed_date_time: str | None`
    :   Date and time when the task was completed

    `created_by_id: str | None`
    :   ID of the user who created this task

    `created_date: str | None`
    :   Date and time when the task was created

    `description: str | None`
    :   Text description or notes about the task

    `id: str`
    :   Unique identifier for the task record

    `is_closed: bool | None`
    :   Whether the task has been completed

    `is_deleted: bool | None`
    :   Whether the task has been moved to the Recycle Bin

    `is_high_priority: bool | None`
    :   Whether the task is marked as high priority

    `last_modified_by_id: str | None`
    :   ID of the user who last modified this task

    `last_modified_date: str | None`
    :   Date and time when the task was last modified

    `model_config`
    :   The type of the None singleton.

    `owner_id: str | None`
    :   ID of the user who owns this task

    `priority: str | None`
    :   Priority level of the task (High, Normal, Low)

    `status: str | None`
    :   Current status of the task

    `subject: str | None`
    :   Subject or title of the task

    `system_modstamp: str | None`
    :   System timestamp when the record was last modified

    `task_subtype: str | None`
    :   Subtype of the task (e.g., Call, Email, Task)

    `type_: str | None`
    :   Type of task

    `what_id: str | None`
    :   ID of the related object (Account, Opportunity, etc.)

    `who_id: str | None`
    :   ID of the related person (Contact or Lead)