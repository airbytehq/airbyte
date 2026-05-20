---
id: airbyte_agent_sdk-connectors-customer_io-models
title: airbyte_agent_sdk.connectors.customer_io.models
---

Module airbyte_agent_sdk.connectors.customer_io.models
======================================================
Pydantic models for customer-io connector.

This module contains Pydantic models used for authentication configuration
and response envelope types.

Classes
-------

<a id="ActivitiesListResultMeta"></a>

`ActivitiesListResultMeta(**data: Any)`
:   Metadata for activities.Action.LIST operation
    
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

<a id="Activity"></a>

`Activity(**data: Any)`
:   Activity type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `customer_id: str | None`
    :   The type of the None singleton.

    `customer_identifiers: airbyte_agent_sdk.connectors.customer_io.models.ActivityCustomerIdentifiers | None`
    :   The type of the None singleton.

    `data: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `delivery_id: str | None`
    :   The type of the None singleton.

    `delivery_type: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `timestamp: int | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="ActivityCustomerIdentifiers"></a>

`ActivityCustomerIdentifiers(**data: Any)`
:   Customer identification details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cio_id: str | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `model_config`
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

    * airbyte_agent_sdk.connectors.customer_io.models.AirbyteSearchResult[CampaignActionsSearchData]
    * airbyte_agent_sdk.connectors.customer_io.models.AirbyteSearchResult[CampaignsSearchData]
    * airbyte_agent_sdk.connectors.customer_io.models.AirbyteSearchResult[NewslettersSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.customer_io.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

`AirbyteSearchResult[CampaignActionsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CampaignActionsSearchResult"></a>

`CampaignActionsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[CampaignsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.customer_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[NewslettersSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="NewslettersSearchResult"></a>

`NewslettersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="BroadcastTriggerParams"></a>

`BroadcastTriggerParams(**data: Any)`
:   BroadcastTriggerParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `data_file_url: str | None`
    :   The type of the None singleton.

    `email_add_duplicates: bool | None`
    :   The type of the None singleton.

    `email_ignore_missing: bool | None`
    :   The type of the None singleton.

    `emails: list[str] | None`
    :   The type of the None singleton.

    `id_ignore_missing: bool | None`
    :   The type of the None singleton.

    `ids: list[str] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `per_user_data: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `recipients: dict[str, typing.Any] | None`
    :   The type of the None singleton.

<a id="BroadcastTriggerResponse"></a>

`BroadcastTriggerResponse(**data: Any)`
:   BroadcastTriggerResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Campaign"></a>

`Campaign(**data: Any)`
:   Campaign type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `actions: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `active: bool | None`
    :   The type of the None singleton.

    `created: int | None`
    :   The type of the None singleton.

    `created_by: str | None`
    :   The type of the None singleton.

    `date_attribute: str | None`
    :   The type of the None singleton.

    `deduplicate_id: str | None`
    :   The type of the None singleton.

    `event_name: str | None`
    :   The type of the None singleton.

    `filter_segment_ids: list[int] | None`
    :   The type of the None singleton.

    `first_started: int | None`
    :   The type of the None singleton.

    `frequency: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `msg_templates: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `scheduled_start: int | None`
    :   The type of the None singleton.

    `scheduled_start_should_backfill: bool | None`
    :   The type of the None singleton.

    `scheduled_stop: int | None`
    :   The type of the None singleton.

    `scheduled_stop_should_sunset: bool | None`
    :   The type of the None singleton.

    `start_hour: int | None`
    :   The type of the None singleton.

    `start_minutes: int | None`
    :   The type of the None singleton.

    `state: str | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

    `timezone: str | None`
    :   The type of the None singleton.

    `trigger_segment_ids: list[int] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated: int | None`
    :   The type of the None singleton.

    `use_customer_timezone: bool | None`
    :   The type of the None singleton.

<a id="CampaignAction"></a>

`CampaignAction(**data: Any)`
:   CampaignAction type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bcc: str | None`
    :   The type of the None singleton.

    `body: str | None`
    :   The type of the None singleton.

    `body_amp: str | None`
    :   The type of the None singleton.

    `body_plain: str | None`
    :   The type of the None singleton.

    `broadcast_id: int | None`
    :   The type of the None singleton.

    `campaign_id: int | None`
    :   The type of the None singleton.

    `created: int | None`
    :   The type of the None singleton.

    `deduplicate_id: str | None`
    :   The type of the None singleton.

    `editor: str | None`
    :   The type of the None singleton.

    `fake_bcc: bool | None`
    :   The type of the None singleton.

    `from_: str | None`
    :   The type of the None singleton.

    `from_id: int | None`
    :   The type of the None singleton.

    `headers: str | None`
    :   The type of the None singleton.

    `id: typing.Any | None`
    :   The type of the None singleton.

    `language: str | None`
    :   The type of the None singleton.

    `layout: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `parent_action_id: int | None`
    :   The type of the None singleton.

    `preheader_text: str | None`
    :   The type of the None singleton.

    `preprocessor: str | None`
    :   The type of the None singleton.

    `recipient: str | None`
    :   The type of the None singleton.

    `reply_to: str | None`
    :   The type of the None singleton.

    `reply_to_id: int | None`
    :   The type of the None singleton.

    `sending_state: str | None`
    :   The type of the None singleton.

    `subject: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated: int | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="CampaignActionsListResultMeta"></a>

`CampaignActionsListResultMeta(**data: Any)`
:   Metadata for campaign_actions.Action.LIST operation
    
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

<a id="CampaignActionsSearchData"></a>

`CampaignActionsSearchData(**data: Any)`
:   Search result data for campaign_actions entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bcc: str | None`
    :   BCC addresses

    `body: str | None`
    :   Action body content (HTML for emails)

    `campaign_id: int | None`
    :   Parent campaign ID

    `created: int | None`
    :   Creation timestamp (Unix)

    `deduplicate_id: str | None`
    :   Deduplication identifier

    `editor: str | None`
    :   Editor used to create the action

    `fake_bcc: bool | None`
    :   Whether to use fake BCC

    `from_: str | None`
    :   From address

    `from_id: str | None`
    :   Sender identity ID

    `headers: str | None`
    :   Custom email headers as JSON

    `id: str | None`
    :   Unique action identifier

    `language: str | None`
    :   Language variant

    `layout: str | None`
    :   Layout template used

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Action name

    `parent_action_id: int | None`
    :   Parent action ID for language variants

    `preheader_text: str | None`
    :   Email preheader/preview text

    `preprocessor: str | None`
    :   CSS preprocessor setting

    `recipient: str | None`
    :   Recipient address

    `recipient_environment_id: int | None`
    :   Recipient environment ID

    `reply_to: str | None`
    :   Reply-to address

    `reply_to_id: str | None`
    :   Reply-to sender identity ID

    `request_method: str | None`
    :   HTTP request method for webhook actions

    `sending_state: str | None`
    :   Sending behavior (automatic or draft)

    `subject: str | None`
    :   Email subject line

    `type_: str | None`
    :   Action type (email, webhook, twilio, push, slack, in_app, whatsapp)

    `updated: int | None`
    :   Last update timestamp (Unix)

    `url: str | None`
    :   Webhook URL (for webhook actions)

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

    `actions: list[typing.Any] | None`
    :   Actions defined in this campaign

    `active: bool | None`
    :   Whether the campaign is active

    `created: int | None`
    :   Creation timestamp (Unix)

    `created_by: str | None`
    :   Who created the campaign

    `date_attribute: str | None`
    :   Date attribute used for date-triggered campaigns

    `deduplicate_id: str | None`
    :   Deduplication identifier

    `event_name: str | None`
    :   Event name that triggers the campaign

    `first_started: int | None`
    :   When the campaign was first started (Unix)

    `frequency: str | None`
    :   How frequently a person can receive this campaign

    `id: int | None`
    :   Unique campaign identifier

    `model_config`
    :   The type of the None singleton.

    `msg_templates: list[typing.Any] | None`
    :   Message templates used in the campaign

    `name: str | None`
    :   Campaign name

    `start_hour: int | None`
    :   Hour of the day to trigger

    `start_minutes: int | None`
    :   Minute of the hour to trigger

    `state: str | None`
    :   Campaign status (draft, active, stopped)

    `tags: list[typing.Any] | None`
    :   Tags associated with the campaign

    `timezone: str | None`
    :   Timezone for trigger scheduling

    `trigger_segment_ids: list[typing.Any] | None`
    :   Segment IDs that trigger this campaign

    `type_: str | None`
    :   Campaign trigger type

    `updated: int | None`
    :   Last update timestamp (Unix)

    `use_customer_timezone: bool | None`
    :   Whether to use the customer's timezone

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

    `bytes: int | None`
    :   The type of the None singleton.

    `created_at: int | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `rows: int | None`
    :   The type of the None singleton.

    `schema_: list[str] | None`
    :   The type of the None singleton.

    `updated_at: int | None`
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

    `data: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="CollectionUpdateParams"></a>

`CollectionUpdateParams(**data: Any)`
:   CollectionUpdateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `data: list[dict[str, typing.Any]] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `url: str | None`
    :   The type of the None singleton.

<a id="CustomerIoAuthConfig"></a>

`CustomerIoAuthConfig(**data: Any)`
:   App API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `app_api_key: str`
    :   Your Customer.io App API key. Generate one in your workspace settings at Settings > API Credentials > App API Key.

    `model_config`
    :   The type of the None singleton.

<a id="CustomerIoCheckResult"></a>

`CustomerIoCheckResult(**data: Any)`
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

<a id="CustomerIoExecuteResult"></a>

`CustomerIoExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult[list[Campaign]]
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult[list[Collection]]
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult[list[Export]]
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult[list[ReportingWebhook]]
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult[list[Segment]]
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult[list[Snippet]]

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="CustomerIoExecuteResultWithMeta"></a>

`CustomerIoExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta[list[Activity], ActivitiesListResultMeta]
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta[list[CampaignAction], CampaignActionsListResultMeta]
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta[list[Message], MessagesListResultMeta]
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta[list[Newsletter], NewslettersListResultMeta]
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta[list[SenderIdentity], SenderIdentitiesListResultMeta]

    ### Class variables

    `meta: ~S | None`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`CustomerIoExecuteResultWithMeta[list[Activity], ActivitiesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ActivitiesListResult"></a>

`ActivitiesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`CustomerIoExecuteResultWithMeta[list[CampaignAction], CampaignActionsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CampaignActionsListResult"></a>

`CampaignActionsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`CustomerIoExecuteResultWithMeta[list[Message], MessagesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
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

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`CustomerIoExecuteResultWithMeta[list[Newsletter], NewslettersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="NewslettersListResult"></a>

`NewslettersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`CustomerIoExecuteResultWithMeta[list[SenderIdentity], SenderIdentitiesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SenderIdentitiesListResult"></a>

`SenderIdentitiesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`CustomerIoExecuteResult[list[Campaign]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CampaignsListResult"></a>

`CampaignsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`CustomerIoExecuteResult[list[Collection]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="CollectionsListResult"></a>

`CollectionsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`CustomerIoExecuteResult[list[Export]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ExportsListResult"></a>

`ExportsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`CustomerIoExecuteResult[list[ReportingWebhook]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ReportingWebhooksListResult"></a>

`ReportingWebhooksListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`CustomerIoExecuteResult[list[Segment]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
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

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`CustomerIoExecuteResult[list[Snippet]](**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SnippetsListResult"></a>

`SnippetsListResult(**data: Any)`
:   Response envelope with data only.
    
    Used for actions that return data without metadata.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.customer_io.models.CustomerIoExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="CustomerIoReplicationConfig"></a>

`CustomerIoReplicationConfig(**data: Any)`
:   Replication Configuration - Settings for data replication from Customer.io.
    
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

<a id="Export"></a>

`Export(**data: Any)`
:   Export type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: int | None`
    :   The type of the None singleton.

    `deduplicate_id: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `downloads: int | None`
    :   The type of the None singleton.

    `failed: bool | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `status: str | None`
    :   The type of the None singleton.

    `total: int | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated_at: int | None`
    :   The type of the None singleton.

    `user_email: str | None`
    :   The type of the None singleton.

    `user_id: int | None`
    :   The type of the None singleton.

<a id="ExportCreateParams"></a>

`ExportCreateParams(**data: Any)`
:   ExportCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `filters: dict[str, typing.Any]`
    :   The type of the None singleton.

    `model_config`
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

    `action_id: int | None`
    :   The type of the None singleton.

    `broadcast_id: int | None`
    :   The type of the None singleton.

    `campaign_id: int | None`
    :   The type of the None singleton.

    `content_id: int | None`
    :   The type of the None singleton.

    `created: int | None`
    :   The type of the None singleton.

    `customer_id: str | None`
    :   The type of the None singleton.

    `customer_identifiers: airbyte_agent_sdk.connectors.customer_io.models.MessageCustomerIdentifiers | None`
    :   The type of the None singleton.

    `deduplicate_id: str | None`
    :   The type of the None singleton.

    `failure_message: str | None`
    :   The type of the None singleton.

    `forgotten: bool | None`
    :   The type of the None singleton.

    `id: str | None`
    :   The type of the None singleton.

    `message_template_id: int | None`
    :   The type of the None singleton.

    `metrics: airbyte_agent_sdk.connectors.customer_io.models.MessageMetrics | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `newsletter_id: int | None`
    :   The type of the None singleton.

    `parent_action_id: int | None`
    :   The type of the None singleton.

    `recipient: str | None`
    :   The type of the None singleton.

    `subject: str | None`
    :   The type of the None singleton.

    `trigger_event_id: str | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

<a id="MessageCustomerIdentifiers"></a>

`MessageCustomerIdentifiers(**data: Any)`
:   Customer identification details
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `cio_id: str | None`
    :   Customer.io internal ID

    `email: str | None`
    :   Person's email address

    `id: str | None`
    :   Person's ID

    `model_config`
    :   The type of the None singleton.

<a id="MessageMetrics"></a>

`MessageMetrics(**data: Any)`
:   Delivery metrics timestamps
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `bounced: int | None`
    :   The type of the None singleton.

    `clicked: int | None`
    :   The type of the None singleton.

    `converted: int | None`
    :   The type of the None singleton.

    `created: int | None`
    :   The type of the None singleton.

    `delivered: int | None`
    :   The type of the None singleton.

    `drafted: int | None`
    :   The type of the None singleton.

    `failed: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `opened: int | None`
    :   The type of the None singleton.

    `sent: int | None`
    :   The type of the None singleton.

    `undeliverable: int | None`
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

    `model_config`
    :   The type of the None singleton.

    `next: str | None`
    :   The type of the None singleton.

<a id="Newsletter"></a>

`Newsletter(**data: Any)`
:   Newsletter type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content_ids: list[int] | None`
    :   The type of the None singleton.

    `created: int | None`
    :   The type of the None singleton.

    `deduplicate_id: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `recipient_segment_ids: list[int] | None`
    :   The type of the None singleton.

    `sent_at: int | None`
    :   The type of the None singleton.

    `subscription_topic_id: int | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated: int | None`
    :   The type of the None singleton.

<a id="NewslettersListResultMeta"></a>

`NewslettersListResultMeta(**data: Any)`
:   Metadata for newsletters.Action.LIST operation
    
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

<a id="NewslettersSearchData"></a>

`NewslettersSearchData(**data: Any)`
:   Search result data for newsletters entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `content_ids: list[typing.Any] | None`
    :   Content variant IDs for this newsletter

    `created: int | None`
    :   Creation timestamp (Unix)

    `deduplicate_id: str | None`
    :   Deduplication identifier

    `id: int | None`
    :   Unique newsletter identifier

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   Newsletter name

    `sent_at: int | None`
    :   When the newsletter was last sent (Unix)

    `tags: list[typing.Any] | None`
    :   Tags associated with the newsletter

    `type_: str | None`
    :   Channel type (email, webhook, twilio, push, in_app, inbox)

    `updated: int | None`
    :   Last update timestamp (Unix)

<a id="ReportingWebhook"></a>

`ReportingWebhook(**data: Any)`
:   ReportingWebhook type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `disabled: bool | None`
    :   The type of the None singleton.

    `endpoint: str | None`
    :   The type of the None singleton.

    `events: list[str] | None`
    :   The type of the None singleton.

    `full_resolution: bool | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `with_content: bool | None`
    :   The type of the None singleton.

<a id="ReportingWebhookCreateParams"></a>

`ReportingWebhookCreateParams(**data: Any)`
:   ReportingWebhookCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `disabled: bool | None`
    :   The type of the None singleton.

    `endpoint: str`
    :   The type of the None singleton.

    `events: list[str]`
    :   The type of the None singleton.

    `full_resolution: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `with_content: bool | None`
    :   The type of the None singleton.

<a id="ReportingWebhookUpdateParams"></a>

`ReportingWebhookUpdateParams(**data: Any)`
:   ReportingWebhookUpdateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `disabled: bool | None`
    :   The type of the None singleton.

    `endpoint: str`
    :   The type of the None singleton.

    `events: list[str]`
    :   The type of the None singleton.

    `full_resolution: bool | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `with_content: bool | None`
    :   The type of the None singleton.

<a id="Segment"></a>

`Segment(**data: Any)`
:   Segment type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `conditions: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `created_at: int | None`
    :   The type of the None singleton.

    `deduplicate_id: str | None`
    :   The type of the None singleton.

    `description: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `progress: int | None`
    :   The type of the None singleton.

    `state: str | None`
    :   The type of the None singleton.

    `tags: list[str] | None`
    :   The type of the None singleton.

    `type_: str | None`
    :   The type of the None singleton.

    `updated_at: int | None`
    :   The type of the None singleton.

<a id="SegmentCreateParams"></a>

`SegmentCreateParams(**data: Any)`
:   SegmentCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `segment: airbyte_agent_sdk.connectors.customer_io.models.SegmentCreateParamsSegment`
    :   The type of the None singleton.

<a id="SegmentCreateParamsSegment"></a>

`SegmentCreateParamsSegment(**data: Any)`
:   Nested schema for SegmentCreateParams.segment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `description: str | None`
    :   Optional description of the segment

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   Name of the manual segment

<a id="SenderIdentitiesListResultMeta"></a>

`SenderIdentitiesListResultMeta(**data: Any)`
:   Metadata for sender_identities.Action.LIST operation
    
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

<a id="SenderIdentity"></a>

`SenderIdentity(**data: Any)`
:   SenderIdentity type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address: str | None`
    :   The type of the None singleton.

    `auto_generated: bool | None`
    :   The type of the None singleton.

    `deduplicate_id: str | None`
    :   The type of the None singleton.

    `email: str | None`
    :   The type of the None singleton.

    `id: int | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The type of the None singleton.

    `phone: str | None`
    :   The type of the None singleton.

    `template_type: str | None`
    :   The type of the None singleton.

<a id="Snippet"></a>

`Snippet(**data: Any)`
:   Snippet type definition
    
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

    `updated_at: int | None`
    :   The type of the None singleton.

    `value: str | None`
    :   The type of the None singleton.

<a id="SnippetCreateParams"></a>

`SnippetCreateParams(**data: Any)`
:   SnippetCreateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

<a id="SnippetUpdateParams"></a>

`SnippetUpdateParams(**data: Any)`
:   SnippetUpdateParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

    `value: str`
    :   The type of the None singleton.

<a id="TransactionalEmailParams"></a>

`TransactionalEmailParams(**data: Any)`
:   TransactionalEmailParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `attachments: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `bcc: str | None`
    :   The type of the None singleton.

    `body: str | None`
    :   The type of the None singleton.

    `body_plain: str | None`
    :   The type of the None singleton.

    `disable_message_retention: bool | None`
    :   The type of the None singleton.

    `from_: str | None`
    :   The type of the None singleton.

    `headers: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `identifiers: dict[str, typing.Any]`
    :   The type of the None singleton.

    `message_data: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `preheader_text: str | None`
    :   The type of the None singleton.

    `queue_draft: bool | None`
    :   The type of the None singleton.

    `reply_to: str | None`
    :   The type of the None singleton.

    `send_at: int | None`
    :   The type of the None singleton.

    `send_to_unsubscribed: bool | None`
    :   The type of the None singleton.

    `subject: str | None`
    :   The type of the None singleton.

    `to: str`
    :   The type of the None singleton.

    `tracked: bool | None`
    :   The type of the None singleton.

    `transactional_message_id: typing.Any | None`
    :   The type of the None singleton.

<a id="TransactionalInboxMessageParams"></a>

`TransactionalInboxMessageParams(**data: Any)`
:   TransactionalInboxMessageParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `identifiers: dict[str, typing.Any]`
    :   The type of the None singleton.

    `message_data: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `transactional_message_id: Any`
    :   The type of the None singleton.

<a id="TransactionalPushParams"></a>

`TransactionalPushParams(**data: Any)`
:   TransactionalPushParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `custom_data: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `custom_payload: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `disable_message_retention: bool | None`
    :   The type of the None singleton.

    `identifiers: dict[str, typing.Any]`
    :   The type of the None singleton.

    `image_url: str | None`
    :   The type of the None singleton.

    `link: str | None`
    :   The type of the None singleton.

    `message: str | None`
    :   The type of the None singleton.

    `message_data: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `queue_draft: bool | None`
    :   The type of the None singleton.

    `send_at: int | None`
    :   The type of the None singleton.

    `send_to_unsubscribed: bool | None`
    :   The type of the None singleton.

    `sound: str | None`
    :   The type of the None singleton.

    `title: str | None`
    :   The type of the None singleton.

    `to: str | None`
    :   The type of the None singleton.

    `transactional_message_id: typing.Any | None`
    :   The type of the None singleton.

<a id="TransactionalSendResponse"></a>

`TransactionalSendResponse(**data: Any)`
:   TransactionalSendResponse type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `delivery_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `queued_at: int | None`
    :   The type of the None singleton.

<a id="TransactionalSmsParams"></a>

`TransactionalSmsParams(**data: Any)`
:   TransactionalSmsParams type definition
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `disable_message_retention: bool | None`
    :   The type of the None singleton.

    `from_: str | None`
    :   The type of the None singleton.

    `identifiers: dict[str, typing.Any]`
    :   The type of the None singleton.

    `message_data: dict[str, typing.Any] | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `queue_draft: bool | None`
    :   The type of the None singleton.

    `send_to_unsubscribed: bool | None`
    :   The type of the None singleton.

    `to: str`
    :   The type of the None singleton.

    `tracked: bool | None`
    :   The type of the None singleton.

    `transactional_message_id: Any`
    :   The type of the None singleton.