---
id: airbyte_agent_sdk-connectors-klaviyo-models
title: airbyte_agent_sdk.connectors.klaviyo.models
---

Module airbyte_agent_sdk.connectors.klaviyo.models
==================================================
Pydantic models for klaviyo connector.

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

    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult[CampaignsSearchData]
    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult[EmailTemplatesSearchData]
    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult[EventsSearchData]
    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult[FlowsSearchData]
    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult[ListsSearchData]
    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult[MetricsSearchData]
    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult[ProfilesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[CampaignsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[EmailTemplatesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="EmailTemplatesSearchResult"></a>

`EmailTemplatesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[EventsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="EventsSearchResult"></a>

`EventsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[FlowsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="FlowsSearchResult"></a>

`FlowsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ListsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[MetricsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MetricsSearchResult"></a>

`MetricsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ProfilesSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProfilesSearchResult"></a>

`ProfilesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Campaign"></a>

`Campaign(**data: Any)`
:   A Klaviyo campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.klaviyo.models.CampaignAttributes | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.klaviyo.models.CampaignLinks | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="CampaignAttributes"></a>

`CampaignAttributes(**data: Any)`
:   Campaign attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | Any | None`
    :   Whether campaign is archived

    `audiences: dict[str, typing.Any] | Any | None`
    :   Target audiences

    `created_at: str | Any | None`
    :   Creation timestamp

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   Campaign name

    `scheduled_at: str | Any | None`
    :   Scheduled send time

    `send_options: dict[str, typing.Any] | Any | None`
    :   Send options

    `send_strategy: dict[str, typing.Any] | Any | None`
    :   Send strategy

    `send_time: str | Any | None`
    :   Actual send time

    `status: str | Any | None`
    :   Campaign status

    `tracking_options: dict[str, typing.Any] | Any | None`
    :   Tracking options

    `updated_at: str | Any | None`
    :   Last update timestamp

<a id="CampaignLinks"></a>

`CampaignLinks(**data: Any)`
:   Related links
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | Any | None`
    :   The type of the None singleton.

<a id="CampaignsList"></a>

`CampaignsList(**data: Any)`
:   Paginated list of campaigns
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.klaviyo.models.Campaign] | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.klaviyo.models.CampaignsListLinks | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="CampaignsListLinks"></a>

`CampaignsListLinks(**data: Any)`
:   Nested schema for CampaignsList.links
    
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

    `prev: str | Any | None`
    :   The type of the None singleton.

    `self: str | Any | None`
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

    `attributes: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated_at: str | None`
    :   The type of the None singleton.

<a id="EmailTemplatesListResultMeta"></a>

`EmailTemplatesListResultMeta(**data: Any)`
:   Metadata for email_templates.Action.LIST operation
    
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

<a id="EmailTemplatesSearchData"></a>

`EmailTemplatesSearchData(**data: Any)`
:   Search result data for email_templates entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated: str | None`
    :   The type of the None singleton.

<a id="Event"></a>

`Event(**data: Any)`
:   A Klaviyo event representing an action taken by a profile
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.klaviyo.models.EventAttributes | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.klaviyo.models.EventLinks | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: airbyte_agent_sdk.connectors.klaviyo.models.EventRelationships | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="EventAttributes"></a>

`EventAttributes(**data: Any)`
:   Event attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `datetime: str | Any | None`
    :   Event datetime

    `event_properties: dict[str, typing.Any] | Any | None`
    :   Custom event properties

    `model_config`
    :   The type of the None singleton.

    `timestamp: Any`
    :   Event timestamp (can be ISO string or Unix timestamp)

    `uuid: str | Any | None`
    :   Event UUID

<a id="EventLinks"></a>

`EventLinks(**data: Any)`
:   Related links
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | Any | None`
    :   The type of the None singleton.

<a id="EventRelationships"></a>

`EventRelationships(**data: Any)`
:   Related resources
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `metric: airbyte_agent_sdk.connectors.klaviyo.models.EventRelationshipsMetric | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `profile: airbyte_agent_sdk.connectors.klaviyo.models.EventRelationshipsProfile | Any | None`
    :   The type of the None singleton.

<a id="EventRelationshipsMetric"></a>

`EventRelationshipsMetric(**data: Any)`
:   Nested schema for EventRelationships.metric
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.klaviyo.models.EventRelationshipsMetricData | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="EventRelationshipsMetricData"></a>

`EventRelationshipsMetricData(**data: Any)`
:   Nested schema for EventRelationshipsMetric.data
    
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

<a id="EventRelationshipsProfile"></a>

`EventRelationshipsProfile(**data: Any)`
:   Nested schema for EventRelationships.profile
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: airbyte_agent_sdk.connectors.klaviyo.models.EventRelationshipsProfileData | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="EventRelationshipsProfileData"></a>

`EventRelationshipsProfileData(**data: Any)`
:   Nested schema for EventRelationshipsProfile.data
    
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

<a id="EventsList"></a>

`EventsList(**data: Any)`
:   Paginated list of events
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.klaviyo.models.Event] | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.klaviyo.models.EventsListLinks | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="EventsListLinks"></a>

`EventsListLinks(**data: Any)`
:   Nested schema for EventsList.links
    
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

    `prev: str | Any | None`
    :   The type of the None singleton.

    `self: str | Any | None`
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

    `model_config`
    :   The type of the None singleton.

    `next: str | Any | None`
    :   The type of the None singleton.

<a id="EventsSearchData"></a>

`EventsSearchData(**data: Any)`
:   Search result data for events entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `datetime: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="Flow"></a>

`Flow(**data: Any)`
:   A Klaviyo flow (automated sequence)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.klaviyo.models.FlowAttributes | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.klaviyo.models.FlowLinks | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="FlowAttributes"></a>

`FlowAttributes(**data: Any)`
:   Flow attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archived: bool | Any | None`
    :   Whether flow is archived

    `created: str | Any | None`
    :   Creation timestamp

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   Flow name

    `status: str | Any | None`
    :   Flow status (draft, manual, live)

    `trigger_type: str | Any | None`
    :   Type of trigger for the flow

    `updated: str | Any | None`
    :   Last update timestamp

<a id="FlowLinks"></a>

`FlowLinks(**data: Any)`
:   Related links
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | Any | None`
    :   The type of the None singleton.

<a id="FlowsList"></a>

`FlowsList(**data: Any)`
:   Paginated list of flows
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.klaviyo.models.Flow] | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.klaviyo.models.FlowsListLinks | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="FlowsListLinks"></a>

`FlowsListLinks(**data: Any)`
:   Nested schema for FlowsList.links
    
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

    `prev: str | Any | None`
    :   The type of the None singleton.

    `self: str | Any | None`
    :   The type of the None singleton.

<a id="FlowsListResultMeta"></a>

`FlowsListResultMeta(**data: Any)`
:   Metadata for flows.Action.LIST operation
    
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

<a id="FlowsSearchData"></a>

`FlowsSearchData(**data: Any)`
:   Search result data for flows entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated: str | None`
    :   The type of the None singleton.

<a id="KlaviyoAuthConfig"></a>

`KlaviyoAuthConfig(**data: Any)`
:   Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your Klaviyo private API key

    `model_config`
    :   The type of the None singleton.

<a id="KlaviyoCheckResult"></a>

`KlaviyoCheckResult(**data: Any)`
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

<a id="KlaviyoExecuteResult"></a>

`KlaviyoExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="KlaviyoExecuteResultWithMeta"></a>

`KlaviyoExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta[list[Event], EventsListResultMeta]
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta[list[Flow], FlowsListResultMeta]
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta[list[List], ListsListResultMeta]
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta[list[Metric], MetricsListResultMeta]
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta[list[Profile], ProfilesListResultMeta]
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta[list[Template], EmailTemplatesListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`KlaviyoExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResult
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

    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`KlaviyoExecuteResultWithMeta[list[Event], EventsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResult
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

    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`KlaviyoExecuteResultWithMeta[list[Flow], FlowsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="FlowsListResult"></a>

`FlowsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`KlaviyoExecuteResultWithMeta[list[List], ListsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResult
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

    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`KlaviyoExecuteResultWithMeta[list[Metric], MetricsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="MetricsListResult"></a>

`MetricsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`KlaviyoExecuteResultWithMeta[list[Profile], ProfilesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ProfilesListResult"></a>

`ProfilesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`KlaviyoExecuteResultWithMeta[list[Template], EmailTemplatesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="EmailTemplatesListResult"></a>

`EmailTemplatesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.klaviyo.models.KlaviyoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="List"></a>

`List(**data: Any)`
:   A Klaviyo list for organizing profiles
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.klaviyo.models.ListAttributes | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.klaviyo.models.ListLinks | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="ListAttributes"></a>

`ListAttributes(**data: Any)`
:   List attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: str | Any | None`
    :   Creation timestamp

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   List name

    `opt_in_process: str | Any | None`
    :   Opt-in process type

    `updated: str | Any | None`
    :   Last update timestamp

<a id="ListLinks"></a>

`ListLinks(**data: Any)`
:   Related links
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | Any | None`
    :   The type of the None singleton.

<a id="ListsList"></a>

`ListsList(**data: Any)`
:   Paginated list of lists
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.klaviyo.models.List] | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.klaviyo.models.ListsListLinks | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ListsListLinks"></a>

`ListsListLinks(**data: Any)`
:   Nested schema for ListsList.links
    
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

    `prev: str | Any | None`
    :   The type of the None singleton.

    `self: str | Any | None`
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

    `attributes: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated: str | None`
    :   The type of the None singleton.

<a id="Metric"></a>

`Metric(**data: Any)`
:   A Klaviyo metric (event type)
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.klaviyo.models.MetricAttributes | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.klaviyo.models.MetricLinks | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="MetricAttributes"></a>

`MetricAttributes(**data: Any)`
:   Metric attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: str | Any | None`
    :   Creation timestamp

    `integration: airbyte_agent_sdk.connectors.klaviyo.models.MetricAttributesIntegration | Any | None`
    :   Integration information

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   Metric name

    `updated: str | Any | None`
    :   Last update timestamp

<a id="MetricAttributesIntegration"></a>

`MetricAttributesIntegration(**data: Any)`
:   Integration information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `category: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

<a id="MetricLinks"></a>

`MetricLinks(**data: Any)`
:   Related links
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | Any | None`
    :   The type of the None singleton.

<a id="MetricsList"></a>

`MetricsList(**data: Any)`
:   Paginated list of metrics
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.klaviyo.models.Metric] | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.klaviyo.models.MetricsListLinks | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="MetricsListLinks"></a>

`MetricsListLinks(**data: Any)`
:   Nested schema for MetricsList.links
    
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

    `prev: str | Any | None`
    :   The type of the None singleton.

    `self: str | Any | None`
    :   The type of the None singleton.

<a id="MetricsListResultMeta"></a>

`MetricsListResultMeta(**data: Any)`
:   Metadata for metrics.Action.LIST operation
    
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

<a id="MetricsSearchData"></a>

`MetricsSearchData(**data: Any)`
:   Search result data for metrics entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated: str | None`
    :   The type of the None singleton.

<a id="Profile"></a>

`Profile(**data: Any)`
:   A Klaviyo profile representing a contact
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.klaviyo.models.ProfileAttributes | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.klaviyo.models.ProfileLinks | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="ProfileAttributes"></a>

`ProfileAttributes(**data: Any)`
:   Profile attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: str | Any | None`
    :   Creation timestamp

    `email: str | Any | None`
    :   Email address

    `external_id: str | Any | None`
    :   External identifier

    `first_name: str | Any | None`
    :   First name

    `image: str | Any | None`
    :   Profile image URL

    `last_name: str | Any | None`
    :   Last name

    `location: airbyte_agent_sdk.connectors.klaviyo.models.ProfileAttributesLocation | Any | None`
    :   Location information

    `model_config`
    :   The type of the None singleton.

    `organization: str | Any | None`
    :   Organization name

    `phone_number: str | Any | None`
    :   Phone number

    `properties: dict[str, typing.Any] | Any | None`
    :   Custom properties

    `title: str | Any | None`
    :   Job title

    `updated: str | Any | None`
    :   Last update timestamp

<a id="ProfileAttributesLocation"></a>

`ProfileAttributesLocation(**data: Any)`
:   Location information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address1: str | Any | None`
    :   The type of the None singleton.

    `address2: str | Any | None`
    :   The type of the None singleton.

    `city: str | Any | None`
    :   The type of the None singleton.

    `country: str | Any | None`
    :   The type of the None singleton.

    `latitude: float | Any | None`
    :   The type of the None singleton.

    `longitude: float | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `region: str | Any | None`
    :   The type of the None singleton.

    `timezone: str | Any | None`
    :   The type of the None singleton.

    `zip: str | Any | None`
    :   The type of the None singleton.

<a id="ProfileLinks"></a>

`ProfileLinks(**data: Any)`
:   Related links
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | Any | None`
    :   The type of the None singleton.

<a id="ProfilesList"></a>

`ProfilesList(**data: Any)`
:   Paginated list of profiles
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.klaviyo.models.Profile] | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.klaviyo.models.ProfilesListLinks | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ProfilesListLinks"></a>

`ProfilesListLinks(**data: Any)`
:   Nested schema for ProfilesList.links
    
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

    `prev: str | Any | None`
    :   The type of the None singleton.

    `self: str | Any | None`
    :   The type of the None singleton.

<a id="ProfilesListResultMeta"></a>

`ProfilesListResultMeta(**data: Any)`
:   Metadata for profiles.Action.LIST operation
    
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

<a id="ProfilesSearchData"></a>

`ProfilesSearchData(**data: Any)`
:   Search result data for profiles entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `links: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `relationships: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `segments: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated: str | None`
    :   The type of the None singleton.

<a id="Template"></a>

`Template(**data: Any)`
:   A Klaviyo email template
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attributes: airbyte_agent_sdk.connectors.klaviyo.models.TemplateAttributes | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.klaviyo.models.TemplateLinks | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="TemplateAttributes"></a>

`TemplateAttributes(**data: Any)`
:   Template attributes
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created: str | Any | None`
    :   Creation timestamp

    `editor_type: str | Any | None`
    :   Editor type used to create template

    `html: str | Any | None`
    :   HTML content

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   Template name

    `text: str | Any | None`
    :   Plain text content

    `updated: str | Any | None`
    :   Last update timestamp

<a id="TemplateLinks"></a>

`TemplateLinks(**data: Any)`
:   Related links
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `self: str | Any | None`
    :   The type of the None singleton.

<a id="TemplatesList"></a>

`TemplatesList(**data: Any)`
:   Paginated list of templates
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[airbyte_agent_sdk.connectors.klaviyo.models.Template] | Any`
    :   The type of the None singleton.

    `links: airbyte_agent_sdk.connectors.klaviyo.models.TemplatesListLinks | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="TemplatesListLinks"></a>

`TemplatesListLinks(**data: Any)`
:   Nested schema for TemplatesList.links
    
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

    `prev: str | Any | None`
    :   The type of the None singleton.

    `self: str | Any | None`
    :   The type of the None singleton.