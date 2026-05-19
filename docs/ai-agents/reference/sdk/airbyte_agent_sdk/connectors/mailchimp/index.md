---
id: airbyte_agent_sdk-connectors-mailchimp-index
title: airbyte_agent_sdk.connectors.mailchimp.index
---

Module airbyte_agent_sdk.connectors.mailchimp
=============================================
Mailchimp connector for Airbyte SDK.

Auto-generated from OpenAPI specification.

Sub-modules
-----------
* airbyte_agent_sdk.connectors.mailchimp.connector
* airbyte_agent_sdk.connectors.mailchimp.connector_model
* airbyte_agent_sdk.connectors.mailchimp.models
* airbyte_agent_sdk.connectors.mailchimp.types

Classes
-------

<a id="AirbyteAuthConfig"></a>

`AirbyteAuthConfig(**data: Any)`
:   Authentication configuration for Airbyte hosted mode execution.
    
    Pass this to the connector's `auth_config` parameter to use hosted mode,
    where API credentials are stored securely in Airbyte Cloud.
    
    For hosted mode execution, provide client credentials with either:
    - `connector_id`: Direct connector/source ID (skips lookup)
    - `workspace_name`: Workspace name for connector lookup
    
    Attributes:
        workspace_name: Workspace name for hosted mode connector lookup
        organization_id: Optional Airbyte organization ID for multi-org selection
        airbyte_client_id: Airbyte OAuth client ID (required for hosted mode)
        airbyte_client_secret: Airbyte OAuth client secret (required for hosted mode)
        connector_id: Specific connector/source ID (skips lookup if provided)
    
    Examples:
        # Hosted mode with connector_id (no lookup needed)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with workspace_name (lookup by workspace)
        connector = GongConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `airbyte_client_id: str | None`
    :   The type of the None singleton.

    `airbyte_client_secret: str | None`
    :   The type of the None singleton.

    `connector_id: str | None`
    :   The type of the None singleton.

    `model_config`
    :   The type of the None singleton.

    `organization_id: str | None`
    :   The type of the None singleton.

    `workspace_name: str | None`
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

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[AutomationsSearchData]
    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[CampaignsSearchData]
    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[EmailActivitySearchData]
    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[InterestCategoriesSearchData]
    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[InterestsSearchData]
    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[ListMembersSearchData]
    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[ListsSearchData]
    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[ReportsSearchData]
    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[SegmentMembersSearchData]
    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[SegmentsSearchData]
    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[TagsSearchData]
    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult[UnsubscribesSearchData]

    ### Class variables

    `data: list[~D]`
    :   List of matching records.

    `meta: airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchMeta`
    :   Pagination metadata.

    `model_config`
    :   The type of the None singleton.

<a id="AutomationsSearchResult"></a>

`AutomationsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

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

<a id="InterestCategoriesSearchResult"></a>

`InterestCategoriesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="InterestsSearchResult"></a>

`InterestsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="ListMembersSearchResult"></a>

`ListMembersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

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

<a id="SegmentMembersSearchResult"></a>

`SegmentMembersSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="SegmentsSearchResult"></a>

`SegmentsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="TagsSearchResult"></a>

`TagsSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="UnsubscribesSearchResult"></a>

`UnsubscribesSearchResult(**data: Any)`
:   Result from Airbyte cache search operations with typed records.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * airbyte_agent_sdk.connectors.mailchimp.models.AirbyteSearchResult
    * pydantic.main.BaseModel
    * typing.Generic

<a id="AutomationsSearchData"></a>

`AutomationsSearchData(**data: Any)`
:   Search result data for automations entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `create_time: str | None`
    :   The date and time the Automation was created

    `emails_sent: int | None`
    :   The total number of emails sent for the Automation

    `id: str`
    :   A string that uniquely identifies an Automation workflow

    `model_config`
    :   The type of the None singleton.

    `recipients: dict[str, typing.Any] | None`
    :   List settings for the Automation

    `report_summary: dict[str, typing.Any] | None`
    :   A summary of opens and clicks for sent campaigns

    `settings: dict[str, typing.Any] | None`
    :   The settings for the Automation workflow

    `start_time: str | None`
    :   The date and time the Automation was started

    `status: str | None`
    :   The current status of the Automation

    `tracking: dict[str, typing.Any] | None`
    :   The tracking options for the Automation

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

<a id="InterestCategoriesSearchData"></a>

`InterestCategoriesSearchData(**data: Any)`
:   Search result data for interest_categories entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `display_order: int | None`
    :   The order that the categories are displayed in the list

    `id: str`
    :   The id for the interest category

    `list_id: str | None`
    :   The unique list id for the category

    `model_config`
    :   The type of the None singleton.

    `title: str | None`
    :   The text description of this category

    `type_: str | None`
    :   Determines how this category's interests appear on signup forms

<a id="InterestsSearchData"></a>

`InterestsSearchData(**data: Any)`
:   Search result data for interests entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `category_id: str | None`
    :   The id for the interest category

    `display_order: int | None`
    :   The display order for interests

    `id: str`
    :   The ID for the interest

    `list_id: str | None`
    :   The ID for the list that this interest belongs to

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the interest

    `subscriber_count: str | None`
    :   The number of subscribers associated with this interest

<a id="ListMembersSearchData"></a>

`ListMembersSearchData(**data: Any)`
:   Search result data for list_members entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `consents_to_one_to_one_messaging: bool | None`
    :   Indicates whether a contact consents to 1:1 messaging

    `contact_id: str | None`
    :   As Mailchimp evolves beyond email, you may eventually have contacts without email addresses

    `email_address: str | None`
    :   Email address for a subscriber

    `email_client: str | None`
    :   The list member's email client

    `email_type: str | None`
    :   Type of email this member asked to get

    `full_name: str | None`
    :   The contact's full name

    `id: str`
    :   The MD5 hash of the lowercase version of the list member's email address

    `interests: dict[str, typing.Any] | None`
    :   The key of this object's properties is the ID of the interest in question

    `ip_opt: str | None`
    :   The IP address the subscriber used to confirm their opt-in status

    `ip_signup: str | None`
    :   IP address the subscriber signed up from

    `language: str | None`
    :   If set/detected, the subscriber's language

    `last_changed: str | None`
    :   The date and time the member's info was last changed

    `list_id: str | None`
    :   The list id

    `location: dict[str, typing.Any] | None`
    :   Subscriber location information

    `member_rating: int | None`
    :   Star rating for this member, between 1 and 5

    `merge_fields: dict[str, typing.Any] | None`
    :   A dictionary of merge fields where the keys are the merge tags

    `model_config`
    :   The type of the None singleton.

    `source: str | None`
    :   The source from which the subscriber was added to this list

    `stats: dict[str, typing.Any] | None`
    :   Open and click rates for this subscriber

    `status: str | None`
    :   Subscriber's current status

    `tags: list[typing.Any] | None`
    :   Returns up to 50 tags applied to this member

    `tags_count: int | None`
    :   The number of tags applied to this member

    `timestamp_opt: str | None`
    :   The date and time the subscriber confirmed their opt-in status

    `timestamp_signup: str | None`
    :   The date and time the subscriber signed up for the list

    `unique_email_id: str | None`
    :   An identifier for the address across all of Mailchimp

    `unsubscribe_reason: str | None`
    :   A subscriber's reason for unsubscribing

    `vip: bool | None`
    :   VIP status for subscriber

    `web_id: int | None`
    :   The ID used in the Mailchimp web application

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

<a id="MailchimpConnector"></a>

`MailchimpConnector(auth_config: MailchimpAuthConfig | AirbyteAuthConfig | BaseModel | None = None, on_token_refresh: Any | None = None, data_center: str | None = None)`
:   Type-safe Mailchimp API connector.
    
    Auto-generated from OpenAPI specification with full type safety.
    
    Initialize a new mailchimp connector instance.
    
    Supports both local and hosted execution modes:
    - Local mode: Provide connector-specific auth config (e.g., MailchimpAuthConfig)
    - Hosted mode: Provide `AirbyteAuthConfig` with client credentials and either `connector_id` or `workspace_name`
    
    Args:
        auth_config: Either connector-specific auth config for local mode, or AirbyteAuthConfig for hosted mode
        on_token_refresh: Optional callback for OAuth2 token refresh persistence.
            Called with new_tokens dict when tokens are refreshed. Can be sync or async.
            Example: lambda tokens: save_to_database(tokens)            data_center: The data center for your Mailchimp account (e.g., us1, us2, us6)
    Examples:
        # Local mode (direct API calls)
        connector = MailchimpConnector(auth_config=MailchimpAuthConfig(api_key="..."))
        # Hosted mode with explicit connector_id (no lookup needed)
        connector = MailchimpConnector(
            auth_config=AirbyteAuthConfig(
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789",
                connector_id="existing-source-uuid"
            )
        )
    
        # Hosted mode with lookup by workspace_name
        connector = MailchimpConnector(
            auth_config=AirbyteAuthConfig(
                workspace_name="user-123",
                organization_id="00000000-0000-0000-0000-000000000123",
                airbyte_client_id="client_abc123",
                airbyte_client_secret="secret_xyz789"
            )
        )

    ### Class variables

    `connector_name`
    :   The type of the None singleton.

    `connector_version`
    :   The type of the None singleton.

    `sdk_version`
    :   The type of the None singleton.

    ### Static methods

    `tool_utils(func: _F | None = None, *, update_docstring: bool = True, max_output_chars: int | None = 100000, framework: FrameworkName | None = None, internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> ~_F | Callable[[~_F], ~_F]`
    :   Decorator that adds tool utilities like docstring augmentation and output limits.
        
        Composes :func:`airbyte_agent_sdk.translation.translate_exceptions` for
        runtime wrapping (sync/async branch + output-size check + framework
        signal translation + optional internal retry loop), and adds
        connector-specific docstring augmentation on top of it.
        
        Usage:
            @mcp.tool()
            @MailchimpConnector.tool_utils
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @MailchimpConnector.tool_utils(update_docstring=False, max_output_chars=None)
            async def execute(entity: str, action: str, params: dict):
                ...
        
            @mcp.tool()
            @MailchimpConnector.tool_utils(framework="pydantic_ai", internal_retries=2)
            async def execute(entity: str, action: str, params: dict):
                ...
        
        Args:
            update_docstring: When True, append connector capabilities to __doc__.
            max_output_chars: Max serialized output size before raising. Use None to disable.
            framework: One of ``"pydantic_ai" | "langchain" | "openai_agents" | "mcp"``.
                Defaults to None → auto-detect by attempting each framework's canonical
                import in order. Explicit always wins.
            internal_retries: How many transient runtime failures (429/5xx, network,
                timeout) to retry silently before surfacing. Default 0. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            should_internal_retry: Optional predicate ``(error, args, kwargs) -> bool``
                further restricting which retryable errors are safe for this specific
                tool. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.
            exhausted_runtime_failure_message: Optional callback
                ``(error, args, kwargs) -> str | None``. Invoked after internal retries
                are exhausted OR were skipped via ``should_internal_retry`` returning
                False. Forwarded to
                :func:`airbyte_agent_sdk.translation.translate_exceptions`.

    ### Instance variables

    `connector_id: str | None`
    :   Get the connector/source ID (only available in hosted mode).
        
        Returns:
            The connector ID if in hosted mode, None if in local mode.

    ### Methods

    `check(self) ‑> airbyte_agent_sdk.connectors.mailchimp.models.MailchimpCheckResult`
    :   Perform a health check to verify connectivity and credentials.
        
        Executes a lightweight list operation (limit=1) to validate that
        the connector can communicate with the API and credentials are valid.
        
        Returns:
            MailchimpCheckResult with status ("healthy" or "unhealthy") and optional error message
        
        Example:
            result = await connector.check()
            if result.status == "healthy":
                print("Connection verified!")
            else:
                print(f"Check failed: \{result.error\}")

    `close(self)`
    :   Close the connector and release resources.

    `entity_schema(self, entity: str) ‑> dict[str, typing.Any] | None`
    :   Get the JSON schema for an entity.
        
        Args:
            entity: Entity name (e.g., "contacts", "companies")
        
        Returns:
            JSON schema dict describing the entity structure, or None if not found.
        
        Example:
            schema = connector.entity_schema("contacts")
            if schema:
                print(f"Contact properties: \{list(schema.get('properties', \{\}).keys())\}")

    `execute(self, entity: str, action: "Literal['list', 'get', 'context_store_search']", params: Mapping[str, Any] | None = None) ‑> Any`
    :   Execute an entity operation with full type safety.
        
        This is the recommended interface for blessed connectors as it:
        - Uses the same signature as non-blessed connectors
        - Provides full IDE autocomplete for entity/action/params
        - Makes migration from generic to blessed connectors seamless
        
        Args:
            entity: Entity name (e.g., "customers")
            action: Operation action (e.g., "create", "get", "list")
            params: Operation parameters (typed based on entity+action)
        
        Returns:
            Typed response based on the operation
        
        Example:
            customer = await connector.execute(
                entity="customers",
                action="get",
                params=\{"id": "cus_123"\}
            )

    `list_entities(self) ‑> list[dict[str, typing.Any]]`
    :   Get structured data about available entities, actions, and parameters.
        
        Returns a list of entity descriptions with:
        - entity_name: Name of the entity (e.g., "contacts", "deals")
        - description: Entity description from the first endpoint
        - available_actions: List of actions (e.g., ["list", "get", "create"])
        - parameters: Dict mapping action -> list of parameter dicts
        
        Example:
            entities = connector.list_entities()
            for entity in entities:
                print(f"\{entity['entity_name']\}: \{entity['available_actions']\}")

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

<a id="SegmentMembersSearchData"></a>

`SegmentMembersSearchData(**data: Any)`
:   Search result data for segment_members entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `email_address: str | None`
    :   Email address for a subscriber

    `email_client: str | None`
    :   The list member's email client

    `email_type: str | None`
    :   Type of email this member asked to get

    `id: str`
    :   The MD5 hash of the lowercase version of the list member's email address

    `interests: dict[str, typing.Any] | None`
    :   The key of this object's properties is the ID of the interest in question

    `ip_opt: str | None`
    :   The IP address the subscriber used to confirm their opt-in status

    `ip_signup: str | None`
    :   IP address the subscriber signed up from

    `language: str | None`
    :   If set/detected, the subscriber's language

    `last_changed: str | None`
    :   The date and time the member's info was last changed

    `list_id: str | None`
    :   The list id

    `location: dict[str, typing.Any] | None`
    :   Subscriber location information

    `member_rating: int | None`
    :   Star rating for this member, between 1 and 5

    `merge_fields: dict[str, typing.Any] | None`
    :   A dictionary of merge fields where the keys are the merge tags

    `model_config`
    :   The type of the None singleton.

    `stats: dict[str, typing.Any] | None`
    :   Open and click rates for this subscriber

    `status: str | None`
    :   Subscriber's current status

    `timestamp_opt: str | None`
    :   The date and time the subscriber confirmed their opt-in status

    `timestamp_signup: str | None`
    :   The date and time the subscriber signed up for the list

    `unique_email_id: str | None`
    :   An identifier for the address across all of Mailchimp

    `vip: bool | None`
    :   VIP status for subscriber

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

    `created_at: str | None`
    :   The date and time the segment was created

    `id: int`
    :   The unique id for the segment

    `list_id: str | None`
    :   The list id

    `member_count: int | None`
    :   The number of active subscribers currently included in the segment

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the segment

    `options: dict[str, typing.Any] | None`
    :   The conditions of the segment

    `type_: str | None`
    :   The type of segment

    `updated_at: str | None`
    :   The date and time the segment was last updated

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

    `id: int`
    :   The unique id for the tag

    `model_config`
    :   The type of the None singleton.

    `name: str | None`
    :   The name of the tag

<a id="UnsubscribesSearchData"></a>

`UnsubscribesSearchData(**data: Any)`
:   Search result data for unsubscribes entity.
    
    Create a new model by parsing and validating input data from keyword arguments.
    
    Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
    validated to form a valid model.
    
    `self` is explicitly positional-only to allow `self` as a field name.

    ### Ancestors (in MRO)

    * pydantic.main.BaseModel

    ### Class variables

    `campaign_id: str | None`
    :   The campaign id

    `email_address: str | None`
    :   Email address for a subscriber

    `email_id: str | None`
    :   The MD5 hash of the lowercase version of the list member's email address

    `list_id: str | None`
    :   The list id

    `list_is_active: bool | None`
    :   The status of the list used

    `merge_fields: dict[str, typing.Any] | None`
    :   A dictionary of merge fields where the keys are the merge tags

    `model_config`
    :   The type of the None singleton.

    `reason: str | None`
    :   If available, the reason listed by the member for unsubscribing

    `timestamp: str | None`
    :   The date and time the member opted-out

    `vip: bool | None`
    :   VIP status for subscriber