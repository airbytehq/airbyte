---
id: airbyte_agent_sdk-connectors-sendgrid-models
title: airbyte_agent_sdk.connectors.sendgrid.models
---

Module airbyte_agent_sdk.connectors.sendgrid.models
===================================================
Pydantic models for sendgrid connector.

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

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[BlocksSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[BouncesSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[CampaignsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[ContactsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[GlobalSuppressionsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[InvalidEmailsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[ListsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SegmentsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SinglesendStatsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SinglesendsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SuppressionGroupMembersSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[SuppressionGroupsSearchData]
    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult[TemplatesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[BlocksSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BlocksSearchResult"></a>

`BlocksSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[BouncesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BouncesSearchResult"></a>

`BouncesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CampaignsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CampaignsSearchResult"></a>

`CampaignsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ContactsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[GlobalSuppressionsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="GlobalSuppressionsSearchResult"></a>

`GlobalSuppressionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[InvalidEmailsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="InvalidEmailsSearchResult"></a>

`InvalidEmailsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ListsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ListsSearchResult"></a>

`ListsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SegmentsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SegmentsSearchResult"></a>

`SegmentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SinglesendStatsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SinglesendStatsSearchResult"></a>

`SinglesendStatsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SinglesendsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SinglesendsSearchResult"></a>

`SinglesendsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SuppressionGroupMembersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersSearchResult"></a>

`SuppressionGroupMembersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SuppressionGroupsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SuppressionGroupsSearchResult"></a>

`SuppressionGroupsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TemplatesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TemplatesSearchResult"></a>

`TemplatesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Block"></a>

`Block(**data: Any)`
:   A blocked email record
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: int | Any`
    :   The type of the None singleton.

    `email: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reason: str | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

<a id="BlocksListResultMeta"></a>

`BlocksListResultMeta(**data: Any)`
:   Metadata for blocks.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="BlocksSearchData"></a>

`BlocksSearchData(**data: Any)`
:   Search result data for blocks entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: int | None`
    :   Unix timestamp when the block occurred

    `email: str | None`
    :   The blocked email address

    `model_config`
    :   The type of the None singleton.

    `reason: str | None`
    :   The reason for the block

    `status: str | None`
    :   The status code for the block

<a id="Bounce"></a>

`Bounce(**data: Any)`
:   A bounced email record
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: int | Any`
    :   The type of the None singleton.

    `email: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reason: str | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

<a id="BouncesListResultMeta"></a>

`BouncesListResultMeta(**data: Any)`
:   Metadata for bounces.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="BouncesSearchData"></a>

`BouncesSearchData(**data: Any)`
:   Search result data for bounces entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: int | None`
    :   Unix timestamp when the bounce occurred

    `email: str | None`
    :   The email address that bounced

    `model_config`
    :   The type of the None singleton.

    `reason: str | None`
    :   The reason for the bounce

    `status: str | None`
    :   The enhanced status code for the bounce

<a id="Campaign"></a>

`Campaign(**data: Any)`
:   A SendGrid marketing campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channels: list[str] | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_abtest: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

<a id="CampaignsList"></a>

`CampaignsList(**data: Any)`
:   Response containing a list of campaigns
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `metadata: airbyte_agent_sdk.connectors.sendgrid.models.CampaignsListMetadata | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `result: list[airbyte_agent_sdk.connectors.sendgrid.models.Campaign] | Any`
    :   The type of the None singleton.

<a id="CampaignsListMetadata"></a>

`CampaignsListMetadata(**data: Any)`
:   Nested schema for CampaignsList._metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
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

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="CampaignsSearchData"></a>

`CampaignsSearchData(**data: Any)`
:   Search result data for campaigns entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `channels: list[typing.Any] | None`
    :   Channels for this campaign

    `created_at: str | None`
    :   When the campaign was created

    `id: str | None`
    :   Unique campaign identifier

    `is_abtest: bool | None`
    :   Whether this campaign is an A/B test

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Campaign name

    `status: str | None`
    :   Campaign status

    `updated_at: str | None`
    :   When the campaign was last updated

<a id="Contact"></a>

`Contact(**data: Any)`
:   A SendGrid marketing contact
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address_line_1: str | Any | None`
    :   The type of the None singleton.

    `address_line_2: str | Any | None`
    :   The type of the None singleton.

    `alternate_emails: list[str] | Any | None`
    :   The type of the None singleton.

    `city: str | Any | None`
    :   The type of the None singleton.

    `country: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `custom_fields: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `facebook: str | Any | None`
    :   The type of the None singleton.

    `first_name: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `last_name: str | Any | None`
    :   The type of the None singleton.

    `line: str | Any | None`
    :   The type of the None singleton.

    `list_ids: list[str] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `phone_number: str | Any | None`
    :   The type of the None singleton.

    `postal_code: str | Any | None`
    :   The type of the None singleton.

    `segment_ids: list[str] | Any | None`
    :   The type of the None singleton.

    `state_province_region: str | Any | None`
    :   The type of the None singleton.

    `unique_name: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `whatsapp: str | Any | None`
    :   The type of the None singleton.

<a id="ContactsList"></a>

`ContactsList(**data: Any)`
:   Response containing a list of contacts
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `contact_count: int | Any`
    :   The type of the None singleton.

    `metadata: airbyte_agent_sdk.connectors.sendgrid.models.ContactsListMetadata | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `result: list[airbyte_agent_sdk.connectors.sendgrid.models.Contact] | Any`
    :   The type of the None singleton.

<a id="ContactsListMetadata"></a>

`ContactsListMetadata(**data: Any)`
:   Nested schema for ContactsList._metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
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

    `contact_count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
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

    `address_line_1: str | None`
    :   Address line 1

    `address_line_2: str | None`
    :   Address line 2

    `alternate_emails: list[typing.Any] | None`
    :   Alternate email addresses

    `city: str | None`
    :   City

    `contact_id: str | None`
    :   Unique contact identifier used by Airbyte

    `country: str | None`
    :   Country

    `created_at: str | None`
    :   When the contact was created

    `custom_fields: dict[str, typing.Any] | None`
    :   Custom field values

    `email: str | None`
    :   Contact email address

    `facebook: str | None`
    :   Facebook ID

    `first_name: str | None`
    :   Contact first name

    `last_name: str | None`
    :   Contact last name

    `line: str | None`
    :   LINE ID

    `list_ids: list[typing.Any] | None`
    :   IDs of lists the contact belongs to

    `model_config`
    :   The type of the None singleton.

    `phone_number: str | None`
    :   Phone number

    `postal_code: str | None`
    :   Postal code

    `state_province_region: str | None`
    :   State, province, or region

    `unique_name: str | None`
    :   Unique name for the contact

    `updated_at: str | None`
    :   When the contact was last updated

    `whatsapp: str | None`
    :   WhatsApp number

<a id="GlobalSuppression"></a>

`GlobalSuppression(**data: Any)`
:   A globally suppressed email address
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: int | Any`
    :   The type of the None singleton.

    `email: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="GlobalSuppressionsListResultMeta"></a>

`GlobalSuppressionsListResultMeta(**data: Any)`
:   Metadata for global_suppressions.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="GlobalSuppressionsSearchData"></a>

`GlobalSuppressionsSearchData(**data: Any)`
:   Search result data for global_suppressions entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: int | None`
    :   Unix timestamp when the global suppression was created

    `email: str | None`
    :   The globally suppressed email address

    `model_config`
    :   The type of the None singleton.

<a id="InvalidEmail"></a>

`InvalidEmail(**data: Any)`
:   An invalid email record
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: int | Any`
    :   The type of the None singleton.

    `email: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reason: str | Any`
    :   The type of the None singleton.

<a id="InvalidEmailsListResultMeta"></a>

`InvalidEmailsListResultMeta(**data: Any)`
:   Metadata for invalid_emails.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="InvalidEmailsSearchData"></a>

`InvalidEmailsSearchData(**data: Any)`
:   Search result data for invalid_emails entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: int | None`
    :   Unix timestamp when the invalid email was recorded

    `email: str | None`
    :   The invalid email address

    `model_config`
    :   The type of the None singleton.

    `reason: str | None`
    :   The reason the email is invalid

<a id="List"></a>

`List(**data: Any)`
:   A SendGrid marketing list
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `contact_count: int | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `metadata: airbyte_agent_sdk.connectors.sendgrid.models.ListMetadata | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

<a id="ListMetadata"></a>

`ListMetadata(**data: Any)`
:   Metadata about the list resource
    
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
    :   The type of the None singleton.

<a id="ListsList"></a>

`ListsList(**data: Any)`
:   Response containing a list of marketing lists
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `metadata: airbyte_agent_sdk.connectors.sendgrid.models.ListsListMetadata | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `result: list[airbyte_agent_sdk.connectors.sendgrid.models.List] | Any`
    :   The type of the None singleton.

<a id="ListsListMetadata"></a>

`ListsListMetadata(**data: Any)`
:   Nested schema for ListsList._metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="ListsListResultMeta"></a>

`ListsListResultMeta(**data: Any)`
:   Metadata for lists.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="ListsSearchData"></a>

`ListsSearchData(**data: Any)`
:   Search result data for lists entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `contact_count: int | None`
    :   Number of contacts in the list

    `id: str | None`
    :   Unique list identifier

    `metadata: dict[str, typing.Any] | None`
    :   Metadata about the list resource

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Name of the list

<a id="Segment"></a>

`Segment(**data: Any)`
:   A SendGrid marketing segment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `contacts_count: int | Any`
    :   The type of the None singleton.

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `next_sample_update: str | Any | None`
    :   The type of the None singleton.

    `parent_list_ids: list[str | None] | Any | None`
    :   The type of the None singleton.

    `query_version: str | Any`
    :   The type of the None singleton.

    `sample_updated_at: str | Any | None`
    :   The type of the None singleton.

    `status: airbyte_agent_sdk.connectors.sendgrid.models.SegmentStatus | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

<a id="SegmentStatus"></a>

`SegmentStatus(**data: Any)`
:   Segment status details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `query_validation: str | Any`
    :   The type of the None singleton.

<a id="SegmentsList"></a>

`SegmentsList(**data: Any)`
:   Response containing a list of segments
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.sendgrid.models.Segment] | Any`
    :   The type of the None singleton.

<a id="SegmentsSearchData"></a>

`SegmentsSearchData(**data: Any)`
:   Search result data for segments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `contacts_count: int | None`
    :   Number of contacts in the segment

    `created_at: str | None`
    :   When the segment was created

    `id: str | None`
    :   Unique segment identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Segment name

    `next_sample_update: str | None`
    :   When the next sample update will occur

    `parent_list_ids: list[typing.Any] | None`
    :   IDs of parent lists

    `query_version: str | None`
    :   Query version used

    `sample_updated_at: str | None`
    :   When the sample was last updated

    `status: dict[str, typing.Any] | None`
    :   Segment status details

    `updated_at: str | None`
    :   When the segment was last updated

<a id="SendgridAuthConfig"></a>

`SendgridAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your SendGrid API key (generated at https://app.sendgrid.com/settings/api_keys)

    `model_config`
    :   The type of the None singleton.

<a id="SendgridCheckResult"></a>

`SendgridCheckResult(**data: Any)`
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

<a id="SendgridExecuteResult"></a>

`SendgridExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult[list[Segment]]
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult[list[SuppressionGroup]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="SendgridExecuteResultWithMeta"></a>

`SendgridExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[Block], BlocksListResultMeta]
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[Bounce], BouncesListResultMeta]
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[Contact], ContactsListResultMeta]
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[GlobalSuppression], GlobalSuppressionsListResultMeta]
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[InvalidEmail], InvalidEmailsListResultMeta]
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[List], ListsListResultMeta]
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[SingleSendStats], SinglesendStatsListResultMeta]
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[SingleSend], SinglesendsListResultMeta]
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[SpamReport], SpamReportsListResultMeta]
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[SuppressionGroupMember], SuppressionGroupMembersListResultMeta]
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta[list[Template], TemplatesListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`SendgridExecuteResultWithMeta[list[Block], BlocksListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BlocksListResult"></a>

`BlocksListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SendgridExecuteResultWithMeta[list[Bounce], BouncesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BouncesListResult"></a>

`BouncesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SendgridExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
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

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SendgridExecuteResultWithMeta[list[Contact], ContactsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
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

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SendgridExecuteResultWithMeta[list[GlobalSuppression], GlobalSuppressionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="GlobalSuppressionsListResult"></a>

`GlobalSuppressionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SendgridExecuteResultWithMeta[list[InvalidEmail], InvalidEmailsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="InvalidEmailsListResult"></a>

`InvalidEmailsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SendgridExecuteResultWithMeta[list[List], ListsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ListsListResult"></a>

`ListsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SendgridExecuteResultWithMeta[list[SingleSendStats], SinglesendStatsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SinglesendStatsListResult"></a>

`SinglesendStatsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SendgridExecuteResultWithMeta[list[SingleSend], SinglesendsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SinglesendsListResult"></a>

`SinglesendsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SendgridExecuteResultWithMeta[list[SpamReport], SpamReportsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SpamReportsListResult"></a>

`SpamReportsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SendgridExecuteResultWithMeta[list[SuppressionGroupMember], SuppressionGroupMembersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersListResult"></a>

`SuppressionGroupMembersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SendgridExecuteResultWithMeta[list[Template], TemplatesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TemplatesListResult"></a>

`TemplatesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SendgridExecuteResult[list[Segment]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
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

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`SendgridExecuteResult[list[SuppressionGroup]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SuppressionGroupsListResult"></a>

`SuppressionGroupsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.sendgrid.models.SendgridExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SendgridReplicationConfig"></a>

`SendgridReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from SendGrid.
    
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
    :   UTC date and time in the format 2017-01-25T00:00:00Z. Any data before this date will not be replicated.

<a id="SingleSend"></a>

`SingleSend(**data: Any)`
:   A SendGrid single send
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `categories: list[str] | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `email_config: airbyte_agent_sdk.connectors.sendgrid.models.SingleSendEmailConfig | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `is_abtest: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `send_at: str | Any | None`
    :   The type of the None singleton.

    `send_to: airbyte_agent_sdk.connectors.sendgrid.models.SingleSendSendTo | Any | None`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

<a id="SingleSendEmailConfig"></a>

`SingleSendEmailConfig(**data: Any)`
:   Email configuration details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `custom_unsubscribe_url: str | Any | None`
    :   The type of the None singleton.

    `design_id: str | Any | None`
    :   The type of the None singleton.

    `editor: str | Any | None`
    :   The type of the None singleton.

    `generate_plain_content: bool | Any`
    :   The type of the None singleton.

    `html_content: str | Any | None`
    :   The type of the None singleton.

    `ip_pool: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `plain_content: str | Any | None`
    :   The type of the None singleton.

    `sender_id: int | Any | None`
    :   The type of the None singleton.

    `subject: str | Any | None`
    :   The type of the None singleton.

    `suppression_group_id: int | Any | None`
    :   The type of the None singleton.

<a id="SingleSendSendTo"></a>

`SingleSendSendTo(**data: Any)`
:   Recipients configuration
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `all: bool | Any`
    :   The type of the None singleton.

    `list_ids: list[str] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `segment_ids: list[str] | Any | None`
    :   The type of the None singleton.

<a id="SingleSendStats"></a>

`SingleSendStats(**data: Any)`
:   Stats for a single send
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ab_phase: str | Any | None`
    :   The type of the None singleton.

    `ab_variation: str | Any | None`
    :   The type of the None singleton.

    `aggregation: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `stats: airbyte_agent_sdk.connectors.sendgrid.models.SingleSendStatsStats | Any | None`
    :   The type of the None singleton.

<a id="SingleSendStatsList"></a>

`SingleSendStatsList(**data: Any)`
:   Response containing a list of single send stats
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `metadata: airbyte_agent_sdk.connectors.sendgrid.models.SingleSendStatsListMetadata | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `results: list[airbyte_agent_sdk.connectors.sendgrid.models.SingleSendStats] | Any`
    :   The type of the None singleton.

<a id="SingleSendStatsListMetadata"></a>

`SingleSendStatsListMetadata(**data: Any)`
:   Nested schema for SingleSendStatsList._metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="SingleSendStatsStats"></a>

`SingleSendStatsStats(**data: Any)`
:   Email statistics for the single send
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bounce_drops: int | Any`
    :   The type of the None singleton.

    `bounces: int | Any`
    :   The type of the None singleton.

    `clicks: int | Any`
    :   The type of the None singleton.

    `delivered: int | Any`
    :   The type of the None singleton.

    `invalid_emails: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `opens: int | Any`
    :   The type of the None singleton.

    `requests: int | Any`
    :   The type of the None singleton.

    `spam_report_drops: int | Any`
    :   The type of the None singleton.

    `spam_reports: int | Any`
    :   The type of the None singleton.

    `unique_clicks: int | Any`
    :   The type of the None singleton.

    `unique_opens: int | Any`
    :   The type of the None singleton.

    `unsubscribes: int | Any`
    :   The type of the None singleton.

<a id="SingleSendsList"></a>

`SingleSendsList(**data: Any)`
:   Response containing a list of single sends
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `metadata: airbyte_agent_sdk.connectors.sendgrid.models.SingleSendsListMetadata | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `result: list[airbyte_agent_sdk.connectors.sendgrid.models.SingleSend] | Any`
    :   The type of the None singleton.

<a id="SingleSendsListMetadata"></a>

`SingleSendsListMetadata(**data: Any)`
:   Nested schema for SingleSendsList._metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="SinglesendStatsListResultMeta"></a>

`SinglesendStatsListResultMeta(**data: Any)`
:   Metadata for singlesend_stats.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="SinglesendStatsSearchData"></a>

`SinglesendStatsSearchData(**data: Any)`
:   Search result data for singlesend_stats entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ab_phase: str | None`
    :   The A/B test phase

    `ab_variation: str | None`
    :   The A/B test variation

    `aggregation: str | None`
    :   The aggregation type

    `id: str | None`
    :   The single send ID

    `model_config`
    :   The type of the None singleton.

    `stats: dict[str, typing.Any] | None`
    :   Email statistics for the single send

<a id="SinglesendsListResultMeta"></a>

`SinglesendsListResultMeta(**data: Any)`
:   Metadata for singlesends.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="SinglesendsSearchData"></a>

`SinglesendsSearchData(**data: Any)`
:   Search result data for singlesends entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `categories: list[typing.Any] | None`
    :   Categories associated with this single send

    `created_at: str | None`
    :   When the single send was created

    `id: str | None`
    :   Unique single send identifier

    `is_abtest: bool | None`
    :   Whether this is an A/B test

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Single send name

    `send_at: str | None`
    :   Scheduled send time

    `status: str | None`
    :   Current status: draft, scheduled, or triggered

    `updated_at: str | None`
    :   When the single send was last updated

<a id="SpamReport"></a>

`SpamReport(**data: Any)`
:   A spam report record
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: int | Any`
    :   The type of the None singleton.

    `email: str | Any`
    :   The type of the None singleton.

    `ip: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SpamReportsListResultMeta"></a>

`SpamReportsListResultMeta(**data: Any)`
:   Metadata for spam_reports.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="SuppressionGroup"></a>

`SuppressionGroup(**data: Any)`
:   A suppression (unsubscribe) group
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `is_default: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `unsubscribes: int | Any`
    :   The type of the None singleton.

<a id="SuppressionGroupMember"></a>

`SuppressionGroupMember(**data: Any)`
:   A member of a suppression group
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: int | Any`
    :   The type of the None singleton.

    `email: str | Any`
    :   The type of the None singleton.

    `group_id: int | Any`
    :   The type of the None singleton.

    `group_name: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersListResultMeta"></a>

`SuppressionGroupMembersListResultMeta(**data: Any)`
:   Metadata for suppression_group_members.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="SuppressionGroupMembersSearchData"></a>

`SuppressionGroupMembersSearchData(**data: Any)`
:   Search result data for suppression_group_members entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: int | None`
    :   Unix timestamp when the suppression was created

    `email: str | None`
    :   The suppressed email address

    `group_id: int | None`
    :   ID of the suppression group

    `group_name: str | None`
    :   Name of the suppression group

    `model_config`
    :   The type of the None singleton.

<a id="SuppressionGroupsSearchData"></a>

`SuppressionGroupsSearchData(**data: Any)`
:   Search result data for suppression_groups entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | None`
    :   Description of the suppression group

    `id: int | None`
    :   Unique suppression group identifier

    `is_default: bool | None`
    :   Whether this is the default suppression group

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Suppression group name

    `unsubscribes: int | None`
    :   Number of unsubscribes in this group

<a id="Template"></a>

`Template(**data: Any)`
:   A SendGrid transactional template
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `generation: str | Any`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

    `versions: list[typing.Any] | Any | None`
    :   The type of the None singleton.

<a id="TemplatesList"></a>

`TemplatesList(**data: Any)`
:   Response containing a list of templates
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `metadata: airbyte_agent_sdk.connectors.sendgrid.models.TemplatesListMetadata | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `templates: list[airbyte_agent_sdk.connectors.sendgrid.models.Template] | Any`
    :   The type of the None singleton.

<a id="TemplatesListMetadata"></a>

`TemplatesListMetadata(**data: Any)`
:   Nested schema for TemplatesList._metadata
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="TemplatesListResultMeta"></a>

`TemplatesListResultMeta(**data: Any)`
:   Metadata for templates.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="TemplatesSearchData"></a>

`TemplatesSearchData(**data: Any)`
:   Search result data for templates entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `generation: str | None`
    :   Template generation (legacy or dynamic)

    `id: str | None`
    :   Unique template identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Template name

    `updated_at: str | None`
    :   When the template was last updated

    `versions: list[typing.Any] | None`
    :   Template versions