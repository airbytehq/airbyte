---
id: airbyte_agent_sdk-connectors-mailchimp-models
title: airbyte_agent_sdk.connectors.mailchimp.models
---

Module airbyte_agent_sdk.connectors.mailchimp.models
====================================================
Pydantic models for mailchimp connector.

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

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[CampaignsSearchData]
    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[EmailActivitySearchData]
    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[ListsSearchData]
    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[ReportsSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchMeta`
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

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[EmailActivitySearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="EmailActivitySearchResult"></a>

`EmailActivitySearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ListsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult
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

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

`AirbyteSearchResult[ReportsSearchData](**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ReportsSearchResult"></a>

`ReportsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Automation"></a>

`Automation(**data: Any)`
:   A summary of an individual Automation workflow's settings and content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `create_time: str | Any | None`
    :   The type of the None singleton.

    `emails_sent: int | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `recipients: airbyte_agent_sdk.connectors.mailchimp.models.AutomationRecipients | Any | None`
    :   The type of the None singleton.

    `report_summary: airbyte_agent_sdk.connectors.mailchimp.models.AutomationReportSummary | Any | None`
    :   The type of the None singleton.

    `settings: airbyte_agent_sdk.connectors.mailchimp.models.AutomationSettings | Any | None`
    :   The type of the None singleton.

    `start_time: str | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `tracking: airbyte_agent_sdk.connectors.mailchimp.models.AutomationTracking | Any | None`
    :   The type of the None singleton.

<a id="AutomationRecipients"></a>

`AutomationRecipients(**data: Any)`
:   List settings for the Automation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `list_id: str | Any | None`
    :   The unique list id

    `list_is_active: bool | Any | None`
    :   The status of the list used

    `list_name: str | Any | None`
    :   The name of the list

    `model_config`
    :   The type of the None singleton.

    `segment_opts: airbyte_agent_sdk.connectors.mailchimp.models.AutomationRecipientsSegmentOpts | Any | None`
    :   An object representing all segmentation options

    `store_id: str | Any | None`
    :   The id of the store

<a id="AutomationRecipientsSegmentOpts"></a>

`AutomationRecipientsSegmentOpts(**data: Any)`
:   An object representing all segmentation options
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `conditions: list[dict[str, typing.Any]] | Any | None`
    :   Segment match conditions

    `match: str | Any | None`
    :   Segment match type

    `model_config`
    :   The type of the None singleton.

    `saved_segment_id: int | Any | None`
    :   The id for an existing saved segment

<a id="AutomationReportSummary"></a>

`AutomationReportSummary(**data: Any)`
:   A summary of opens and clicks for sent campaigns
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `click_rate: float | Any | None`
    :   The number of unique clicks divided by the total number of successful deliveries

    `clicks: int | Any | None`
    :   The total number of clicks for an campaign

    `model_config`
    :   The type of the None singleton.

    `open_rate: float | Any | None`
    :   The number of unique opens divided by the total number of successful deliveries

    `opens: int | Any | None`
    :   The total number of opens for a campaign

    `subscriber_clicks: int | Any | None`
    :   The number of unique clicks

    `unique_opens: int | Any | None`
    :   The number of unique opens

<a id="AutomationSettings"></a>

`AutomationSettings(**data: Any)`
:   The settings for the Automation workflow
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `authenticate: bool | Any | None`
    :   Whether Mailchimp authenticated the Automation

    `auto_footer: bool | Any | None`
    :   Whether to automatically append Mailchimp's default footer

    `from_name: str | Any | None`
    :   The from name for the Automation

    `inline_css: bool | Any | None`
    :   Whether to automatically inline the CSS

    `model_config`
    :   The type of the None singleton.

    `reply_to: str | Any | None`
    :   The reply-to email address for the Automation

    `title: str | Any | None`
    :   The title of the Automation

    `to_name: str | Any | None`
    :   The Automation's custom to name

    `use_conversation: bool | Any | None`
    :   Whether to use Mailchimp Conversation feature

<a id="AutomationTracking"></a>

`AutomationTracking(**data: Any)`
:   The tracking options for the Automation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `clicktale: str | Any | None`
    :   The custom slug for ClickTale tracking

    `ecomm360: bool | Any | None`
    :   Whether to enable eCommerce360 tracking

    `goal_tracking: bool | Any | None`
    :   Whether to enable Goal tracking

    `google_analytics: str | Any | None`
    :   The custom slug for Google Analytics tracking

    `html_clicks: bool | Any | None`
    :   Whether to track clicks in the HTML version

    `model_config`
    :   The type of the None singleton.

    `opens: bool | Any | None`
    :   Whether to track opens

    `text_clicks: bool | Any | None`
    :   Whether to track clicks in the plain-text version

<a id="AutomationsList"></a>

`AutomationsList(**data: Any)`
:   A summary of the Automations for an account
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `automations: list[airbyte_agent_sdk.connectors.mailchimp.models.Automation] | Any`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_items: int | Any`
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

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Campaign"></a>

`Campaign(**data: Any)`
:   A summary of an individual campaign's settings and content
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `archive_url: str | Any | None`
    :   The type of the None singleton.

    `content_type: str | Any | None`
    :   The type of the None singleton.

    `create_time: str | Any | None`
    :   The type of the None singleton.

    `delivery_status: airbyte_agent_sdk.connectors.mailchimp.models.CampaignDeliveryStatus | Any | None`
    :   The type of the None singleton.

    `emails_sent: int | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `long_archive_url: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `needs_block_refresh: bool | Any | None`
    :   The type of the None singleton.

    `parent_campaign_id: str | Any | None`
    :   The type of the None singleton.

    `recipients: airbyte_agent_sdk.connectors.mailchimp.models.CampaignRecipients | Any | None`
    :   The type of the None singleton.

    `report_summary: airbyte_agent_sdk.connectors.mailchimp.models.CampaignReportSummary | Any | None`
    :   The type of the None singleton.

    `resendable: bool | Any | None`
    :   The type of the None singleton.

    `send_time: str | Any | None`
    :   The type of the None singleton.

    `settings: airbyte_agent_sdk.connectors.mailchimp.models.CampaignSettings | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `tracking: airbyte_agent_sdk.connectors.mailchimp.models.CampaignTracking | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `web_id: int | Any | None`
    :   The type of the None singleton.

<a id="CampaignDeliveryStatus"></a>

`CampaignDeliveryStatus(**data: Any)`
:   Updates on campaigns in the process of sending
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `can_cancel: bool | Any | None`
    :   Whether a campaign send can be canceled

    `emails_canceled: int | Any | None`
    :   The total number of emails canceled for this campaign

    `emails_sent: int | Any | None`
    :   The total number of emails confirmed sent for this campaign so far

    `enabled: bool | Any | None`
    :   Whether Campaign Delivery Status is enabled for this account and target campaign

    `model_config`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The current state of a campaign delivery

<a id="CampaignRecipients"></a>

`CampaignRecipients(**data: Any)`
:   List settings for the campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `list_id: str | Any | None`
    :   The unique list id

    `list_is_active: bool | Any | None`
    :   The status of the list used

    `list_name: str | Any | None`
    :   The name of the list

    `model_config`
    :   The type of the None singleton.

    `recipient_count: int | Any | None`
    :   Count of the recipients on the associated list

    `segment_text: str | Any | None`
    :   A description of the segment used for the campaign

<a id="CampaignReportSummary"></a>

`CampaignReportSummary(**data: Any)`
:   For sent campaigns, a summary of opens, clicks, and e-commerce data
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `click_rate: float | Any | None`
    :   The number of unique clicks divided by the total number of successful deliveries

    `clicks: int | Any | None`
    :   The total number of clicks for an campaign

    `ecommerce: airbyte_agent_sdk.connectors.mailchimp.models.CampaignReportSummaryEcommerce | Any | None`
    :   E-Commerce stats for a campaign

    `model_config`
    :   The type of the None singleton.

    `open_rate: float | Any | None`
    :   The number of unique opens divided by the total number of successful deliveries

    `opens: int | Any | None`
    :   The total number of opens for a campaign

    `subscriber_clicks: int | Any | None`
    :   The number of unique clicks

    `unique_opens: int | Any | None`
    :   The number of unique opens

<a id="CampaignReportSummaryEcommerce"></a>

`CampaignReportSummaryEcommerce(**data: Any)`
:   E-Commerce stats for a campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `total_orders: int | Any | None`
    :   The total orders for a campaign

    `total_revenue: float | Any | None`
    :   The total revenue for a campaign

    `total_spent: float | Any | None`
    :   The total spent for a campaign

<a id="CampaignSettings"></a>

`CampaignSettings(**data: Any)`
:   The settings for your campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `authenticate: bool | Any | None`
    :   Whether Mailchimp authenticated the campaign

    `auto_footer: bool | Any | None`
    :   Automatically append Mailchimp's default footer to the campaign

    `auto_tweet: bool | Any | None`
    :   Automatically tweet a link to the campaign archive page when the campaign is sent

    `drag_and_drop: bool | Any | None`
    :   Whether the campaign uses the drag-and-drop editor

    `fb_comments: bool | Any | None`
    :   Allows Facebook comments on the campaign

    `folder_id: str | Any | None`
    :   If the campaign is listed in a folder

    `from_name: str | Any | None`
    :   The from name on the campaign

    `inline_css: bool | Any | None`
    :   Automatically inline the CSS included with the campaign content

    `model_config`
    :   The type of the None singleton.

    `preview_text: str | Any | None`
    :   The preview text for the campaign

    `reply_to: str | Any | None`
    :   The reply-to email address for the campaign

    `subject_line: str | Any | None`
    :   The subject line for the campaign

    `template_id: int | Any | None`
    :   The id for the template used in this campaign

    `timewarp: bool | Any | None`
    :   Send this campaign using Timewarp

    `title: str | Any | None`
    :   The title of the campaign

    `to_name: str | Any | None`
    :   The campaign's custom to name

    `use_conversation: bool | Any | None`
    :   Use Mailchimp Conversation feature to manage out-of-office replies

<a id="CampaignTracking"></a>

`CampaignTracking(**data: Any)`
:   The tracking options for a campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `clicktale: str | Any | None`
    :   The custom slug for ClickTale tracking

    `ecomm360: bool | Any | None`
    :   Whether to enable eCommerce360 tracking

    `goal_tracking: bool | Any | None`
    :   Whether to enable Goal tracking

    `google_analytics: str | Any | None`
    :   The custom slug for Google Analytics tracking

    `html_clicks: bool | Any | None`
    :   Whether to track clicks in the HTML version of the campaign

    `model_config`
    :   The type of the None singleton.

    `opens: bool | Any | None`
    :   Whether to track opens

    `text_clicks: bool | Any | None`
    :   Whether to track clicks in the plain-text version of the campaign

<a id="CampaignsList"></a>

`CampaignsList(**data: Any)`
:   A collection of campaigns
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `campaigns: list[airbyte_agent_sdk.connectors.mailchimp.models.Campaign] | Any`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_items: int | Any`
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

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
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

    `ab_split_opts: dict[str, typing.Any] | None`
    :   [A/B Testing](https://mailchimp.com/help/about-ab-testing-campaigns/) options for a campaign.

    `archive_url: str | None`
    :   The link to the campaign's archive version in ISO 8601 format.

    `content_type: str | None`
    :   How the campaign's content is put together.

    `create_time: str | None`
    :   The date and time the campaign was created in ISO 8601 format.

    `delivery_status: dict[str, typing.Any] | None`
    :   Updates on campaigns in the process of sending.

    `emails_sent: int | None`
    :   The total number of emails sent for this campaign.

    `id: str | None`
    :   A string that uniquely identifies this campaign.

    `long_archive_url: str | None`
    :   The original link to the campaign's archive version.

    `model_config`
    :   The type of the None singleton.

    `needs_block_refresh: bool | None`
    :   Determines if the campaign needs its blocks refreshed by opening the web-based campaign editor. D...

    `parent_campaign_id: str | None`
    :   If this campaign is the child of another campaign, this identifies the parent campaign. For Examp...

    `recipients: dict[str, typing.Any] | None`
    :   List settings for the campaign.

    `report_summary: dict[str, typing.Any] | None`
    :   For sent campaigns, a summary of opens, clicks, and e-commerce data.

    `resendable: bool | None`
    :   Determines if the campaign qualifies to be resent to non-openers.

    `rss_opts: dict[str, typing.Any] | None`
    :   [RSS](https://mailchimp.com/help/share-your-blog-posts-with-mailchimp/) options for a campaign.

    `send_time: str | None`
    :   The date and time a campaign was sent.

    `settings: dict[str, typing.Any] | None`
    :   The settings for your campaign, including subject, from name, reply-to address, and more.

    `social_card: dict[str, typing.Any] | None`
    :   The preview for the campaign, rendered by social networks like Facebook and Twitter. [Learn more]...

    `status: str | None`
    :   The current status of the campaign.

    `tracking: dict[str, typing.Any] | None`
    :   The tracking options for a campaign.

    `type_: str | None`
    :   There are four types of [campaigns](https://mailchimp.com/help/getting-started-with-campaigns/) y...

    `variate_settings: dict[str, typing.Any] | None`
    :   The settings specific to A/B test campaigns.

    `web_id: int | None`
    :   The ID used in the Mailchimp web application. View this campaign in your Mailchimp account at `ht...

<a id="EmailActivity"></a>

`EmailActivity(**data: Any)`
:   A summary of the email activity for a campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `activity: list[airbyte_agent_sdk.connectors.mailchimp.models.EmailActivityActivityItem] | Any | None`
    :   The type of the None singleton.

    `campaign_id: str | Any | None`
    :   The type of the None singleton.

    `email_address: str | Any | None`
    :   The type of the None singleton.

    `email_id: str | Any | None`
    :   The type of the None singleton.

    `list_id: str | Any | None`
    :   The type of the None singleton.

    `list_is_active: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="EmailActivityActivityItem"></a>

`EmailActivityActivityItem(**data: Any)`
:   Nested schema for EmailActivity.activity_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action: str | Any | None`
    :   One of the following actions open, click, or bounce

    `ip: str | Any | None`
    :   The IP address recorded for the action

    `model_config`
    :   The type of the None singleton.

    `timestamp: str | Any | None`
    :   The date and time recorded for the action

    `type_: str | Any | None`
    :   If the action is a bounce, the type of bounce received hard, soft, or blocked

    `url: str | Any | None`
    :   If the action is a click, the URL on which the member clicked

<a id="EmailActivityList"></a>

`EmailActivityList(**data: Any)`
:   A list of member's subscriber activity in a specific campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `campaign_id: str | Any | None`
    :   The type of the None singleton.

    `emails: list[airbyte_agent_sdk.connectors.mailchimp.models.EmailActivity] | Any`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_items: int | Any`
    :   The type of the None singleton.

<a id="EmailActivityListResultMeta"></a>

`EmailActivityListResultMeta(**data: Any)`
:   Metadata for email_activity.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="EmailActivitySearchData"></a>

`EmailActivitySearchData(**data: Any)`
:   Search result data for email_activity entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `action: str | None`
    :   One of the following actions: 'open', 'click', or 'bounce'

    `campaign_id: str | None`
    :   The unique id for the campaign.

    `email_address: str | None`
    :   Email address for a subscriber.

    `email_id: str | None`
    :   The MD5 hash of the lowercase version of the list member's email address.

    `ip: str | None`
    :   The IP address recorded for the action.

    `list_id: str | None`
    :   The unique id for the list.

    `list_is_active: bool | None`
    :   The status of the list used, namely if it's deleted or disabled.

    `model_config`
    :   The type of the None singleton.

    `timestamp: str | None`
    :   The date and time recorded for the action in ISO 8601 format.

    `type_: str | None`
    :   If the action is a 'bounce', the type of bounce received: 'hard', 'soft'.

    `url: str | None`
    :   If the action is a 'click', the URL on which the member clicked.

<a id="Interest"></a>

`Interest(**data: Any)`
:   Assign subscribers to interests to group them together
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `category_id: str | Any | None`
    :   The type of the None singleton.

    `display_order: int | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `list_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `subscriber_count: str | Any | None`
    :   The type of the None singleton.

<a id="InterestCategoriesList"></a>

`InterestCategoriesList(**data: Any)`
:   Information about this list's interest categories
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `categories: list[airbyte_agent_sdk.connectors.mailchimp.models.InterestCategory] | Any`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `list_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_items: int | Any`
    :   The type of the None singleton.

<a id="InterestCategoriesListResultMeta"></a>

`InterestCategoriesListResultMeta(**data: Any)`
:   Metadata for interest_categories.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="InterestCategory"></a>

`InterestCategory(**data: Any)`
:   Interest categories organize interests, which are used to group subscribers based on their preferences
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `display_order: int | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `list_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `title: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

<a id="InterestsList"></a>

`InterestsList(**data: Any)`
:   A list of interests for a specific list
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `category_id: str | Any | None`
    :   The type of the None singleton.

    `interests: list[airbyte_agent_sdk.connectors.mailchimp.models.Interest] | Any`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `list_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_items: int | Any`
    :   The type of the None singleton.

<a id="InterestsListResultMeta"></a>

`InterestsListResultMeta(**data: Any)`
:   Metadata for interests.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Link"></a>

`Link(**data: Any)`
:   A HAL-style link relating the current resource to another.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `href: str | Any | None`
    :   The type of the None singleton.

    `method: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `rel: str | Any | None`
    :   The type of the None singleton.

    `schema_: str | Any | None`
    :   The type of the None singleton.

    `target_schema: str | Any | None`
    :   The type of the None singleton.

<a id="List"></a>

`List(**data: Any)`
:   Information about a specific list
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `beamer_address: str | Any | None`
    :   The type of the None singleton.

    `campaign_defaults: airbyte_agent_sdk.connectors.mailchimp.models.ListCampaignDefaults | Any | None`
    :   The type of the None singleton.

    `contact: airbyte_agent_sdk.connectors.mailchimp.models.ListContact | Any | None`
    :   The type of the None singleton.

    `date_created: str | Any | None`
    :   The type of the None singleton.

    `double_optin: bool | Any | None`
    :   The type of the None singleton.

    `email_type_option: bool | Any | None`
    :   The type of the None singleton.

    `has_welcome: bool | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `list_rating: int | Any | None`
    :   The type of the None singleton.

    `marketing_permissions: bool | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `notify_on_subscribe: str | Any | None`
    :   The type of the None singleton.

    `notify_on_unsubscribe: str | Any | None`
    :   The type of the None singleton.

    `permission_reminder: str | Any | None`
    :   The type of the None singleton.

    `stats: airbyte_agent_sdk.connectors.mailchimp.models.ListStats | Any | None`
    :   The type of the None singleton.

    `subscribe_url_long: str | Any | None`
    :   The type of the None singleton.

    `subscribe_url_short: str | Any | None`
    :   The type of the None singleton.

    `use_archive_bar: bool | Any | None`
    :   The type of the None singleton.

    `visibility: str | Any | None`
    :   The type of the None singleton.

    `web_id: int | Any | None`
    :   The type of the None singleton.

<a id="ListCampaignDefaults"></a>

`ListCampaignDefaults(**data: Any)`
:   Default values for campaigns created for this list
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `from_email: str | Any | None`
    :   The default from email for campaigns sent to this list

    `from_name: str | Any | None`
    :   The default from name for campaigns sent to this list

    `language: str | Any | None`
    :   The default language for this list's forms

    `model_config`
    :   The type of the None singleton.

    `subject: str | Any | None`
    :   The default subject line for campaigns sent to this list

<a id="ListContact"></a>

`ListContact(**data: Any)`
:   Contact information displayed in campaign footers to comply with international spam laws
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `address1: str | Any | None`
    :   The street address for the list contact

    `address2: str | Any | None`
    :   The street address for the list contact

    `city: str | Any | None`
    :   The city for the list contact

    `company: str | Any | None`
    :   The company name for the list

    `country: str | Any | None`
    :   A two-character ISO3166 country code

    `model_config`
    :   The type of the None singleton.

    `phone: str | Any | None`
    :   The phone number for the list contact

    `state: str | Any | None`
    :   The state for the list contact

    `zip: str | Any | None`
    :   The postal or zip code for the list contact

<a id="ListMember"></a>

`ListMember(**data: Any)`
:   Individuals who are currently or have been previously subscribed to this list
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `consents_to_one_to_one_messaging: bool | Any | None`
    :   The type of the None singleton.

    `contact_id: str | Any | None`
    :   The type of the None singleton.

    `email_address: str | Any | None`
    :   The type of the None singleton.

    `email_client: str | Any | None`
    :   The type of the None singleton.

    `email_type: str | Any | None`
    :   The type of the None singleton.

    `full_name: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `interests: dict[str, bool] | Any | None`
    :   The type of the None singleton.

    `ip_opt: str | Any | None`
    :   The type of the None singleton.

    `ip_signup: str | Any | None`
    :   The type of the None singleton.

    `language: str | Any | None`
    :   The type of the None singleton.

    `last_changed: str | Any | None`
    :   The type of the None singleton.

    `list_id: str | Any | None`
    :   The type of the None singleton.

    `location: airbyte_agent_sdk.connectors.mailchimp.models.ListMemberLocation | Any | None`
    :   The type of the None singleton.

    `member_rating: int | Any | None`
    :   The type of the None singleton.

    `merge_fields: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `source: str | Any | None`
    :   The type of the None singleton.

    `stats: airbyte_agent_sdk.connectors.mailchimp.models.ListMemberStats | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `tags: list[airbyte_agent_sdk.connectors.mailchimp.models.ListMemberTagsItem] | Any | None`
    :   The type of the None singleton.

    `tags_count: int | Any | None`
    :   The type of the None singleton.

    `timestamp_opt: str | Any | None`
    :   The type of the None singleton.

    `timestamp_signup: str | Any | None`
    :   The type of the None singleton.

    `unique_email_id: str | Any | None`
    :   The type of the None singleton.

    `unsubscribe_reason: str | Any | None`
    :   The type of the None singleton.

    `vip: bool | Any | None`
    :   The type of the None singleton.

    `web_id: int | Any | None`
    :   The type of the None singleton.

<a id="ListMemberLocation"></a>

`ListMemberLocation(**data: Any)`
:   Subscriber location information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `country_code: str | Any | None`
    :   The unique code for the location country

    `dstoff: int | Any | None`
    :   The offset for timezones where daylight saving time is observed

    `gmtoff: int | Any | None`
    :   The time difference in hours from GMT

    `latitude: float | Any | None`
    :   The location latitude

    `longitude: float | Any | None`
    :   The location longitude

    `model_config`
    :   The type of the None singleton.

    `region: str | Any | None`
    :   The region for the location

    `timezone: str | Any | None`
    :   The timezone for the location

<a id="ListMemberStats"></a>

`ListMemberStats(**data: Any)`
:   Open and click rates for this subscriber
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avg_click_rate: float | Any | None`
    :   A subscriber's average clickthrough rate

    `avg_open_rate: float | Any | None`
    :   A subscriber's average open rate

    `ecommerce_data: airbyte_agent_sdk.connectors.mailchimp.models.ListMemberStatsEcommerceData | Any | None`
    :   Ecommerce stats for the list member if the list is attached to a store

    `model_config`
    :   The type of the None singleton.

<a id="ListMemberStatsEcommerceData"></a>

`ListMemberStatsEcommerceData(**data: Any)`
:   Ecommerce stats for the list member if the list is attached to a store
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `currency_code: str | Any | None`
    :   The three-letter ISO 4217 code for the currency that the store accepts

    `model_config`
    :   The type of the None singleton.

    `number_of_orders: float | Any | None`
    :   The total number of orders placed by the list member

    `total_revenue: float | Any | None`
    :   The total revenue the list member has brought in

<a id="ListMemberTagsItem"></a>

`ListMemberTagsItem(**data: Any)`
:   Nested schema for ListMember.tags_item
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any | None`
    :   The tag id

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The name of the tag

<a id="ListMembersList"></a>

`ListMembersList(**data: Any)`
:   Manage members of a specific Mailchimp list
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `list_id: str | Any | None`
    :   The type of the None singleton.

    `members: list[airbyte_agent_sdk.connectors.mailchimp.models.ListMember] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_items: int | Any`
    :   The type of the None singleton.

<a id="ListMembersListResultMeta"></a>

`ListMembersListResultMeta(**data: Any)`
:   Metadata for list_members.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ListStats"></a>

`ListStats(**data: Any)`
:   Stats for the list
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avg_sub_rate: float | Any | None`
    :   The average number of subscriptions per month for the list

    `avg_unsub_rate: float | Any | None`
    :   The average number of unsubscriptions per month for the list

    `campaign_count: int | Any | None`
    :   The number of campaigns in any status that use this list

    `campaign_last_sent: str | Any | None`
    :   The date and time the last campaign was sent to this list

    `cleaned_count: int | Any | None`
    :   The number of members cleaned from the list

    `cleaned_count_since_send: int | Any | None`
    :   The number of members cleaned from the list since the last campaign was sent

    `click_rate: float | Any | None`
    :   The average click rate for campaigns sent to this list

    `last_sub_date: str | Any | None`
    :   The date and time of the last time someone subscribed to this list

    `last_unsub_date: str | Any | None`
    :   The date and time of the last time someone unsubscribed from this list

    `member_count: int | Any | None`
    :   The number of active members in the list

    `member_count_since_send: int | Any | None`
    :   The number of active members in the list since the last campaign was sent

    `merge_field_count: int | Any | None`
    :   The number of merge fields for this list

    `model_config`
    :   The type of the None singleton.

    `open_rate: float | Any | None`
    :   The average open rate for campaigns sent to this list

    `target_sub_rate: float | Any | None`
    :   The target number of subscriptions per month for the list to keep it growing

    `total_contacts: int | Any | None`
    :   The number of contacts in the list, including subscribed, unsubscribed, pending, cleaned, deleted, transactional, and those that need to be reconfirmed

    `unsubscribe_count: int | Any | None`
    :   The number of members who have unsubscribed from the list

    `unsubscribe_count_since_send: int | Any | None`
    :   The number of members who have unsubscribed since the last campaign was sent

<a id="ListsList"></a>

`ListsList(**data: Any)`
:   A collection of subscriber lists for this account
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `lists: list[airbyte_agent_sdk.connectors.mailchimp.models.List] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_items: int | Any`
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

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
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

    `beamer_address: str | None`
    :   The list's Email Beamer address.

    `campaign_defaults: dict[str, typing.Any] | None`
    :   Default values for campaigns created for this list.

    `contact: dict[str, typing.Any] | None`
    :   Contact information displayed in campaign footers to comply with international spam laws.

    `date_created: str | None`
    :   The date and time that this list was created in ISO 8601 format.

    `double_optin: bool | None`
    :   Whether or not to require the subscriber to confirm subscription via email.

    `email_type_option: bool | None`
    :   Whether the list supports multiple formats for emails. When set to `true`, subscribers can choose...

    `has_welcome: bool | None`
    :   Whether or not this list has a welcome automation connected.

    `id: str | None`
    :   A string that uniquely identifies this list.

    `list_rating: int | None`
    :   An auto-generated activity score for the list (0-5).

    `marketing_permissions: bool | None`
    :   Whether or not the list has marketing permissions (eg. GDPR) enabled.

    `model_config`
    :   The type of the None singleton.

    `modules: list[typing.Any] | None`
    :   Any list-specific modules installed for this list.

    `name: str | None`
    :   The name of the list.

    `notify_on_subscribe: str | None`
    :   The email address to send subscribe notifications to.

    `notify_on_unsubscribe: str | None`
    :   The email address to send unsubscribe notifications to.

    `permission_reminder: str | None`
    :   The permission reminder for the list.

    `stats: dict[str, typing.Any] | None`
    :   Stats for the list. Many of these are cached for at least five minutes.

    `subscribe_url_long: str | None`
    :   The full version of this list's subscribe form (host will vary).

    `subscribe_url_short: str | None`
    :   Our EepURL shortened version of this list's subscribe form.

    `use_archive_bar: bool | None`
    :   Whether campaigns for this list use the Archive Bar in archives by default.

    `visibility: str | None`
    :   Whether this list is public or private.

    `web_id: int | None`
    :   The ID used in the Mailchimp web application. View this list in your Mailchimp account at `https:...

<a id="MailchimpAuthConfig"></a>

`MailchimpAuthConfig(**data: Any)`
:   API Key Authentication
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `api_key: str`
    :   Your Mailchimp API key. You can find this in your Mailchimp account under Account > Extras > API keys.

    `model_config`
    :   The type of the None singleton.

<a id="MailchimpCheckResult"></a>

`MailchimpCheckResult(**data: Any)`
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

<a id="MailchimpExecuteResult"></a>

`MailchimpExecuteResult(**data: Any)`
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

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta

    ### Class variables

    `data: ~T`
    :   Response data containing the result of the action.

    `model_config`
    :   The type of the None singleton.

<a id="MailchimpExecuteResultWithMeta"></a>

`MailchimpExecuteResultWithMeta(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Descendants

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[Automation], AutomationsListResultMeta]
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta]
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[EmailActivity], EmailActivityListResultMeta]
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[InterestCategory], InterestCategoriesListResultMeta]
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[Interest], InterestsListResultMeta]
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[ListMember], ListMembersListResultMeta]
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[List], ListsListResultMeta]
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[Report], ReportsListResultMeta]
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[SegmentMember], SegmentMembersListResultMeta]
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[Segment], SegmentsListResultMeta]
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[Tag], TagsListResultMeta]
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta[list[Unsubscribe], UnsubscribesListResultMeta]

    ### Class variables

    `meta: ~S`
    :   Metadata about the response (e.g., pagination cursors, record counts).

