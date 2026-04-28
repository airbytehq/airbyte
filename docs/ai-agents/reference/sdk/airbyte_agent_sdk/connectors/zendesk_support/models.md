---
id: airbyte_agent_sdk-connectors-zendesk_support-models
title: airbyte_agent_sdk.connectors.zendesk_support.models
---

Module airbyte_agent_sdk.connectors.zendesk_support.models
==========================================================
Pydantic models for zendesk-support connector.

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

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[BrandsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[DeletedTicketsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[GroupsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[OrganizationsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[SatisfactionRatingsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[TagsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[TicketAuditsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[TicketCommentsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[TicketFieldsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[TicketFormsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[TicketMetricsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[TicketsSearchData]
    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult[UsersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[BrandsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BrandsSearchResult"></a>

`BrandsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[DeletedTicketsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DeletedTicketsSearchResult"></a>

`DeletedTicketsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[GroupsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[OrganizationsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrganizationsSearchResult"></a>

`OrganizationsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[SatisfactionRatingsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TagsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TicketAuditsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TicketAuditsSearchResult"></a>

`TicketAuditsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TicketCommentsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TicketCommentsSearchResult"></a>

`TicketCommentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TicketFieldsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TicketFormsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TicketMetricsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TicketMetricsSearchResult"></a>

`TicketMetricsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[TicketsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[UsersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.zendesk_support.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Article"></a>

`Article(**data: Any)`
:   Help Center article object
    
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

    `created_at: str | Any`
    :   The type of the None singleton.

    `draft: bool | Any`
    :   The type of the None singleton.

    `html_url: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `label_names: list[str] | Any`
    :   The type of the None singleton.

    `locale: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `position: int | Any`
    :   The type of the None singleton.

    `promoted: bool | Any`
    :   The type of the None singleton.

    `section_id: int | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

    `vote_count: int | Any`
    :   The type of the None singleton.

    `vote_sum: int | Any`
    :   The type of the None singleton.

<a id="ArticleAttachment"></a>

`ArticleAttachment(**data: Any)`
:   Article attachment object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `article_id: int | Any`
    :   The type of the None singleton.

    `content_type: str | Any`
    :   The type of the None singleton.

    `content_url: str | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `file_name: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `inline: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `size: int | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="ArticleAttachmentsListResultMeta"></a>

`ArticleAttachmentsListResultMeta(**data: Any)`
:   Metadata for article_attachments.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="ArticlesListResultMeta"></a>

`ArticlesListResultMeta(**data: Any)`
:   Metadata for articles.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="Attachment"></a>

`Attachment(**data: Any)`
:   Zendesk Support attachment object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content_type: str | Any`
    :   The type of the None singleton.

    `content_url: str | Any`
    :   The type of the None singleton.

    `deleted: bool | Any`
    :   The type of the None singleton.

    `file_name: str | Any`
    :   The type of the None singleton.

    `height: int | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `inline: bool | Any`
    :   The type of the None singleton.

    `malware_access_override: bool | Any`
    :   The type of the None singleton.

    `malware_scan_result: str | Any`
    :   The type of the None singleton.

    `mapped_content_url: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `size: int | Any`
    :   The type of the None singleton.

    `thumbnails: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

    `width: int | Any | None`
    :   The type of the None singleton.

<a id="Automation"></a>

`Automation(**data: Any)`
:   Zendesk Support automation object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actions: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `active: bool | Any`
    :   The type of the None singleton.

    `conditions: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `position: int | Any`
    :   The type of the None singleton.

    `raw_title: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="AutomationsListResultMeta"></a>

`AutomationsListResultMeta(**data: Any)`
:   Metadata for automations.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="Brand"></a>

`Brand(**data: Any)`
:   Zendesk Support brand object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | Any`
    :   The type of the None singleton.

    `brand_url: str | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `default: bool | Any`
    :   The type of the None singleton.

    `has_help_center: bool | Any`
    :   The type of the None singleton.

    `help_center_state: str | Any`
    :   The type of the None singleton.

    `host_mapping: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `is_deleted: bool | Any`
    :   The type of the None singleton.

    `logo: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `signature_template: str | Any`
    :   The type of the None singleton.

    `subdomain: str | Any`
    :   The type of the None singleton.

    `ticket_form_ids: list[int] | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="BrandsListResultMeta"></a>

`BrandsListResultMeta(**data: Any)`
:   Metadata for brands.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="BrandsSearchData"></a>

`BrandsSearchData(**data: Any)`
:   Search result data for brands entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | None`
    :   Indicates whether the brand is set as active

    `brand_url: str | None`
    :   The public URL of the brand

    `created_at: str | None`
    :   Timestamp when the brand was created

    `default: bool | None`
    :   Indicates whether the brand is the default brand for tickets generated from non-branded channels

    `has_help_center: bool | None`
    :   Indicates whether the brand has a Help Center enabled

    `help_center_state: str | None`
    :   The state of the Help Center, with allowed values of enabled, disabled, or restricted

    `host_mapping: str | None`
    :   The host mapping configuration for the brand, visible only to administrators

    `id: int | None`
    :   Unique identifier automatically assigned when the brand is created

    `is_deleted: bool | None`
    :   Indicates whether the brand has been deleted

    `logo: str | None`
    :   Brand logo image file represented as an Attachment object

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the brand

    `signature_template: str | None`
    :   The signature template used for the brand

    `subdomain: str | None`
    :   The subdomain associated with the brand

    `ticket_form_ids: list[typing.Any] | None`
    :   Array of ticket form IDs that are available for use by this brand

    `updated_at: str | None`
    :   Timestamp when the brand was last updated

    `url: str | None`
    :   The API URL for accessing this brand resource

<a id="DeletedTicket"></a>

`DeletedTicket(**data: Any)`
:   Zendesk Support deleted ticket object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actor: airbyte_agent_sdk.connectors.zendesk_support.models.DeletedTicketActor | Any | None`
    :   The type of the None singleton.

    `deleted_at: str | Any | None`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `previous_state: str | Any | None`
    :   The type of the None singleton.

    `subject: str | Any | None`
    :   The type of the None singleton.

<a id="DeletedTicketActor"></a>

`DeletedTicketActor(**data: Any)`
:   The user who performed the deletion action
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The unique identifier of the user

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The name of the user

<a id="DeletedTicketsListResultMeta"></a>

`DeletedTicketsListResultMeta(**data: Any)`
:   Metadata for deleted_tickets.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="DeletedTicketsSearchData"></a>

`DeletedTicketsSearchData(**data: Any)`
:   Search result data for deleted_tickets entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actor: dict[str, typing.Any] | None`
    :   The user who performed the deletion action

    `deleted_at: str | None`
    :   The timestamp when the ticket was deleted

    `description: str | None`
    :   Additional details or comments about the deleted ticket

    `id: int | None`
    :   The unique identifier of the deleted ticket

    `model_config`
    :   The type of the None singleton.

    `previous_state: str | None`
    :   The state of the ticket before it was deleted

    `subject: str | None`
    :   The subject or title of the deleted ticket

<a id="Group"></a>

`Group(**data: Any)`
:   Zendesk Support group object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any`
    :   The type of the None singleton.

    `default: bool | Any`
    :   The type of the None singleton.

    `deleted: bool | Any`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `is_public: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="GroupMembership"></a>

`GroupMembership(**data: Any)`
:   Zendesk Support group membership object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any`
    :   The type of the None singleton.

    `default: bool | Any`
    :   The type of the None singleton.

    `group_id: int | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

    `user_id: int | Any`
    :   The type of the None singleton.

<a id="GroupMembershipsListResultMeta"></a>

`GroupMembershipsListResultMeta(**data: Any)`
:   Metadata for group_memberships.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
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

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
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

    `created_at: str | None`
    :   Timestamp indicating when the group was created

    `default: bool | None`
    :   Indicates if the group is the default one for the account

    `deleted: bool | None`
    :   Indicates whether the group has been deleted

    `description: str | None`
    :   The description of the group

    `id: int | None`
    :   Unique identifier automatically assigned when creating groups

    `is_public: bool | None`
    :   Indicates if the group is public (true) or private (false)

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the group

    `updated_at: str | None`
    :   Timestamp indicating when the group was last updated

    `url: str | None`
    :   The API URL of the group

<a id="Macro"></a>

`Macro(**data: Any)`
:   Zendesk Support macro object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actions: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `active: bool | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `position: int | Any`
    :   The type of the None singleton.

    `raw_title: str | Any`
    :   The type of the None singleton.

    `restriction: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="MacrosListResultMeta"></a>

`MacrosListResultMeta(**data: Any)`
:   Metadata for macros.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="Organization"></a>

`Organization(**data: Any)`
:   Zendesk Support organization object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any`
    :   The type of the None singleton.

    `details: str | Any | None`
    :   The type of the None singleton.

    `domain_names: list[str] | Any`
    :   The type of the None singleton.

    `external_id: str | Any | None`
    :   The type of the None singleton.

    `group_id: int | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `notes: str | Any | None`
    :   The type of the None singleton.

    `organization_fields: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `shared_comments: bool | Any`
    :   The type of the None singleton.

    `shared_tickets: bool | Any`
    :   The type of the None singleton.

    `tags: list[str] | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="OrganizationMembership"></a>

`OrganizationMembership(**data: Any)`
:   Zendesk Support organization membership object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any`
    :   The type of the None singleton.

    `default: bool | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organization_id: int | Any`
    :   The type of the None singleton.

    `organization_name: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

    `user_id: int | Any`
    :   The type of the None singleton.

    `view_tickets: bool | Any`
    :   The type of the None singleton.

<a id="OrganizationMembershipsListResultMeta"></a>

`OrganizationMembershipsListResultMeta(**data: Any)`
:   Metadata for organization_memberships.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="OrganizationsListResultMeta"></a>

`OrganizationsListResultMeta(**data: Any)`
:   Metadata for organizations.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
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
    :   Timestamp when the organization was created

    `deleted_at: str | None`
    :   Timestamp when the organization was deleted

    `details: str | None`
    :   Details about the organization, such as the address

    `domain_names: list[typing.Any] | None`
    :   Array of domain names associated with this organization for automatic user assignment

    `external_id: str | None`
    :   Unique external identifier to associate the organization to an external record (case-insensitive)

    `group_id: int | None`
    :   ID of the group where new tickets from users in this organization are automatically assigned

    `id: int | None`
    :   Unique identifier automatically assigned when the organization is created

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Unique name for the organization (mandatory field)

    `notes: str | None`
    :   Notes about the organization

    `organization_fields: dict[str, typing.Any] | None`
    :   Key-value object for custom organization fields

    `shared_comments: bool | None`
    :   Boolean indicating whether end users in this organization can comment on each other's tickets

    `shared_tickets: bool | None`
    :   Boolean indicating whether end users in this organization can see each other's tickets

    `tags: list[typing.Any] | None`
    :   Array of tags associated with the organization

    `updated_at: str | None`
    :   Timestamp of the last update to the organization

    `url: str | None`
    :   The API URL of this organization

<a id="SLAPolicy"></a>

`SLAPolicy(**data: Any)`
:   Zendesk Support SLA policy object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `filter: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `policy_metrics: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `position: int | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="SatisfactionRating"></a>

`SatisfactionRating(**data: Any)`
:   Zendesk Support satisfaction rating object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `assignee_id: int | Any | None`
    :   The type of the None singleton.

    `comment: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `group_id: int | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reason: str | Any | None`
    :   The type of the None singleton.

    `reason_code: int | Any | None`
    :   The type of the None singleton.

    `reason_id: int | Any | None`
    :   The type of the None singleton.

    `requester_id: int | Any`
    :   The type of the None singleton.

    `score: str | Any`
    :   The type of the None singleton.

    `ticket_id: int | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
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

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
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

    `assignee_id: int | None`
    :   The identifier of the agent assigned to the ticket at the time the rating was submitted

    `comment: str | None`
    :   Optional comment provided by the requester with the rating

    `created_at: str | None`
    :   Timestamp indicating when the satisfaction rating was created

    `group_id: int | None`
    :   The identifier of the group assigned to the ticket at the time the rating was submitted

    `id: int | None`
    :   Unique identifier for the satisfaction rating, automatically assigned upon creation

    `model_config`
    :   The type of the None singleton.

    `reason: str | None`
    :   Free-text reason for a bad rating provided by the requester in a follow-up question

    `reason_id: int | None`
    :   Identifier for the predefined reason given for a negative rating

    `requester_id: int | None`
    :   The identifier of the ticket requester who submitted the satisfaction rating

    `score: str | None`
    :   The satisfaction rating value: 'offered', 'unoffered', 'good', or 'bad'

    `ticket_id: int | None`
    :   The identifier of the ticket being rated

    `updated_at: str | None`
    :   Timestamp indicating when the satisfaction rating was last updated

    `url: str | None`
    :   The API URL of this satisfaction rating resource

<a id="SlaPoliciesListResultMeta"></a>

`SlaPoliciesListResultMeta(**data: Any)`
:   Metadata for sla_policies.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="Tag"></a>

`Tag(**data: Any)`
:   Zendesk Support tag object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
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

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
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

    `count: int | None`
    :   The number of times this tag has been used across resources

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The tag name string used to label and categorize resources

<a id="Ticket"></a>

`Ticket(**data: Any)`
:   Zendesk Support ticket object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `allow_attachments: bool | Any`
    :   The type of the None singleton.

    `allow_channelback: bool | Any`
    :   The type of the None singleton.

    `assignee_id: int | Any | None`
    :   The type of the None singleton.

    `brand_id: int | Any`
    :   The type of the None singleton.

    `collaborator_ids: list[int] | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `custom_fields: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `custom_status_id: int | Any`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `due_at: str | Any | None`
    :   The type of the None singleton.

    `email_cc_ids: list[int] | Any`
    :   The type of the None singleton.

    `external_id: str | Any | None`
    :   The type of the None singleton.

    `fields: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `follower_ids: list[int] | Any`
    :   The type of the None singleton.

    `followup_ids: list[int] | Any`
    :   The type of the None singleton.

    `forum_topic_id: int | Any | None`
    :   The type of the None singleton.

    `from_messaging_channel: bool | Any`
    :   The type of the None singleton.

    `generated_timestamp: int | Any`
    :   The type of the None singleton.

    `group_id: int | Any | None`
    :   The type of the None singleton.

    `has_incidents: bool | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `is_public: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organization_id: int | Any | None`
    :   The type of the None singleton.

    `priority: str | Any | None`
    :   The type of the None singleton.

    `problem_id: int | Any | None`
    :   The type of the None singleton.

    `raw_subject: str | Any | None`
    :   The type of the None singleton.

    `recipient: str | Any | None`
    :   The type of the None singleton.

    `requester_id: int | Any`
    :   The type of the None singleton.

    `result_type: str | Any | None`
    :   The type of the None singleton.

    `satisfaction_rating: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `sharing_agreement_ids: list[int] | Any`
    :   The type of the None singleton.

    `status: str | Any`
    :   The type of the None singleton.

    `subject: str | Any | None`
    :   The type of the None singleton.

    `submitter_id: int | Any`
    :   The type of the None singleton.

    `tags: list[str] | Any`
    :   The type of the None singleton.

    `ticket_form_id: int | Any`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

    `via: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

<a id="TicketAudit"></a>

`TicketAudit(**data: Any)`
:   Zendesk Support ticket audit object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `author_id: int | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `events: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `metadata: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `ticket_id: int | Any`
    :   The type of the None singleton.

    `via: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

<a id="TicketAuditsListResultMeta"></a>

`TicketAuditsListResultMeta(**data: Any)`
:   Metadata for ticket_audits.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="TicketAuditsSearchData"></a>

`TicketAuditsSearchData(**data: Any)`
:   Search result data for ticket_audits entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attachments: list[typing.Any] | None`
    :   Files or documents attached to the audit

    `author_id: int | None`
    :   The unique identifier of the user who created the audit

    `created_at: str | None`
    :   Timestamp indicating when the audit was created

    `events: list[typing.Any] | None`
    :   Array of events that occurred in this audit, such as field changes, comments, or tag updates

    `id: int | None`
    :   Unique identifier for the audit record, automatically assigned when the audit is created

    `metadata: dict[str, typing.Any] | None`
    :   Custom and system data associated with the audit

    `model_config`
    :   The type of the None singleton.

    `ticket_id: int | None`
    :   The unique identifier of the ticket associated with this audit

    `via: dict[str, typing.Any] | None`
    :   Describes how the audit was created, providing context about the creation source

<a id="TicketComment"></a>

`TicketComment(**data: Any)`
:   Zendesk Support ticket comment object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attachments: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `audit_id: int | Any`
    :   The type of the None singleton.

    `author_id: int | Any`
    :   The type of the None singleton.

    `body: str | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `html_body: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `metadata: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `plain_body: str | Any`
    :   The type of the None singleton.

    `public: bool | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `via: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

<a id="TicketCommentsListResultMeta"></a>

`TicketCommentsListResultMeta(**data: Any)`
:   Metadata for ticket_comments.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="TicketCommentsSearchData"></a>

`TicketCommentsSearchData(**data: Any)`
:   Search result data for ticket_comments entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attachments: list[typing.Any] | None`
    :   List of files or media attached to the comment

    `audit_id: int | None`
    :   Identifier of the audit record associated with this comment event

    `author_id: int | None`
    :   Identifier of the user who created the comment

    `body: str | None`
    :   Content of the comment in its original format

    `created_at: str | None`
    :   Timestamp when the comment was created

    `event_type: str | None`
    :   Specific classification of the event within the ticket event stream

    `html_body: str | None`
    :   HTML-formatted content of the comment

    `id: int | None`
    :   Unique identifier for the comment event

    `metadata: dict[str, typing.Any] | None`
    :   Additional structured information about the comment not covered by standard fields

    `model_config`
    :   The type of the None singleton.

    `plain_body: str | None`
    :   Plain text content of the comment without formatting

    `public: bool | None`
    :   Boolean indicating whether the comment is visible to end users or is an internal note

    `ticket_id: int | None`
    :   Identifier of the ticket to which this comment belongs

    `timestamp: int | None`
    :   Timestamp of when the event occurred in the incremental export stream

    `type_: str | None`
    :   Type of event, typically indicating this is a comment event

    `uploads: list[typing.Any] | None`
    :   Array of upload tokens or identifiers for files being attached to the comment

    `via: dict[str, typing.Any] | None`
    :   Channel or method through which the comment was submitted

    `via_reference_id: int | None`
    :   Reference identifier for the channel through which the comment was created

<a id="TicketField"></a>

`TicketField(**data: Any)`
:   Zendesk Support ticket field object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | Any`
    :   The type of the None singleton.

    `agent_description: str | Any | None`
    :   The type of the None singleton.

    `collapsed_for_agents: bool | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `custom_field_options: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `description: str | Any`
    :   The type of the None singleton.

    `editable_in_portal: bool | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `position: int | Any`
    :   The type of the None singleton.

    `raw_description: str | Any`
    :   The type of the None singleton.

    `raw_title: str | Any`
    :   The type of the None singleton.

    `raw_title_in_portal: str | Any`
    :   The type of the None singleton.

    `regexp_for_validation: str | Any | None`
    :   The type of the None singleton.

    `removable: bool | Any`
    :   The type of the None singleton.

    `required: bool | Any`
    :   The type of the None singleton.

    `required_in_portal: bool | Any`
    :   The type of the None singleton.

    `sub_type_id: int | Any`
    :   The type of the None singleton.

    `system_field_options: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `tag: str | Any | None`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `title_in_portal: str | Any`
    :   The type of the None singleton.

    `type_: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

    `visible_in_portal: bool | Any`
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

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
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

    `active: bool | None`
    :   Whether this field is currently available for use

    `agent_description: str | None`
    :   A description of the ticket field that only agents can see

    `collapsed_for_agents: bool | None`
    :   If true, the field is shown to agents by default; if false, it is hidden alongside infrequently used fields

    `created_at: str | None`
    :   Timestamp when the custom ticket field was created

    `custom_field_options: list[typing.Any] | None`
    :   Array of option objects for custom ticket fields of type multiselect or tagger

    `custom_statuses: list[typing.Any] | None`
    :   List of customized ticket statuses, only present for system ticket fields of type custom_status

    `description: str | None`
    :   Text describing the purpose of the ticket field to users

    `editable_in_portal: bool | None`
    :   Whether this field is editable by end users in Help Center

    `id: int | None`
    :   Unique identifier for the ticket field, automatically assigned when created

    `key: str | None`
    :   Internal identifier or reference key for the field

    `model_config`
    :   The type of the None singleton.

    `position: int | None`
    :   The relative position of the ticket field on a ticket, controlling display order

    `raw_description: str | None`
    :   The dynamic content placeholder if present, or the description value if not

    `raw_title: str | None`
    :   The dynamic content placeholder if present, or the title value if not

    `raw_title_in_portal: str | None`
    :   The dynamic content placeholder if present, or the title_in_portal value if not

    `regexp_for_validation: str | None`
    :   For regexp fields only, the validation pattern for a field value to be deemed valid

    `removable: bool | None`
    :   If false, this field is a system field that must be present on all tickets

    `required: bool | None`
    :   If true, agents must enter a value in the field to change the ticket status to solved

    `required_in_portal: bool | None`
    :   If true, end users must enter a value in the field to create a request

    `sub_type_id: int | None`
    :   For system ticket fields of type priority and status, controlling available options

    `system_field_options: list[typing.Any] | None`
    :   Array of options for system ticket fields of type tickettype, priority, or status

    `tag: str | None`
    :   For checkbox fields only, a tag added to tickets when the checkbox field is selected

    `title: str | None`
    :   The title of the ticket field displayed to agents

    `title_in_portal: str | None`
    :   The title of the ticket field displayed to end users in Help Center

    `type_: str | None`
    :   Field type such as text, textarea, checkbox, date, integer, decimal, regexp, multiselect, or tagger

    `updated_at: str | None`
    :   Timestamp when the custom ticket field was last updated

    `url: str | None`
    :   The API URL for this ticket field resource

    `visible_in_portal: bool | None`
    :   Whether this field is visible to end users in Help Center

<a id="TicketForm"></a>

`TicketForm(**data: Any)`
:   Zendesk Support ticket form object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | Any`
    :   The type of the None singleton.

    `agent_conditions: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `default: bool | Any`
    :   The type of the None singleton.

    `display_name: str | Any`
    :   The type of the None singleton.

    `end_user_conditions: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `end_user_visible: bool | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `in_all_brands: bool | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `position: int | Any`
    :   The type of the None singleton.

    `raw_display_name: str | Any`
    :   The type of the None singleton.

    `raw_name: str | Any`
    :   The type of the None singleton.

    `restricted_brand_ids: list[int] | Any`
    :   The type of the None singleton.

    `ticket_field_ids: list[int] | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
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

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
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

    `active: bool | None`
    :   Indicates if the form is set as active

    `agent_conditions: list[typing.Any] | None`
    :   Array of condition sets for agent workspaces

    `created_at: str | None`
    :   Timestamp when the ticket form was created

    `default: bool | None`
    :   Indicates if the form is the default form for this account

    `display_name: str | None`
    :   The name of the form that is displayed to an end user

    `end_user_conditions: list[typing.Any] | None`
    :   Array of condition sets for end user products

    `end_user_visible: bool | None`
    :   Indicates if the form is visible to the end user

    `id: int | None`
    :   Unique identifier for the ticket form, automatically assigned when creating the form

    `in_all_brands: bool | None`
    :   Indicates if the form is available for use in all brands on this account

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the ticket form

    `position: int | None`
    :   The position of this form among other forms in the account, such as in a dropdown

    `raw_display_name: str | None`
    :   The dynamic content placeholder if present, or the display_name value if not

    `raw_name: str | None`
    :   The dynamic content placeholder if present, or the name value if not

    `restricted_brand_ids: list[typing.Any] | None`
    :   IDs of all brands that this ticket form is restricted to

    `ticket_field_ids: list[typing.Any] | None`
    :   IDs of all ticket fields included in this ticket form

    `updated_at: str | None`
    :   Timestamp of the last update to the ticket form

    `url: str | None`
    :   URL of the ticket form

<a id="TicketMetric"></a>

`TicketMetric(**data: Any)`
:   Zendesk Support ticket metric object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_wait_time_in_minutes: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `assigned_at: str | Any | None`
    :   The type of the None singleton.

    `assignee_stations: int | Any`
    :   The type of the None singleton.

    `assignee_updated_at: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `first_resolution_time_in_minutes: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `full_resolution_time_in_minutes: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `group_stations: int | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `initially_assigned_at: str | Any | None`
    :   The type of the None singleton.

    `latest_comment_added_at: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `on_hold_time_in_minutes: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `reopens: int | Any`
    :   The type of the None singleton.

    `replies: int | Any`
    :   The type of the None singleton.

    `reply_time_in_minutes: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `requester_updated_at: str | Any`
    :   The type of the None singleton.

    `requester_wait_time_in_minutes: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `solved_at: str | Any | None`
    :   The type of the None singleton.

    `status_updated_at: str | Any`
    :   The type of the None singleton.

    `ticket_id: int | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="TicketMetricsListResultMeta"></a>

`TicketMetricsListResultMeta(**data: Any)`
:   Metadata for ticket_metrics.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="TicketMetricsSearchData"></a>

`TicketMetricsSearchData(**data: Any)`
:   Search result data for ticket_metrics entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `agent_wait_time_in_minutes: dict[str, typing.Any] | None`
    :   Number of minutes the agent spent waiting during calendar and business hours

    `assigned_at: str | None`
    :   Timestamp when the ticket was assigned

    `assignee_stations: int | None`
    :   Number of assignees the ticket had

    `assignee_updated_at: str | None`
    :   Timestamp when the assignee last updated the ticket

    `created_at: str | None`
    :   Timestamp when the metric record was created

    `custom_status_updated_at: str | None`
    :   Timestamp when the ticket's custom status was last updated

    `first_resolution_time_in_minutes: dict[str, typing.Any] | None`
    :   Number of minutes to the first resolution time during calendar and business hours

    `full_resolution_time_in_minutes: dict[str, typing.Any] | None`
    :   Number of minutes to the full resolution during calendar and business hours

    `generated_timestamp: int | None`
    :   Timestamp of when record was last updated

    `group_stations: int | None`
    :   Number of groups the ticket passed through

    `id: int | None`
    :   Unique identifier for the ticket metric record

    `initially_assigned_at: str | None`
    :   Timestamp when the ticket was initially assigned

    `instance_id: int | None`
    :   ID of the Zendesk instance associated with the ticket

    `latest_comment_added_at: str | None`
    :   Timestamp when the latest comment was added

    `metric: str | None`
    :   Ticket metrics data

    `model_config`
    :   The type of the None singleton.

    `on_hold_time_in_minutes: dict[str, typing.Any] | None`
    :   Number of minutes on hold

    `reopens: int | None`
    :   Total number of times the ticket was reopened

    `replies: int | None`
    :   The number of public replies added to a ticket by an agent

    `reply_time_in_minutes: dict[str, typing.Any] | None`
    :   Number of minutes to the first reply during calendar and business hours

    `reply_time_in_seconds: dict[str, typing.Any] | None`
    :   Number of seconds to the first reply during calendar hours, only available for Messaging tickets

    `requester_updated_at: str | None`
    :   Timestamp when the requester last updated the ticket

    `requester_wait_time_in_minutes: dict[str, typing.Any] | None`
    :   Number of minutes the requester spent waiting during calendar and business hours

    `solved_at: str | None`
    :   Timestamp when the ticket was solved

    `status: dict[str, typing.Any] | None`
    :   The current status of the ticket (open, pending, solved, etc.).

    `status_updated_at: str | None`
    :   Timestamp when the status of the ticket was last updated

    `ticket_id: int | None`
    :   Identifier of the associated ticket

    `time: str | None`
    :   Time related to the ticket

    `type_: str | None`
    :   Type of ticket

    `updated_at: str | None`
    :   Timestamp when the metric record was last updated

    `url: str | None`
    :   The API url of the ticket metric

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

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
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

    `allow_attachments: bool | None`
    :   Boolean indicating whether attachments are allowed on the ticket

    `allow_channelback: bool | None`
    :   Boolean indicating whether agents can reply to the ticket through the original channel

    `assignee_id: int | None`
    :   Unique identifier of the agent currently assigned to the ticket

    `brand_id: int | None`
    :   Unique identifier of the brand associated with the ticket in multi-brand accounts

    `collaborator_ids: list[typing.Any] | None`
    :   Array of user identifiers who are collaborating on the ticket

    `created_at: str | None`
    :   Timestamp indicating when the ticket was created

    `custom_fields: list[typing.Any] | None`
    :   Array of custom field values specific to the account's ticket configuration

    `custom_status_id: int | None`
    :   Unique identifier of the custom status applied to the ticket

    `deleted_ticket_form_id: int | None`
    :   The ID of the ticket form that was previously associated with this ticket but has since been deleted

    `description: str | None`
    :   Initial description or content of the ticket when it was created

    `due_at: str | None`
    :   Timestamp indicating when the ticket is due for completion or resolution

    `email_cc_ids: list[typing.Any] | None`
    :   Array of user identifiers who are CC'd on ticket email notifications

    `external_id: str | None`
    :   External identifier for the ticket, used for integrations with other systems

    `fields: list[typing.Any] | None`
    :   Array of ticket field values including both system and custom fields

    `follower_ids: list[typing.Any] | None`
    :   Array of user identifiers who are following the ticket for updates

    `followup_ids: list[typing.Any] | None`
    :   Array of identifiers for follow-up tickets related to this ticket

    `forum_topic_id: int | None`
    :   Unique identifier linking the ticket to a forum topic if applicable

    `from_messaging_channel: bool | None`
    :   Boolean indicating whether the ticket originated from a messaging channel

    `generated_timestamp: int | None`
    :   Timestamp updated for all ticket updates including system changes, used for incremental export

    `group_id: int | None`
    :   Unique identifier of the agent group assigned to handle the ticket

    `has_incidents: bool | None`
    :   Boolean indicating whether this problem ticket has related incident tickets

    `id: int | None`
    :   Unique identifier for the ticket

    `is_public: bool | None`
    :   Boolean indicating whether the ticket is publicly visible

    `model_config`
    :   The type of the None singleton.

    `organization_id: int | None`
    :   Unique identifier of the organization associated with the ticket

    `priority: str | None`
    :   Priority level assigned to the ticket (e.g., urgent, high, normal, low)

    `problem_id: int | None`
    :   Unique identifier of the problem ticket if this is an incident ticket

    `raw_subject: str | None`
    :   Original unprocessed subject line before any system modifications

    `recipient: str | None`
    :   Email address or identifier of the ticket recipient

    `requester_id: int | None`
    :   Unique identifier of the user who requested or created the ticket

    `result_type: str | None`
    :   The type of the search result (e.g. ticket) when returned from search endpoints

    `satisfaction_rating: Any`
    :   Object containing customer satisfaction rating data for the ticket

    `sharing_agreement_ids: list[typing.Any] | None`
    :   Array of sharing agreement identifiers if the ticket is shared across Zendesk instances

    `status: str | None`
    :   Current status of the ticket (e.g., new, open, pending, solved, closed)

    `subject: str | None`
    :   Subject line of the ticket describing the issue or request

    `submitter_id: int | None`
    :   Unique identifier of the user who submitted the ticket on behalf of the requester

    `tags: list[typing.Any] | None`
    :   Array of tags applied to the ticket for categorization and filtering

    `ticket_form_id: int | None`
    :   Unique identifier of the ticket form used when creating the ticket

    `type_: str | None`
    :   Type of ticket (e.g., problem, incident, question, task)

    `updated_at: str | None`
    :   Timestamp indicating when the ticket was last updated with a ticket event

    `url: str | None`
    :   API URL to access the full ticket resource

    `via: dict[str, typing.Any] | None`
    :   Object describing the channel and method through which the ticket was created

<a id="Trigger"></a>

`Trigger(**data: Any)`
:   Zendesk Support trigger object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actions: list[dict[str, typing.Any]] | Any`
    :   The type of the None singleton.

    `active: bool | Any`
    :   The type of the None singleton.

    `category_id: str | Any`
    :   The type of the None singleton.

    `conditions: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `position: int | Any`
    :   The type of the None singleton.

    `raw_title: str | Any`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="TriggersListResultMeta"></a>

`TriggersListResultMeta(**data: Any)`
:   Metadata for triggers.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="User"></a>

`User(**data: Any)`
:   Zendesk Support user object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | Any`
    :   The type of the None singleton.

    `alias: str | Any | None`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `custom_role_id: int | Any | None`
    :   The type of the None singleton.

    `default_group_id: int | Any | None`
    :   The type of the None singleton.

    `details: str | Any | None`
    :   The type of the None singleton.

    `email: str | Any | None`
    :   The type of the None singleton.

    `external_id: str | Any | None`
    :   The type of the None singleton.

    `iana_time_zone: str | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `last_login_at: str | Any | None`
    :   The type of the None singleton.

    `locale: str | Any`
    :   The type of the None singleton.

    `locale_id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `moderator: bool | Any`
    :   The type of the None singleton.

    `name: str | Any`
    :   The type of the None singleton.

    `notes: str | Any | None`
    :   The type of the None singleton.

    `only_private_comments: bool | Any`
    :   The type of the None singleton.

    `organization_id: int | Any | None`
    :   The type of the None singleton.

    `permanently_deleted: bool | Any`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The type of the None singleton.

    `photo: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `report_csv: bool | Any`
    :   The type of the None singleton.

    `restricted_agent: bool | Any`
    :   The type of the None singleton.

    `role: str | Any`
    :   The type of the None singleton.

    `role_type: int | Any | None`
    :   The type of the None singleton.

    `shared: bool | Any`
    :   The type of the None singleton.

    `shared_agent: bool | Any`
    :   The type of the None singleton.

    `shared_phone_number: bool | Any | None`
    :   The type of the None singleton.

    `signature: str | Any | None`
    :   The type of the None singleton.

    `suspended: bool | Any`
    :   The type of the None singleton.

    `tags: list[str] | Any`
    :   The type of the None singleton.

    `ticket_restriction: str | Any | None`
    :   The type of the None singleton.

    `time_zone: str | Any`
    :   The type of the None singleton.

    `two_factor_auth_enabled: bool | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

    `user_fields: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `verified: bool | Any`
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

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
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

    `active: bool | None`
    :   Indicates if the user account is currently active

    `alias: str | None`
    :   Alternative name or nickname for the user

    `chat_only: bool | None`
    :   Indicates if the user can only interact via chat

    `created_at: str | None`
    :   Timestamp indicating when the user was created

    `custom_role_id: int | None`
    :   Identifier for a custom role assigned to the user

    `default_group_id: int | None`
    :   Identifier of the default group assigned to the user

    `details: str | None`
    :   Additional descriptive information about the user

    `email: str | None`
    :   Email address of the user

    `external_id: str | None`
    :   External system identifier for the user, used for integrations

    `iana_time_zone: str | None`
    :   IANA standard time zone identifier for the user

    `id: int | None`
    :   Unique identifier for the user

    `last_login_at: str | None`
    :   Timestamp of the user's most recent login

    `locale: str | None`
    :   Locale setting determining language and regional format preferences

    `locale_id: int | None`
    :   Identifier for the user's locale preference

    `model_config`
    :   The type of the None singleton.

    `moderator: bool | None`
    :   Indicates if the user has moderator privileges

    `name: str | None`
    :   Display name of the user

    `notes: str | None`
    :   Internal notes about the user, visible only to agents

    `only_private_comments: bool | None`
    :   Indicates if the user can only make private comments on tickets

    `organization_id: int | None`
    :   Identifier of the organization the user belongs to

    `permanently_deleted: bool | None`
    :   Indicates if the user has been permanently deleted from the system

    `phone: str | None`
    :   Phone number of the user

    `photo: dict[str, typing.Any] | None`
    :   Profile photo or avatar of the user

    `report_csv: bool | None`
    :   Indicates if the user receives reports in CSV format

    `restricted_agent: bool | None`
    :   Indicates if the agent has restricted access permissions

    `role: str | None`
    :   Role assigned to the user defining their permissions level

    `role_type: int | None`
    :   Type classification of the user's role

    `shared: bool | None`
    :   Indicates if the user is shared across multiple accounts

    `shared_agent: bool | None`
    :   Indicates if the user is a shared agent across multiple brands or accounts

    `shared_phone_number: bool | None`
    :   Indicates if the phone number is shared with other users

    `signature: str | None`
    :   Email signature text for the user

    `suspended: bool | None`
    :   Indicates if the user account is suspended

    `tags: list[typing.Any] | None`
    :   Labels or tags associated with the user for categorization

    `ticket_restriction: str | None`
    :   Defines which tickets the user can access based on restrictions

    `time_zone: str | None`
    :   Time zone setting for the user

    `two_factor_auth_enabled: bool | None`
    :   Indicates if two-factor authentication is enabled for the user

    `updated_at: str | None`
    :   Timestamp indicating when the user was last updated

    `url: str | None`
    :   API endpoint URL for accessing the user's detailed information

    `user_fields: dict[str, typing.Any] | None`
    :   Custom field values specific to the user, stored as key-value pairs

    `verified: bool | None`
    :   Indicates if the user's identity has been verified

<a id="View"></a>

`View(**data: Any)`
:   Zendesk Support view object
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `active: bool | Any`
    :   The type of the None singleton.

    `conditions: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `created_at: str | Any`
    :   The type of the None singleton.

    `description: str | Any | None`
    :   The type of the None singleton.

    `execution: dict[str, typing.Any] | Any`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `position: int | Any`
    :   The type of the None singleton.

    `raw_title: str | Any`
    :   The type of the None singleton.

    `restriction: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `title: str | Any`
    :   The type of the None singleton.

    `updated_at: str | Any`
    :   The type of the None singleton.

    `url: str | Any`
    :   The type of the None singleton.

<a id="ViewsListResultMeta"></a>

`ViewsListResultMeta(**data: Any)`
:   Metadata for views.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `count: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `next_page: str | Any | None`
    :   The type of the None singleton.

    `previous_page: str | Any | None`
    :   The type of the None singleton.

<a id="ZendeskSupportApiTokenAuthConfig"></a>

`ZendeskSupportApiTokenAuthConfig(**data: Any)`
:   API Token - Authenticate using email and API token
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_token: str`
    :   Your Zendesk API token from Admin Center

    `email: str`
    :   Your Zendesk account email address

    `model_config`
    :   The type of the None singleton.

<a id="ZendeskSupportCheckResult"></a>

`ZendeskSupportCheckResult(**data: Any)`
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

<a id="ZendeskSupportExecuteResult"></a>

`ZendeskSupportExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="ZendeskSupportExecuteResultWithMeta"></a>

`ZendeskSupportExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[ArticleAttachment], ArticleAttachmentsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Article], ArticlesListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Automation], AutomationsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Brand], BrandsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[DeletedTicket], DeletedTicketsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[GroupMembership], GroupMembershipsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Group], GroupsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Macro], MacrosListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[OrganizationMembership], OrganizationMembershipsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Organization], OrganizationsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[SLAPolicy], SlaPoliciesListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[SatisfactionRating], SatisfactionRatingsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Tag], TagsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[TicketAudit], TicketAuditsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[TicketComment], TicketCommentsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[TicketField], TicketFieldsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[TicketForm], TicketFormsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[TicketMetric], TicketMetricsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Ticket], TicketsListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[Trigger], TriggersListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[User], UsersListResultMeta]
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta[list[View], ViewsListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`ZendeskSupportExecuteResultWithMeta[list[ArticleAttachment], ArticleAttachmentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ArticleAttachmentsListResult"></a>

`ArticleAttachmentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[Article], ArticlesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ArticlesListResult"></a>

`ArticlesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[Automation], AutomationsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="AutomationsListResult"></a>

`AutomationsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[Brand], BrandsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="BrandsListResult"></a>

`BrandsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[DeletedTicket], DeletedTicketsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="DeletedTicketsListResult"></a>

`DeletedTicketsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[GroupMembership], GroupMembershipsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="GroupMembershipsListResult"></a>

`GroupMembershipsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[Group], GroupsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
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

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[Macro], MacrosListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MacrosListResult"></a>

`MacrosListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[OrganizationMembership], OrganizationMembershipsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrganizationMembershipsListResult"></a>

`OrganizationMembershipsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[Organization], OrganizationsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="OrganizationsListResult"></a>

`OrganizationsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[SLAPolicy], SlaPoliciesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SlaPoliciesListResult"></a>

`SlaPoliciesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[SatisfactionRating], SatisfactionRatingsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
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

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[Tag], TagsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
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

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[TicketAudit], TicketAuditsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TicketAuditsListResult"></a>

`TicketAuditsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[TicketComment], TicketCommentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TicketCommentsListResult"></a>

`TicketCommentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[TicketField], TicketFieldsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
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

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[TicketForm], TicketFormsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
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

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[TicketMetric], TicketMetricsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TicketMetricsListResult"></a>

`TicketMetricsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[Ticket], TicketsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
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

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[Trigger], TriggersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="TriggersListResult"></a>

`TriggersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[User], UsersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
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

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`ZendeskSupportExecuteResultWithMeta[list[View], ViewsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ViewsListResult"></a>

`ViewsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.zendesk_support.models.ZendeskSupportExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ZendeskSupportOauth20AuthConfig"></a>

`ZendeskSupportOauth20AuthConfig(**data: Any)`
:   OAuth 2.0 - Zendesk OAuth 2.0 authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `access_token: str`
    :   OAuth 2.0 access token

    `model_config`
    :   The type of the None singleton.

    `refresh_token: str | None`
    :   OAuth 2.0 refresh token (optional)