`MailchimpExecuteResultWithMeta[list[Automation], AutomationsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
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

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MailchimpExecuteResultWithMeta[list[Campaign], CampaignsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
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

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MailchimpExecuteResultWithMeta[list[EmailActivity], EmailActivityListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="EmailActivityListResult"></a>

`EmailActivityListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MailchimpExecuteResultWithMeta[list[InterestCategory], InterestCategoriesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="InterestCategoriesListResult"></a>

`InterestCategoriesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MailchimpExecuteResultWithMeta[list[Interest], InterestsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="InterestsListResult"></a>

`InterestsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MailchimpExecuteResultWithMeta[list[ListMember], ListMembersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ListMembersListResult"></a>

`ListMembersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MailchimpExecuteResultWithMeta[list[List], ListsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
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

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MailchimpExecuteResultWithMeta[list[Report], ReportsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="ReportsListResult"></a>

`ReportsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MailchimpExecuteResultWithMeta[list[SegmentMember], SegmentMembersListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SegmentMembersListResult"></a>

`SegmentMembersListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MailchimpExecuteResultWithMeta[list[Segment], SegmentsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="SegmentsListResult"></a>

`SegmentsListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MailchimpExecuteResultWithMeta[list[Tag], TagsListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
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

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

`MailchimpExecuteResultWithMeta[list[Unsubscribe], UnsubscribesListResultMeta](**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

    ### Class variables

    `model_config`
    :   The type of the None singleton.

<a id="UnsubscribesListResult"></a>

`UnsubscribesListResult(**data: Any)`
:   Response envelope with data and metadata.
    
    Used for actions that return both data and metadata (e.g., pagination info).
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResultWithMeta
    * airbyte_agent_sdk.connectors.mailchimp.models.MailchimpExecuteResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="Report"></a>

`Report(**data: Any)`
:   Report details about a sent campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `abuse_reports: int | Any | None`
    :   The type of the None singleton.

    `bounces: airbyte_agent_sdk.connectors.mailchimp.models.ReportBounces | Any | None`
    :   The type of the None singleton.

    `campaign_title: str | Any | None`
    :   The type of the None singleton.

    `clicks: airbyte_agent_sdk.connectors.mailchimp.models.ReportClicks | Any | None`
    :   The type of the None singleton.

    `delivery_status: airbyte_agent_sdk.connectors.mailchimp.models.ReportDeliveryStatus | Any | None`
    :   The type of the None singleton.

    `ecommerce: airbyte_agent_sdk.connectors.mailchimp.models.ReportEcommerce | Any | None`
    :   The type of the None singleton.

    `emails_sent: int | Any | None`
    :   The type of the None singleton.

    `facebook_likes: airbyte_agent_sdk.connectors.mailchimp.models.ReportFacebookLikes | Any | None`
    :   The type of the None singleton.

    `forwards: airbyte_agent_sdk.connectors.mailchimp.models.ReportForwards | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `industry_stats: airbyte_agent_sdk.connectors.mailchimp.models.ReportIndustryStats | Any | None`
    :   The type of the None singleton.

    `list_id: str | Any | None`
    :   The type of the None singleton.

    `list_is_active: bool | Any | None`
    :   The type of the None singleton.

    `list_name: str | Any | None`
    :   The type of the None singleton.

    `list_stats: airbyte_agent_sdk.connectors.mailchimp.models.ReportListStats | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `opens: airbyte_agent_sdk.connectors.mailchimp.models.ReportOpens | Any | None`
    :   The type of the None singleton.

    `preview_text: str | Any | None`
    :   The type of the None singleton.

    `rss_last_send: str | Any | None`
    :   The type of the None singleton.

    `send_time: str | Any | None`
    :   The type of the None singleton.

    `subject_line: str | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `unsubscribed: int | Any | None`
    :   The type of the None singleton.

<a id="ReportBounces"></a>

`ReportBounces(**data: Any)`
:   An object describing the bounce summary for the campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `hard_bounces: int | Any | None`
    :   The total number of hard bounced email addresses

    `model_config`
    :   The type of the None singleton.

    `soft_bounces: int | Any | None`
    :   The total number of soft bounced email addresses

    `syntax_errors: int | Any | None`
    :   The total number of addresses that were syntax-related bounces

<a id="ReportClicks"></a>

`ReportClicks(**data: Any)`
:   An object describing the click activity for the campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `click_rate: float | Any | None`
    :   The number of unique clicks divided by the total number of successful deliveries

    `clicks_total: int | Any | None`
    :   The total number of clicks for the campaign

    `last_click: str | Any | None`
    :   The date and time of the last recorded click for the campaign

    `model_config`
    :   The type of the None singleton.

    `unique_clicks: int | Any | None`
    :   The total number of unique clicks for links across a campaign

    `unique_subscriber_clicks: int | Any | None`
    :   The total number of subscribers who clicked on a campaign

<a id="ReportDeliveryStatus"></a>

`ReportDeliveryStatus(**data: Any)`
:   Updates on campaigns in the process of sending
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `enabled: bool | Any | None`
    :   Whether Campaign Delivery Status is enabled for this account and target campaign

    `model_config`
    :   The type of the None singleton.

<a id="ReportEcommerce"></a>

`ReportEcommerce(**data: Any)`
:   E-Commerce stats for a campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `model_config`
    :   The type of the None singleton.

    `total_orders: int | Any | None`
    :   The total orders for a campaign

    `total_revenue: float | Any | None`
    :   The total revenue for a campaign

    `total_spent: float | Any | None`
    :   The total spent for a campaign

<a id="ReportFacebookLikes"></a>

`ReportFacebookLikes(**data: Any)`
:   An object describing campaign engagement on Facebook
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `facebook_likes: int | Any | None`
    :   The number of Facebook likes for the campaign

    `model_config`
    :   The type of the None singleton.

    `recipient_likes: int | Any | None`
    :   The number of recipients who liked the campaign on Facebook

    `unique_likes: int | Any | None`
    :   The number of unique likes

<a id="ReportForwards"></a>

`ReportForwards(**data: Any)`
:   An object describing the forwards and forward activity for the campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `forwards_count: int | Any | None`
    :   How many times the campaign has been forwarded

    `forwards_opens: int | Any | None`
    :   How many times the forwarded campaign has been opened

    `model_config`
    :   The type of the None singleton.

<a id="ReportIndustryStats"></a>

`ReportIndustryStats(**data: Any)`
:   The average campaign statistics for your industry
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `abuse_rate: float | Any | None`
    :   The industry abuse rate

    `bounce_rate: float | Any | None`
    :   The industry bounce rate

    `click_rate: float | Any | None`
    :   The industry click rate

    `model_config`
    :   The type of the None singleton.

    `open_rate: float | Any | None`
    :   The industry open rate

    `type_: str | Any | None`
    :   The type of business industry associated with your account

    `unopen_rate: float | Any | None`
    :   The industry unopened rate

    `unsub_rate: float | Any | None`
    :   The industry unsubscribe rate

<a id="ReportListStats"></a>

`ReportListStats(**data: Any)`
:   The average campaign statistics for your list
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `click_rate: float | Any | None`
    :   The average click rate for campaigns sent to this list

    `model_config`
    :   The type of the None singleton.

    `open_rate: float | Any | None`
    :   The average open rate for campaigns sent to this list

    `sub_rate: float | Any | None`
    :   The average number of subscriptions per month for the list

    `unsub_rate: float | Any | None`
    :   The average number of unsubscriptions per month for the list

<a id="ReportOpens"></a>

`ReportOpens(**data: Any)`
:   An object describing the open activity for the campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `last_open: str | Any | None`
    :   The date and time of the last recorded open

    `model_config`
    :   The type of the None singleton.

    `open_rate: float | Any | None`
    :   The number of unique opens divided by the total number of successful deliveries

    `opens_total: int | Any | None`
    :   The total number of opens for a campaign

    `unique_opens: int | Any | None`
    :   The total number of unique opens

<a id="ReportsList"></a>

`ReportsList(**data: Any)`
:   A list of reports containing campaigns marked as Sent
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reports: list[airbyte_agent_sdk.connectors.mailchimp.models.Report] | Any`
    :   The type of the None singleton.

    `total_items: int | Any`
    :   The type of the None singleton.

<a id="ReportsListResultMeta"></a>

`ReportsListResultMeta(**data: Any)`
:   Metadata for reports.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="ReportsSearchData"></a>

`ReportsSearchData(**data: Any)`
:   Search result data for reports entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `ab_split: dict[str, typing.Any] | None`
    :   General stats about different groups of an A/B Split campaign. Does not return information about ...

    `abuse_reports: int | None`
    :   The number of abuse reports generated for this campaign.

    `bounces: dict[str, typing.Any] | None`
    :   An object describing the bounce summary for the campaign.

    `campaign_title: str | None`
    :   The title of the campaign.

    `clicks: dict[str, typing.Any] | None`
    :   An object describing the click activity for the campaign.

    `delivery_status: dict[str, typing.Any] | None`
    :   Updates on campaigns in the process of sending.

    `ecommerce: dict[str, typing.Any] | None`
    :   E-Commerce stats for a campaign.

    `emails_sent: int | None`
    :   The total number of emails sent for this campaign.

    `facebook_likes: dict[str, typing.Any] | None`
    :   An object describing campaign engagement on Facebook.

    `forwards: dict[str, typing.Any] | None`
    :   An object describing the forwards and forward activity for the campaign.

    `id: str | None`
    :   A string that uniquely identifies this campaign.

    `industry_stats: dict[str, typing.Any] | None`
    :   The average campaign statistics for your industry.

    `list_id: str | None`
    :   The unique list id.

    `list_is_active: bool | None`
    :   The status of the list used, namely if it's deleted or disabled.

    `list_name: str | None`
    :   The name of the list.

    `list_stats: dict[str, typing.Any] | None`
    :   The average campaign statistics for your list. This won't be present if we haven't calculated i...

    `model_config`
    :   The type of the None singleton.

    `opens: dict[str, typing.Any] | None`
    :   An object describing the open activity for the campaign.

    `preview_text: str | None`
    :   The preview text for the campaign.

    `rss_last_send: str | None`
    :   For RSS campaigns, the date and time of the last send in ISO 8601 format.

    `send_time: str | None`
    :   The date and time a campaign was sent in ISO 8601 format.

    `share_report: dict[str, typing.Any] | None`
    :   The url and password for the VIP report.

    `subject_line: str | None`
    :   The subject line for the campaign.

    `timeseries: list[typing.Any] | None`
    :   An hourly breakdown of the performance of the campaign over the first 24 hours.

    `timewarp: list[typing.Any] | None`
    :   An hourly breakdown of sends, opens, and clicks if a campaign is sent using timewarp.

    `type_: str | None`
    :   The type of campaign (regular, plain-text, ab_split, rss, automation, variate, or auto).

    `unsubscribed: int | None`
    :   The total number of unsubscribed members for this campaign.

<a id="Segment"></a>

`Segment(**data: Any)`
:   Information about a specific segment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `created_at: str | Any | None`
    :   The type of the None singleton.

    `id: int | Any`
    :   The type of the None singleton.

    `list_id: str | Any | None`
    :   The type of the None singleton.

    `member_count: int | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

    `options: airbyte_agent_sdk.connectors.mailchimp.models.SegmentOptions | Any | None`
    :   The type of the None singleton.

    `type_: str | Any | None`
    :   The type of the None singleton.

    `updated_at: str | Any | None`
    :   The type of the None singleton.

<a id="SegmentMember"></a>

`SegmentMember(**data: Any)`
:   Individuals who are currently or have been previously subscribed to this list
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email_address: str | Any | None`
    :   The type of the None singleton.

    `email_client: str | Any | None`
    :   The type of the None singleton.

    `email_type: str | Any | None`
    :   The type of the None singleton.

    `id: str | Any`
    :   The type of the None singleton.

    `interests: dict[str, bool] | Any | None`
    :   The type of the None singleton.

    `ip_opt: str | Any | None`
    :   The type of the None singleton.

    `ip_signup: str | Any | None`
    :   The type of the None singleton.

    `language: str | Any | None`
    :   The type of the None singleton.

    `last_changed: str | Any | None`
    :   The type of the None singleton.

    `list_id: str | Any | None`
    :   The type of the None singleton.

    `location: airbyte_agent_sdk.connectors.mailchimp.models.SegmentMemberLocation | Any | None`
    :   The type of the None singleton.

    `member_rating: int | Any | None`
    :   The type of the None singleton.

    `merge_fields: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `stats: airbyte_agent_sdk.connectors.mailchimp.models.SegmentMemberStats | Any | None`
    :   The type of the None singleton.

    `status: str | Any | None`
    :   The type of the None singleton.

    `timestamp_opt: str | Any | None`
    :   The type of the None singleton.

    `timestamp_signup: str | Any | None`
    :   The type of the None singleton.

    `unique_email_id: str | Any | None`
    :   The type of the None singleton.

    `vip: bool | Any | None`
    :   The type of the None singleton.

<a id="SegmentMemberLocation"></a>

`SegmentMemberLocation(**data: Any)`
:   Subscriber location information
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `country_code: str | Any | None`
    :   The unique code for the location country

    `dstoff: int | Any | None`
    :   The offset for timezones where daylight saving time is observed

    `gmtoff: int | Any | None`
    :   The time difference in hours from GMT

    `latitude: float | Any | None`
    :   The location latitude

    `longitude: float | Any | None`
    :   The location longitude

    `model_config`
    :   The type of the None singleton.

    `region: str | Any | None`
    :   The region for the location

    `timezone: str | Any | None`
    :   The timezone for the location

<a id="SegmentMemberStats"></a>

`SegmentMemberStats(**data: Any)`
:   Open and click rates for this subscriber
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `avg_click_rate: float | Any | None`
    :   A subscriber's average clickthrough rate

    `avg_open_rate: float | Any | None`
    :   A subscriber's average open rate

    `model_config`
    :   The type of the None singleton.

<a id="SegmentMembersList"></a>

`SegmentMembersList(**data: Any)`
:   View members in a specific list segment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `members: list[airbyte_agent_sdk.connectors.mailchimp.models.SegmentMember] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_items: int | Any`
    :   The type of the None singleton.

<a id="SegmentMembersListResultMeta"></a>

`SegmentMembersListResultMeta(**data: Any)`
:   Metadata for segment_members.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="SegmentOptions"></a>

`SegmentOptions(**data: Any)`
:   The conditions of the segment
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `conditions: list[dict[str, typing.Any]] | Any | None`
    :   Segment match conditions

    `match: str | Any | None`
    :   Match type

    `model_config`
    :   The type of the None singleton.

<a id="SegmentsList"></a>

`SegmentsList(**data: Any)`
:   A list of available segments
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `list_id: str | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `segments: list[airbyte_agent_sdk.connectors.mailchimp.models.Segment] | Any`
    :   The type of the None singleton.

    `total_items: int | Any`
    :   The type of the None singleton.

<a id="SegmentsListResultMeta"></a>

`SegmentsListResultMeta(**data: Any)`
:   Metadata for segments.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Tag"></a>

`Tag(**data: Any)`
:   A tag that can be assigned to a list member
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `id: int | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `name: str | Any | None`
    :   The type of the None singleton.

<a id="TagsList"></a>

`TagsList(**data: Any)`
:   A list of tags assigned to a list
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `tags: list[airbyte_agent_sdk.connectors.mailchimp.models.Tag] | Any`
    :   The type of the None singleton.

    `total_items: int | Any`
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

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

<a id="Unsubscribe"></a>

`Unsubscribe(**data: Any)`
:   A member who unsubscribed from a specific campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `campaign_id: str | Any | None`
    :   The type of the None singleton.

    `email_address: str | Any | None`
    :   The type of the None singleton.

    `email_id: str | Any | None`
    :   The type of the None singleton.

    `list_id: str | Any | None`
    :   The type of the None singleton.

    `list_is_active: bool | Any | None`
    :   The type of the None singleton.

    `merge_fields: dict[str, typing.Any] | Any | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `reason: str | Any | None`
    :   The type of the None singleton.

    `timestamp: str | Any | None`
    :   The type of the None singleton.

    `vip: bool | Any | None`
    :   The type of the None singleton.

<a id="UnsubscribesList"></a>

`UnsubscribesList(**data: Any)`
:   A list of members who have unsubscribed from a specific campaign
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `campaign_id: str | Any | None`
    :   The type of the None singleton.

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `total_items: int | Any`
    :   The type of the None singleton.

    `unsubscribes: list[airbyte_agent_sdk.connectors.mailchimp.models.Unsubscribe] | Any`
    :   The type of the None singleton.

<a id="UnsubscribesListResultMeta"></a>

`UnsubscribesListResultMeta(**data: Any)`
:   Metadata for unsubscribes.Action.LIST operation
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `links: list[airbyte_agent_sdk.connectors.mailchimp.models.Link] | Any`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.