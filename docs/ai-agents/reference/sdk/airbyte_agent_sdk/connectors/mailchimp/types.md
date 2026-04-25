---
id: airbyte_agent_sdk-connectors-mailchimp-types
title: airbyte_agent_sdk.connectors.mailchimp.types
---

Module airbyte_agent_sdk.connectors.mailchimp.types
===================================================
Type definitions for mailchimp connector.

Classes
-------

<a id="AirbyteSearchParams"></a>

`AirbyteSearchParams(*args, **kwargs)`
:   Parameters for Airbyte cache search operations (generic, use entity-specific query types for better type hints).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `fields: list[list[str]]`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `query: dict[str, typing.Any]`
    :   The type of the None singleton.

<a id="AutomationsListParams"></a>

`AutomationsListParams(*args, **kwargs)`
:   Parameters for automations.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `before_create_time: str`
    :   The type of the None singleton.

    `before_start_time: str`
    :   The type of the None singleton.

    `count: int`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

    `since_create_time: str`
    :   The type of the None singleton.

    `since_start_time: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

<a id="CampaignsAndCondition"></a>

`CampaignsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.mailchimp.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsInCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignsAnyCondition"></a>

`CampaignsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.mailchimp.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsAnyValueFilter"></a>

`CampaignsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ab_split_opts: Any`
    :   [A/B Testing](https://mailchimp.com/help/about-ab-testing-campaigns/) options for a campaign.

    `archive_url: Any`
    :   The link to the campaign's archive version in ISO 8601 format.

    `content_type: Any`
    :   How the campaign's content is put together.

    `create_time: Any`
    :   The date and time the campaign was created in ISO 8601 format.

    `delivery_status: Any`
    :   Updates on campaigns in the process of sending.

    `emails_sent: Any`
    :   The total number of emails sent for this campaign.

    `id: Any`
    :   A string that uniquely identifies this campaign.

    `long_archive_url: Any`
    :   The original link to the campaign's archive version.

    `needs_block_refresh: Any`
    :   Determines if the campaign needs its blocks refreshed by opening the web-based campaign editor. D...

    `parent_campaign_id: Any`
    :   If this campaign is the child of another campaign, this identifies the parent campaign. For Examp...

    `recipients: Any`
    :   List settings for the campaign.

    `report_summary: Any`
    :   For sent campaigns, a summary of opens, clicks, and e-commerce data.

    `resendable: Any`
    :   Determines if the campaign qualifies to be resent to non-openers.

    `rss_opts: Any`
    :   [RSS](https://mailchimp.com/help/share-your-blog-posts-with-mailchimp/) options for a campaign.

    `send_time: Any`
    :   The date and time a campaign was sent.

    `settings: Any`
    :   The settings for your campaign, including subject, from name, reply-to address, and more.

    `social_card: Any`
    :   The preview for the campaign, rendered by social networks like Facebook and Twitter. [Learn more]...

    `status: Any`
    :   The current status of the campaign.

    `tracking: Any`
    :   The tracking options for a campaign.

    `type_: Any`
    :   There are four types of [campaigns](https://mailchimp.com/help/getting-started-with-campaigns/) y...

    `variate_settings: Any`
    :   The settings specific to A/B test campaigns.

    `web_id: Any`
    :   The ID used in the Mailchimp web application. View this campaign in your Mailchimp account at `ht...

<a id="CampaignsContainsCondition"></a>

`CampaignsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.mailchimp.types.CampaignsAnyValueFilter`
    :   The type of the None singleton.

<a id="CampaignsEqCondition"></a>

`CampaignsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.mailchimp.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsFuzzyCondition"></a>

`CampaignsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.mailchimp.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsGetParams"></a>

`CampaignsGetParams(*args, **kwargs)`
:   Parameters for campaigns.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: str`
    :   The type of the None singleton.

<a id="CampaignsGtCondition"></a>

`CampaignsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.mailchimp.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsGteCondition"></a>

`CampaignsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.mailchimp.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsInCondition"></a>

`CampaignsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.mailchimp.types.CampaignsInFilter`
    :   The type of the None singleton.

<a id="CampaignsInFilter"></a>

`CampaignsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ab_split_opts: list[dict[str, typing.Any]]`
    :   [A/B Testing](https://mailchimp.com/help/about-ab-testing-campaigns/) options for a campaign.

    `archive_url: list[str]`
    :   The link to the campaign's archive version in ISO 8601 format.

    `content_type: list[str]`
    :   How the campaign's content is put together.

    `create_time: list[str]`
    :   The date and time the campaign was created in ISO 8601 format.

    `delivery_status: list[dict[str, typing.Any]]`
    :   Updates on campaigns in the process of sending.

    `emails_sent: list[int]`
    :   The total number of emails sent for this campaign.

    `id: list[str]`
    :   A string that uniquely identifies this campaign.

    `long_archive_url: list[str]`
    :   The original link to the campaign's archive version.

    `needs_block_refresh: list[bool]`
    :   Determines if the campaign needs its blocks refreshed by opening the web-based campaign editor. D...

    `parent_campaign_id: list[str]`
    :   If this campaign is the child of another campaign, this identifies the parent campaign. For Examp...

    `recipients: list[dict[str, typing.Any]]`
    :   List settings for the campaign.

    `report_summary: list[dict[str, typing.Any]]`
    :   For sent campaigns, a summary of opens, clicks, and e-commerce data.

    `resendable: list[bool]`
    :   Determines if the campaign qualifies to be resent to non-openers.

    `rss_opts: list[dict[str, typing.Any]]`
    :   [RSS](https://mailchimp.com/help/share-your-blog-posts-with-mailchimp/) options for a campaign.

    `send_time: list[str]`
    :   The date and time a campaign was sent.

    `settings: list[dict[str, typing.Any]]`
    :   The settings for your campaign, including subject, from name, reply-to address, and more.

    `social_card: list[dict[str, typing.Any]]`
    :   The preview for the campaign, rendered by social networks like Facebook and Twitter. [Learn more]...

    `status: list[str]`
    :   The current status of the campaign.

    `tracking: list[dict[str, typing.Any]]`
    :   The tracking options for a campaign.

    `type_: list[str]`
    :   There are four types of [campaigns](https://mailchimp.com/help/getting-started-with-campaigns/) y...

    `variate_settings: list[dict[str, typing.Any]]`
    :   The settings specific to A/B test campaigns.

    `web_id: list[int]`
    :   The ID used in the Mailchimp web application. View this campaign in your Mailchimp account at `ht...

<a id="CampaignsKeywordCondition"></a>

`CampaignsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.mailchimp.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsLikeCondition"></a>

`CampaignsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.mailchimp.types.CampaignsStringFilter`
    :   The type of the None singleton.

<a id="CampaignsListParams"></a>

`CampaignsListParams(*args, **kwargs)`
:   Parameters for campaigns.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `before_create_time: str`
    :   The type of the None singleton.

    `before_send_time: str`
    :   The type of the None singleton.

    `count: int`
    :   The type of the None singleton.

    `folder_id: str`
    :   The type of the None singleton.

    `list_id: str`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

    `since_create_time: str`
    :   The type of the None singleton.

    `since_send_time: str`
    :   The type of the None singleton.

    `sort_dir: str`
    :   The type of the None singleton.

    `sort_field: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="CampaignsLtCondition"></a>

`CampaignsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.mailchimp.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsLteCondition"></a>

`CampaignsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.mailchimp.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsNeqCondition"></a>

`CampaignsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.mailchimp.types.CampaignsSearchFilter`
    :   The type of the None singleton.

<a id="CampaignsNotCondition"></a>

`CampaignsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.mailchimp.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsInCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsAnyCondition`
    :   The type of the None singleton.

<a id="CampaignsOrCondition"></a>

`CampaignsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.mailchimp.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsInCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsAnyCondition]`
    :   The type of the None singleton.

<a id="CampaignsSearchFilter"></a>

`CampaignsSearchFilter(*args, **kwargs)`
:   Available fields for filtering campaigns search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="CampaignsSearchQuery"></a>

`CampaignsSearchQuery(*args, **kwargs)`
:   Search query for campaigns entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.mailchimp.types.CampaignsEqCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsNeqCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsGtCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsGteCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsLtCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsLteCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsInCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsLikeCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsFuzzyCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsKeywordCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsContainsCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsNotCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsAndCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsOrCondition | airbyte_agent_sdk.connectors.mailchimp.types.CampaignsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.mailchimp.types.CampaignsSortFilter]`
    :   The type of the None singleton.

<a id="CampaignsSortFilter"></a>

`CampaignsSortFilter(*args, **kwargs)`
:   Available fields for sorting campaigns search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ab_split_opts: Literal['asc', 'desc']`
    :   [A/B Testing](https://mailchimp.com/help/about-ab-testing-campaigns/) options for a campaign.

    `archive_url: Literal['asc', 'desc']`
    :   The link to the campaign's archive version in ISO 8601 format.

    `content_type: Literal['asc', 'desc']`
    :   How the campaign's content is put together.

    `create_time: Literal['asc', 'desc']`
    :   The date and time the campaign was created in ISO 8601 format.

    `delivery_status: Literal['asc', 'desc']`
    :   Updates on campaigns in the process of sending.

    `emails_sent: Literal['asc', 'desc']`
    :   The total number of emails sent for this campaign.

    `id: Literal['asc', 'desc']`
    :   A string that uniquely identifies this campaign.

    `long_archive_url: Literal['asc', 'desc']`
    :   The original link to the campaign's archive version.

    `needs_block_refresh: Literal['asc', 'desc']`
    :   Determines if the campaign needs its blocks refreshed by opening the web-based campaign editor. D...

    `parent_campaign_id: Literal['asc', 'desc']`
    :   If this campaign is the child of another campaign, this identifies the parent campaign. For Examp...

    `recipients: Literal['asc', 'desc']`
    :   List settings for the campaign.

    `report_summary: Literal['asc', 'desc']`
    :   For sent campaigns, a summary of opens, clicks, and e-commerce data.

    `resendable: Literal['asc', 'desc']`
    :   Determines if the campaign qualifies to be resent to non-openers.

    `rss_opts: Literal['asc', 'desc']`
    :   [RSS](https://mailchimp.com/help/share-your-blog-posts-with-mailchimp/) options for a campaign.

    `send_time: Literal['asc', 'desc']`
    :   The date and time a campaign was sent.

    `settings: Literal['asc', 'desc']`
    :   The settings for your campaign, including subject, from name, reply-to address, and more.

    `social_card: Literal['asc', 'desc']`
    :   The preview for the campaign, rendered by social networks like Facebook and Twitter. [Learn more]...

    `status: Literal['asc', 'desc']`
    :   The current status of the campaign.

    `tracking: Literal['asc', 'desc']`
    :   The tracking options for a campaign.

    `type_: Literal['asc', 'desc']`
    :   There are four types of [campaigns](https://mailchimp.com/help/getting-started-with-campaigns/) y...

    `variate_settings: Literal['asc', 'desc']`
    :   The settings specific to A/B test campaigns.

    `web_id: Literal['asc', 'desc']`
    :   The ID used in the Mailchimp web application. View this campaign in your Mailchimp account at `ht...

<a id="CampaignsStringFilter"></a>

`CampaignsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ab_split_opts: str`
    :   [A/B Testing](https://mailchimp.com/help/about-ab-testing-campaigns/) options for a campaign.

    `archive_url: str`
    :   The link to the campaign's archive version in ISO 8601 format.

    `content_type: str`
    :   How the campaign's content is put together.

    `create_time: str`
    :   The date and time the campaign was created in ISO 8601 format.

    `delivery_status: str`
    :   Updates on campaigns in the process of sending.

    `emails_sent: str`
    :   The total number of emails sent for this campaign.

    `id: str`
    :   A string that uniquely identifies this campaign.

    `long_archive_url: str`
    :   The original link to the campaign's archive version.

    `needs_block_refresh: str`
    :   Determines if the campaign needs its blocks refreshed by opening the web-based campaign editor. D...

    `parent_campaign_id: str`
    :   If this campaign is the child of another campaign, this identifies the parent campaign. For Examp...

    `recipients: str`
    :   List settings for the campaign.

    `report_summary: str`
    :   For sent campaigns, a summary of opens, clicks, and e-commerce data.

    `resendable: str`
    :   Determines if the campaign qualifies to be resent to non-openers.

    `rss_opts: str`
    :   [RSS](https://mailchimp.com/help/share-your-blog-posts-with-mailchimp/) options for a campaign.

    `send_time: str`
    :   The date and time a campaign was sent.

    `settings: str`
    :   The settings for your campaign, including subject, from name, reply-to address, and more.

    `social_card: str`
    :   The preview for the campaign, rendered by social networks like Facebook and Twitter. [Learn more]...

    `status: str`
    :   The current status of the campaign.

    `tracking: str`
    :   The tracking options for a campaign.

    `type_: str`
    :   There are four types of [campaigns](https://mailchimp.com/help/getting-started-with-campaigns/) y...

    `variate_settings: str`
    :   The settings specific to A/B test campaigns.

    `web_id: str`
    :   The ID used in the Mailchimp web application. View this campaign in your Mailchimp account at `ht...

<a id="EmailActivityAndCondition"></a>

`EmailActivityAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityEqCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityNeqCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityGtCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityGteCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityLtCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityLteCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityInCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityLikeCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityFuzzyCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityKeywordCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityContainsCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityNotCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityAndCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityOrCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityAnyCondition]`
    :   The type of the None singleton.

<a id="EmailActivityAnyCondition"></a>

`EmailActivityAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityAnyValueFilter`
    :   The type of the None singleton.

<a id="EmailActivityAnyValueFilter"></a>

`EmailActivityAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action: Any`
    :   One of the following actions: 'open', 'click', or 'bounce'

    `campaign_id: Any`
    :   The unique id for the campaign.

    `email_address: Any`
    :   Email address for a subscriber.

    `email_id: Any`
    :   The MD5 hash of the lowercase version of the list member's email address.

    `ip: Any`
    :   The IP address recorded for the action.

    `list_id: Any`
    :   The unique id for the list.

    `list_is_active: Any`
    :   The status of the list used, namely if it's deleted or disabled.

    `timestamp: Any`
    :   The date and time recorded for the action in ISO 8601 format.

    `type_: Any`
    :   If the action is a 'bounce', the type of bounce received: 'hard', 'soft'.

    `url: Any`
    :   If the action is a 'click', the URL on which the member clicked.

<a id="EmailActivityContainsCondition"></a>

`EmailActivityContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityAnyValueFilter`
    :   The type of the None singleton.

<a id="EmailActivityEqCondition"></a>

`EmailActivityEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.mailchimp.types.EmailActivitySearchFilter`
    :   The type of the None singleton.

<a id="EmailActivityFuzzyCondition"></a>

`EmailActivityFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityStringFilter`
    :   The type of the None singleton.

<a id="EmailActivityGtCondition"></a>

`EmailActivityGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.mailchimp.types.EmailActivitySearchFilter`
    :   The type of the None singleton.

<a id="EmailActivityGteCondition"></a>

`EmailActivityGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.mailchimp.types.EmailActivitySearchFilter`
    :   The type of the None singleton.

<a id="EmailActivityInCondition"></a>

`EmailActivityInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityInFilter`
    :   The type of the None singleton.

<a id="EmailActivityInFilter"></a>

`EmailActivityInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action: list[str]`
    :   One of the following actions: 'open', 'click', or 'bounce'

    `campaign_id: list[str]`
    :   The unique id for the campaign.

    `email_address: list[str]`
    :   Email address for a subscriber.

    `email_id: list[str]`
    :   The MD5 hash of the lowercase version of the list member's email address.

    `ip: list[str]`
    :   The IP address recorded for the action.

    `list_id: list[str]`
    :   The unique id for the list.

    `list_is_active: list[bool]`
    :   The status of the list used, namely if it's deleted or disabled.

    `timestamp: list[str]`
    :   The date and time recorded for the action in ISO 8601 format.

    `type_: list[str]`
    :   If the action is a 'bounce', the type of bounce received: 'hard', 'soft'.

    `url: list[str]`
    :   If the action is a 'click', the URL on which the member clicked.

<a id="EmailActivityKeywordCondition"></a>

`EmailActivityKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityStringFilter`
    :   The type of the None singleton.

<a id="EmailActivityLikeCondition"></a>

`EmailActivityLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityStringFilter`
    :   The type of the None singleton.

<a id="EmailActivityListParams"></a>

`EmailActivityListParams(*args, **kwargs)`
:   Parameters for email_activity.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: str`
    :   The type of the None singleton.

    `count: int`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

    `since: str`
    :   The type of the None singleton.

<a id="EmailActivityLtCondition"></a>

`EmailActivityLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.mailchimp.types.EmailActivitySearchFilter`
    :   The type of the None singleton.

<a id="EmailActivityLteCondition"></a>

`EmailActivityLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.mailchimp.types.EmailActivitySearchFilter`
    :   The type of the None singleton.

<a id="EmailActivityNeqCondition"></a>

`EmailActivityNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.mailchimp.types.EmailActivitySearchFilter`
    :   The type of the None singleton.

<a id="EmailActivityNotCondition"></a>

`EmailActivityNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityEqCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityNeqCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityGtCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityGteCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityLtCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityLteCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityInCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityLikeCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityFuzzyCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityKeywordCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityContainsCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityNotCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityAndCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityOrCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityAnyCondition`
    :   The type of the None singleton.

<a id="EmailActivityOrCondition"></a>

`EmailActivityOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityEqCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityNeqCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityGtCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityGteCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityLtCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityLteCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityInCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityLikeCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityFuzzyCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityKeywordCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityContainsCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityNotCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityAndCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityOrCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityAnyCondition]`
    :   The type of the None singleton.

<a id="EmailActivitySearchFilter"></a>

`EmailActivitySearchFilter(*args, **kwargs)`
:   Available fields for filtering email_activity search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

    `timestamp: str | None`
    :   The date and time recorded for the action in ISO 8601 format.

    `type_: str | None`
    :   If the action is a 'bounce', the type of bounce received: 'hard', 'soft'.

    `url: str | None`
    :   If the action is a 'click', the URL on which the member clicked.

<a id="EmailActivitySearchQuery"></a>

`EmailActivitySearchQuery(*args, **kwargs)`
:   Search query for email_activity entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityEqCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityNeqCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityGtCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityGteCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityLtCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityLteCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityInCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityLikeCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityFuzzyCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityKeywordCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityContainsCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityNotCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityAndCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityOrCondition | airbyte_agent_sdk.connectors.mailchimp.types.EmailActivityAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.mailchimp.types.EmailActivitySortFilter]`
    :   The type of the None singleton.

<a id="EmailActivitySortFilter"></a>

`EmailActivitySortFilter(*args, **kwargs)`
:   Available fields for sorting email_activity search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action: Literal['asc', 'desc']`
    :   One of the following actions: 'open', 'click', or 'bounce'

    `campaign_id: Literal['asc', 'desc']`
    :   The unique id for the campaign.

    `email_address: Literal['asc', 'desc']`
    :   Email address for a subscriber.

    `email_id: Literal['asc', 'desc']`
    :   The MD5 hash of the lowercase version of the list member's email address.

    `ip: Literal['asc', 'desc']`
    :   The IP address recorded for the action.

    `list_id: Literal['asc', 'desc']`
    :   The unique id for the list.

    `list_is_active: Literal['asc', 'desc']`
    :   The status of the list used, namely if it's deleted or disabled.

    `timestamp: Literal['asc', 'desc']`
    :   The date and time recorded for the action in ISO 8601 format.

    `type_: Literal['asc', 'desc']`
    :   If the action is a 'bounce', the type of bounce received: 'hard', 'soft'.

    `url: Literal['asc', 'desc']`
    :   If the action is a 'click', the URL on which the member clicked.

<a id="EmailActivityStringFilter"></a>

`EmailActivityStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `action: str`
    :   One of the following actions: 'open', 'click', or 'bounce'

    `campaign_id: str`
    :   The unique id for the campaign.

    `email_address: str`
    :   Email address for a subscriber.

    `email_id: str`
    :   The MD5 hash of the lowercase version of the list member's email address.

    `ip: str`
    :   The IP address recorded for the action.

    `list_id: str`
    :   The unique id for the list.

    `list_is_active: str`
    :   The status of the list used, namely if it's deleted or disabled.

    `timestamp: str`
    :   The date and time recorded for the action in ISO 8601 format.

    `type_: str`
    :   If the action is a 'bounce', the type of bounce received: 'hard', 'soft'.

    `url: str`
    :   If the action is a 'click', the URL on which the member clicked.

<a id="InterestCategoriesGetParams"></a>

`InterestCategoriesGetParams(*args, **kwargs)`
:   Parameters for interest_categories.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `interest_category_id: str`
    :   The type of the None singleton.

    `list_id: str`
    :   The type of the None singleton.

<a id="InterestCategoriesListParams"></a>

`InterestCategoriesListParams(*args, **kwargs)`
:   Parameters for interest_categories.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: int`
    :   The type of the None singleton.

    `list_id: str`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

<a id="InterestsGetParams"></a>

`InterestsGetParams(*args, **kwargs)`
:   Parameters for interests.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `interest_category_id: str`
    :   The type of the None singleton.

    `interest_id: str`
    :   The type of the None singleton.

    `list_id: str`
    :   The type of the None singleton.

<a id="InterestsListParams"></a>

`InterestsListParams(*args, **kwargs)`
:   Parameters for interests.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: int`
    :   The type of the None singleton.

    `interest_category_id: str`
    :   The type of the None singleton.

    `list_id: str`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

<a id="ListMembersGetParams"></a>

`ListMembersGetParams(*args, **kwargs)`
:   Parameters for list_members.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `list_id: str`
    :   The type of the None singleton.

    `subscriber_hash: str`
    :   The type of the None singleton.

<a id="ListMembersListParams"></a>

`ListMembersListParams(*args, **kwargs)`
:   Parameters for list_members.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `before_last_changed: str`
    :   The type of the None singleton.

    `before_timestamp_opt: str`
    :   The type of the None singleton.

    `count: int`
    :   The type of the None singleton.

    `email_type: str`
    :   The type of the None singleton.

    `interest_category_id: str`
    :   The type of the None singleton.

    `interest_ids: str`
    :   The type of the None singleton.

    `interest_match: str`
    :   The type of the None singleton.

    `list_id: str`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

    `since_last_changed: str`
    :   The type of the None singleton.

    `since_timestamp_opt: str`
    :   The type of the None singleton.

    `sort_dir: str`
    :   The type of the None singleton.

    `sort_field: str`
    :   The type of the None singleton.

    `status: str`
    :   The type of the None singleton.

    `unique_email_id: str`
    :   The type of the None singleton.

    `vip_only: bool`
    :   The type of the None singleton.

<a id="ListsAndCondition"></a>

`ListsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.mailchimp.types.ListsEqCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsNeqCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsGtCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsGteCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsLtCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsLteCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsInCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsLikeCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsContainsCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsNotCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsAndCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsOrCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsAnyCondition]`
    :   The type of the None singleton.

<a id="ListsAnyCondition"></a>

`ListsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.mailchimp.types.ListsAnyValueFilter`
    :   The type of the None singleton.

<a id="ListsAnyValueFilter"></a>

`ListsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `beamer_address: Any`
    :   The list's Email Beamer address.

    `campaign_defaults: Any`
    :   Default values for campaigns created for this list.

    `contact: Any`
    :   Contact information displayed in campaign footers to comply with international spam laws.

    `date_created: Any`
    :   The date and time that this list was created in ISO 8601 format.

    `double_optin: Any`
    :   Whether or not to require the subscriber to confirm subscription via email.

    `email_type_option: Any`
    :   Whether the list supports multiple formats for emails. When set to `true`, subscribers can choose...

    `has_welcome: Any`
    :   Whether or not this list has a welcome automation connected.

    `id: Any`
    :   A string that uniquely identifies this list.

    `list_rating: Any`
    :   An auto-generated activity score for the list (0-5).

    `marketing_permissions: Any`
    :   Whether or not the list has marketing permissions (eg. GDPR) enabled.

    `modules: Any`
    :   Any list-specific modules installed for this list.

    `name: Any`
    :   The name of the list.

    `notify_on_subscribe: Any`
    :   The email address to send subscribe notifications to.

    `notify_on_unsubscribe: Any`
    :   The email address to send unsubscribe notifications to.

    `permission_reminder: Any`
    :   The permission reminder for the list.

    `stats: Any`
    :   Stats for the list. Many of these are cached for at least five minutes.

    `subscribe_url_long: Any`
    :   The full version of this list's subscribe form (host will vary).

    `subscribe_url_short: Any`
    :   Our EepURL shortened version of this list's subscribe form.

    `use_archive_bar: Any`
    :   Whether campaigns for this list use the Archive Bar in archives by default.

    `visibility: Any`
    :   Whether this list is public or private.

    `web_id: Any`
    :   The ID used in the Mailchimp web application. View this list in your Mailchimp account at `https:...

<a id="ListsContainsCondition"></a>

`ListsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.mailchimp.types.ListsAnyValueFilter`
    :   The type of the None singleton.

<a id="ListsEqCondition"></a>

`ListsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.mailchimp.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsFuzzyCondition"></a>

`ListsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.mailchimp.types.ListsStringFilter`
    :   The type of the None singleton.

<a id="ListsGetParams"></a>

`ListsGetParams(*args, **kwargs)`
:   Parameters for lists.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `list_id: str`
    :   The type of the None singleton.

<a id="ListsGtCondition"></a>

`ListsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.mailchimp.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsGteCondition"></a>

`ListsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.mailchimp.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsInCondition"></a>

`ListsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.mailchimp.types.ListsInFilter`
    :   The type of the None singleton.

<a id="ListsInFilter"></a>

`ListsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `beamer_address: list[str]`
    :   The list's Email Beamer address.

    `campaign_defaults: list[dict[str, typing.Any]]`
    :   Default values for campaigns created for this list.

    `contact: list[dict[str, typing.Any]]`
    :   Contact information displayed in campaign footers to comply with international spam laws.

    `date_created: list[str]`
    :   The date and time that this list was created in ISO 8601 format.

    `double_optin: list[bool]`
    :   Whether or not to require the subscriber to confirm subscription via email.

    `email_type_option: list[bool]`
    :   Whether the list supports multiple formats for emails. When set to `true`, subscribers can choose...

    `has_welcome: list[bool]`
    :   Whether or not this list has a welcome automation connected.

    `id: list[str]`
    :   A string that uniquely identifies this list.

    `list_rating: list[int]`
    :   An auto-generated activity score for the list (0-5).

    `marketing_permissions: list[bool]`
    :   Whether or not the list has marketing permissions (eg. GDPR) enabled.

    `modules: list[list[typing.Any]]`
    :   Any list-specific modules installed for this list.

    `name: list[str]`
    :   The name of the list.

    `notify_on_subscribe: list[str]`
    :   The email address to send subscribe notifications to.

    `notify_on_unsubscribe: list[str]`
    :   The email address to send unsubscribe notifications to.

    `permission_reminder: list[str]`
    :   The permission reminder for the list.

    `stats: list[dict[str, typing.Any]]`
    :   Stats for the list. Many of these are cached for at least five minutes.

    `subscribe_url_long: list[str]`
    :   The full version of this list's subscribe form (host will vary).

    `subscribe_url_short: list[str]`
    :   Our EepURL shortened version of this list's subscribe form.

    `use_archive_bar: list[bool]`
    :   Whether campaigns for this list use the Archive Bar in archives by default.

    `visibility: list[str]`
    :   Whether this list is public or private.

    `web_id: list[int]`
    :   The ID used in the Mailchimp web application. View this list in your Mailchimp account at `https:...

<a id="ListsKeywordCondition"></a>

`ListsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.mailchimp.types.ListsStringFilter`
    :   The type of the None singleton.

<a id="ListsLikeCondition"></a>

`ListsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.mailchimp.types.ListsStringFilter`
    :   The type of the None singleton.

<a id="ListsListParams"></a>

`ListsListParams(*args, **kwargs)`
:   Parameters for lists.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `before_campaign_last_sent: str`
    :   The type of the None singleton.

    `before_date_created: str`
    :   The type of the None singleton.

    `count: int`
    :   The type of the None singleton.

    `email: str`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

    `since_campaign_last_sent: str`
    :   The type of the None singleton.

    `since_date_created: str`
    :   The type of the None singleton.

    `sort_dir: str`
    :   The type of the None singleton.

    `sort_field: str`
    :   The type of the None singleton.

<a id="ListsLtCondition"></a>

`ListsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.mailchimp.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsLteCondition"></a>

`ListsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.mailchimp.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsNeqCondition"></a>

`ListsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.mailchimp.types.ListsSearchFilter`
    :   The type of the None singleton.

<a id="ListsNotCondition"></a>

`ListsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.mailchimp.types.ListsEqCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsNeqCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsGtCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsGteCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsLtCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsLteCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsInCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsLikeCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsContainsCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsNotCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsAndCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsOrCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsAnyCondition`
    :   The type of the None singleton.

<a id="ListsOrCondition"></a>

`ListsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.mailchimp.types.ListsEqCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsNeqCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsGtCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsGteCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsLtCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsLteCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsInCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsLikeCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsContainsCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsNotCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsAndCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsOrCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsAnyCondition]`
    :   The type of the None singleton.

<a id="ListsSearchFilter"></a>

`ListsSearchFilter(*args, **kwargs)`
:   Available fields for filtering lists search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="ListsSearchQuery"></a>

`ListsSearchQuery(*args, **kwargs)`
:   Search query for lists entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.mailchimp.types.ListsEqCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsNeqCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsGtCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsGteCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsLtCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsLteCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsInCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsLikeCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsFuzzyCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsKeywordCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsContainsCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsNotCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsAndCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsOrCondition | airbyte_agent_sdk.connectors.mailchimp.types.ListsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.mailchimp.types.ListsSortFilter]`
    :   The type of the None singleton.

<a id="ListsSortFilter"></a>

`ListsSortFilter(*args, **kwargs)`
:   Available fields for sorting lists search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `beamer_address: Literal['asc', 'desc']`
    :   The list's Email Beamer address.

    `campaign_defaults: Literal['asc', 'desc']`
    :   Default values for campaigns created for this list.

    `contact: Literal['asc', 'desc']`
    :   Contact information displayed in campaign footers to comply with international spam laws.

    `date_created: Literal['asc', 'desc']`
    :   The date and time that this list was created in ISO 8601 format.

    `double_optin: Literal['asc', 'desc']`
    :   Whether or not to require the subscriber to confirm subscription via email.

    `email_type_option: Literal['asc', 'desc']`
    :   Whether the list supports multiple formats for emails. When set to `true`, subscribers can choose...

    `has_welcome: Literal['asc', 'desc']`
    :   Whether or not this list has a welcome automation connected.

    `id: Literal['asc', 'desc']`
    :   A string that uniquely identifies this list.

    `list_rating: Literal['asc', 'desc']`
    :   An auto-generated activity score for the list (0-5).

    `marketing_permissions: Literal['asc', 'desc']`
    :   Whether or not the list has marketing permissions (eg. GDPR) enabled.

    `modules: Literal['asc', 'desc']`
    :   Any list-specific modules installed for this list.

    `name: Literal['asc', 'desc']`
    :   The name of the list.

    `notify_on_subscribe: Literal['asc', 'desc']`
    :   The email address to send subscribe notifications to.

    `notify_on_unsubscribe: Literal['asc', 'desc']`
    :   The email address to send unsubscribe notifications to.

    `permission_reminder: Literal['asc', 'desc']`
    :   The permission reminder for the list.

    `stats: Literal['asc', 'desc']`
    :   Stats for the list. Many of these are cached for at least five minutes.

    `subscribe_url_long: Literal['asc', 'desc']`
    :   The full version of this list's subscribe form (host will vary).

    `subscribe_url_short: Literal['asc', 'desc']`
    :   Our EepURL shortened version of this list's subscribe form.

    `use_archive_bar: Literal['asc', 'desc']`
    :   Whether campaigns for this list use the Archive Bar in archives by default.

    `visibility: Literal['asc', 'desc']`
    :   Whether this list is public or private.

    `web_id: Literal['asc', 'desc']`
    :   The ID used in the Mailchimp web application. View this list in your Mailchimp account at `https:...

<a id="ListsStringFilter"></a>

`ListsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `beamer_address: str`
    :   The list's Email Beamer address.

    `campaign_defaults: str`
    :   Default values for campaigns created for this list.

    `contact: str`
    :   Contact information displayed in campaign footers to comply with international spam laws.

    `date_created: str`
    :   The date and time that this list was created in ISO 8601 format.

    `double_optin: str`
    :   Whether or not to require the subscriber to confirm subscription via email.

    `email_type_option: str`
    :   Whether the list supports multiple formats for emails. When set to `true`, subscribers can choose...

    `has_welcome: str`
    :   Whether or not this list has a welcome automation connected.

    `id: str`
    :   A string that uniquely identifies this list.

    `list_rating: str`
    :   An auto-generated activity score for the list (0-5).

    `marketing_permissions: str`
    :   Whether or not the list has marketing permissions (eg. GDPR) enabled.

    `modules: str`
    :   Any list-specific modules installed for this list.

    `name: str`
    :   The name of the list.

    `notify_on_subscribe: str`
    :   The email address to send subscribe notifications to.

    `notify_on_unsubscribe: str`
    :   The email address to send unsubscribe notifications to.

    `permission_reminder: str`
    :   The permission reminder for the list.

    `stats: str`
    :   Stats for the list. Many of these are cached for at least five minutes.

    `subscribe_url_long: str`
    :   The full version of this list's subscribe form (host will vary).

    `subscribe_url_short: str`
    :   Our EepURL shortened version of this list's subscribe form.

    `use_archive_bar: str`
    :   Whether campaigns for this list use the Archive Bar in archives by default.

    `visibility: str`
    :   Whether this list is public or private.

    `web_id: str`
    :   The ID used in the Mailchimp web application. View this list in your Mailchimp account at `https:...

<a id="ReportsAndCondition"></a>

`ReportsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.mailchimp.types.ReportsEqCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsNeqCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsGtCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsGteCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsLtCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsLteCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsInCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsLikeCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsFuzzyCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsKeywordCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsContainsCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsNotCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsAndCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsOrCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsAnyCondition]`
    :   The type of the None singleton.

<a id="ReportsAnyCondition"></a>

`ReportsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.mailchimp.types.ReportsAnyValueFilter`
    :   The type of the None singleton.

<a id="ReportsAnyValueFilter"></a>

`ReportsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ab_split: Any`
    :   General stats about different groups of an A/B Split campaign. Does not return information about ...

    `abuse_reports: Any`
    :   The number of abuse reports generated for this campaign.

    `bounces: Any`
    :   An object describing the bounce summary for the campaign.

    `campaign_title: Any`
    :   The title of the campaign.

    `clicks: Any`
    :   An object describing the click activity for the campaign.

    `delivery_status: Any`
    :   Updates on campaigns in the process of sending.

    `ecommerce: Any`
    :   E-Commerce stats for a campaign.

    `emails_sent: Any`
    :   The total number of emails sent for this campaign.

    `facebook_likes: Any`
    :   An object describing campaign engagement on Facebook.

    `forwards: Any`
    :   An object describing the forwards and forward activity for the campaign.

    `id: Any`
    :   A string that uniquely identifies this campaign.

    `industry_stats: Any`
    :   The average campaign statistics for your industry.

    `list_id: Any`
    :   The unique list id.

    `list_is_active: Any`
    :   The status of the list used, namely if it's deleted or disabled.

    `list_name: Any`
    :   The name of the list.

    `list_stats: Any`
    :   The average campaign statistics for your list. This won't be present if we haven't calculated i...

    `opens: Any`
    :   An object describing the open activity for the campaign.

    `preview_text: Any`
    :   The preview text for the campaign.

    `rss_last_send: Any`
    :   For RSS campaigns, the date and time of the last send in ISO 8601 format.

    `send_time: Any`
    :   The date and time a campaign was sent in ISO 8601 format.

    `share_report: Any`
    :   The url and password for the VIP report.

    `subject_line: Any`
    :   The subject line for the campaign.

    `timeseries: Any`
    :   An hourly breakdown of the performance of the campaign over the first 24 hours.

    `timewarp: Any`
    :   An hourly breakdown of sends, opens, and clicks if a campaign is sent using timewarp.

    `type_: Any`
    :   The type of campaign (regular, plain-text, ab_split, rss, automation, variate, or auto).

    `unsubscribed: Any`
    :   The total number of unsubscribed members for this campaign.

<a id="ReportsContainsCondition"></a>

`ReportsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.mailchimp.types.ReportsAnyValueFilter`
    :   The type of the None singleton.

<a id="ReportsEqCondition"></a>

`ReportsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.mailchimp.types.ReportsSearchFilter`
    :   The type of the None singleton.

<a id="ReportsFuzzyCondition"></a>

`ReportsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.mailchimp.types.ReportsStringFilter`
    :   The type of the None singleton.

<a id="ReportsGetParams"></a>

`ReportsGetParams(*args, **kwargs)`
:   Parameters for reports.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: str`
    :   The type of the None singleton.

<a id="ReportsGtCondition"></a>

`ReportsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.mailchimp.types.ReportsSearchFilter`
    :   The type of the None singleton.

<a id="ReportsGteCondition"></a>

`ReportsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.mailchimp.types.ReportsSearchFilter`
    :   The type of the None singleton.

<a id="ReportsInCondition"></a>

`ReportsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.mailchimp.types.ReportsInFilter`
    :   The type of the None singleton.

<a id="ReportsInFilter"></a>

`ReportsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ab_split: list[dict[str, typing.Any]]`
    :   General stats about different groups of an A/B Split campaign. Does not return information about ...

    `abuse_reports: list[int]`
    :   The number of abuse reports generated for this campaign.

    `bounces: list[dict[str, typing.Any]]`
    :   An object describing the bounce summary for the campaign.

    `campaign_title: list[str]`
    :   The title of the campaign.

    `clicks: list[dict[str, typing.Any]]`
    :   An object describing the click activity for the campaign.

    `delivery_status: list[dict[str, typing.Any]]`
    :   Updates on campaigns in the process of sending.

    `ecommerce: list[dict[str, typing.Any]]`
    :   E-Commerce stats for a campaign.

    `emails_sent: list[int]`
    :   The total number of emails sent for this campaign.

    `facebook_likes: list[dict[str, typing.Any]]`
    :   An object describing campaign engagement on Facebook.

    `forwards: list[dict[str, typing.Any]]`
    :   An object describing the forwards and forward activity for the campaign.

    `id: list[str]`
    :   A string that uniquely identifies this campaign.

    `industry_stats: list[dict[str, typing.Any]]`
    :   The average campaign statistics for your industry.

    `list_id: list[str]`
    :   The unique list id.

    `list_is_active: list[bool]`
    :   The status of the list used, namely if it's deleted or disabled.

    `list_name: list[str]`
    :   The name of the list.

    `list_stats: list[dict[str, typing.Any]]`
    :   The average campaign statistics for your list. This won't be present if we haven't calculated i...

    `opens: list[dict[str, typing.Any]]`
    :   An object describing the open activity for the campaign.

    `preview_text: list[str]`
    :   The preview text for the campaign.

    `rss_last_send: list[str]`
    :   For RSS campaigns, the date and time of the last send in ISO 8601 format.

    `send_time: list[str]`
    :   The date and time a campaign was sent in ISO 8601 format.

    `share_report: list[dict[str, typing.Any]]`
    :   The url and password for the VIP report.

    `subject_line: list[str]`
    :   The subject line for the campaign.

    `timeseries: list[list[typing.Any]]`
    :   An hourly breakdown of the performance of the campaign over the first 24 hours.

    `timewarp: list[list[typing.Any]]`
    :   An hourly breakdown of sends, opens, and clicks if a campaign is sent using timewarp.

    `type_: list[str]`
    :   The type of campaign (regular, plain-text, ab_split, rss, automation, variate, or auto).

    `unsubscribed: list[int]`
    :   The total number of unsubscribed members for this campaign.

<a id="ReportsKeywordCondition"></a>

`ReportsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.mailchimp.types.ReportsStringFilter`
    :   The type of the None singleton.

<a id="ReportsLikeCondition"></a>

`ReportsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.mailchimp.types.ReportsStringFilter`
    :   The type of the None singleton.

<a id="ReportsListParams"></a>

`ReportsListParams(*args, **kwargs)`
:   Parameters for reports.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `before_send_time: str`
    :   The type of the None singleton.

    `count: int`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

    `since_send_time: str`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="ReportsLtCondition"></a>

`ReportsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.mailchimp.types.ReportsSearchFilter`
    :   The type of the None singleton.

<a id="ReportsLteCondition"></a>

`ReportsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.mailchimp.types.ReportsSearchFilter`
    :   The type of the None singleton.

<a id="ReportsNeqCondition"></a>

`ReportsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.mailchimp.types.ReportsSearchFilter`
    :   The type of the None singleton.

<a id="ReportsNotCondition"></a>

`ReportsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.mailchimp.types.ReportsEqCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsNeqCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsGtCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsGteCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsLtCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsLteCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsInCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsLikeCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsFuzzyCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsKeywordCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsContainsCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsNotCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsAndCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsOrCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsAnyCondition`
    :   The type of the None singleton.

<a id="ReportsOrCondition"></a>

`ReportsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.mailchimp.types.ReportsEqCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsNeqCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsGtCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsGteCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsLtCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsLteCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsInCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsLikeCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsFuzzyCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsKeywordCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsContainsCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsNotCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsAndCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsOrCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsAnyCondition]`
    :   The type of the None singleton.

<a id="ReportsSearchFilter"></a>

`ReportsSearchFilter(*args, **kwargs)`
:   Available fields for filtering reports search queries.

    ### Ancestors (in MRO)

    * builtins.dict

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

<a id="ReportsSearchQuery"></a>

`ReportsSearchQuery(*args, **kwargs)`
:   Search query for reports entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.mailchimp.types.ReportsEqCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsNeqCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsGtCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsGteCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsLtCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsLteCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsInCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsLikeCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsFuzzyCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsKeywordCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsContainsCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsNotCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsAndCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsOrCondition | airbyte_agent_sdk.connectors.mailchimp.types.ReportsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.mailchimp.types.ReportsSortFilter]`
    :   The type of the None singleton.

<a id="ReportsSortFilter"></a>

`ReportsSortFilter(*args, **kwargs)`
:   Available fields for sorting reports search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ab_split: Literal['asc', 'desc']`
    :   General stats about different groups of an A/B Split campaign. Does not return information about ...

    `abuse_reports: Literal['asc', 'desc']`
    :   The number of abuse reports generated for this campaign.

    `bounces: Literal['asc', 'desc']`
    :   An object describing the bounce summary for the campaign.

    `campaign_title: Literal['asc', 'desc']`
    :   The title of the campaign.

    `clicks: Literal['asc', 'desc']`
    :   An object describing the click activity for the campaign.

    `delivery_status: Literal['asc', 'desc']`
    :   Updates on campaigns in the process of sending.

    `ecommerce: Literal['asc', 'desc']`
    :   E-Commerce stats for a campaign.

    `emails_sent: Literal['asc', 'desc']`
    :   The total number of emails sent for this campaign.

    `facebook_likes: Literal['asc', 'desc']`
    :   An object describing campaign engagement on Facebook.

    `forwards: Literal['asc', 'desc']`
    :   An object describing the forwards and forward activity for the campaign.

    `id: Literal['asc', 'desc']`
    :   A string that uniquely identifies this campaign.

    `industry_stats: Literal['asc', 'desc']`
    :   The average campaign statistics for your industry.

    `list_id: Literal['asc', 'desc']`
    :   The unique list id.

    `list_is_active: Literal['asc', 'desc']`
    :   The status of the list used, namely if it's deleted or disabled.

    `list_name: Literal['asc', 'desc']`
    :   The name of the list.

    `list_stats: Literal['asc', 'desc']`
    :   The average campaign statistics for your list. This won't be present if we haven't calculated i...

    `opens: Literal['asc', 'desc']`
    :   An object describing the open activity for the campaign.

    `preview_text: Literal['asc', 'desc']`
    :   The preview text for the campaign.

    `rss_last_send: Literal['asc', 'desc']`
    :   For RSS campaigns, the date and time of the last send in ISO 8601 format.

    `send_time: Literal['asc', 'desc']`
    :   The date and time a campaign was sent in ISO 8601 format.

    `share_report: Literal['asc', 'desc']`
    :   The url and password for the VIP report.

    `subject_line: Literal['asc', 'desc']`
    :   The subject line for the campaign.

    `timeseries: Literal['asc', 'desc']`
    :   An hourly breakdown of the performance of the campaign over the first 24 hours.

    `timewarp: Literal['asc', 'desc']`
    :   An hourly breakdown of sends, opens, and clicks if a campaign is sent using timewarp.

    `type_: Literal['asc', 'desc']`
    :   The type of campaign (regular, plain-text, ab_split, rss, automation, variate, or auto).

    `unsubscribed: Literal['asc', 'desc']`
    :   The total number of unsubscribed members for this campaign.

<a id="ReportsStringFilter"></a>

`ReportsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `ab_split: str`
    :   General stats about different groups of an A/B Split campaign. Does not return information about ...

    `abuse_reports: str`
    :   The number of abuse reports generated for this campaign.

    `bounces: str`
    :   An object describing the bounce summary for the campaign.

    `campaign_title: str`
    :   The title of the campaign.

    `clicks: str`
    :   An object describing the click activity for the campaign.

    `delivery_status: str`
    :   Updates on campaigns in the process of sending.

    `ecommerce: str`
    :   E-Commerce stats for a campaign.

    `emails_sent: str`
    :   The total number of emails sent for this campaign.

    `facebook_likes: str`
    :   An object describing campaign engagement on Facebook.

    `forwards: str`
    :   An object describing the forwards and forward activity for the campaign.

    `id: str`
    :   A string that uniquely identifies this campaign.

    `industry_stats: str`
    :   The average campaign statistics for your industry.

    `list_id: str`
    :   The unique list id.

    `list_is_active: str`
    :   The status of the list used, namely if it's deleted or disabled.

    `list_name: str`
    :   The name of the list.

    `list_stats: str`
    :   The average campaign statistics for your list. This won't be present if we haven't calculated i...

    `opens: str`
    :   An object describing the open activity for the campaign.

    `preview_text: str`
    :   The preview text for the campaign.

    `rss_last_send: str`
    :   For RSS campaigns, the date and time of the last send in ISO 8601 format.

    `send_time: str`
    :   The date and time a campaign was sent in ISO 8601 format.

    `share_report: str`
    :   The url and password for the VIP report.

    `subject_line: str`
    :   The subject line for the campaign.

    `timeseries: str`
    :   An hourly breakdown of the performance of the campaign over the first 24 hours.

    `timewarp: str`
    :   An hourly breakdown of sends, opens, and clicks if a campaign is sent using timewarp.

    `type_: str`
    :   The type of campaign (regular, plain-text, ab_split, rss, automation, variate, or auto).

    `unsubscribed: str`
    :   The total number of unsubscribed members for this campaign.

<a id="SegmentMembersListParams"></a>

`SegmentMembersListParams(*args, **kwargs)`
:   Parameters for segment_members.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `count: int`
    :   The type of the None singleton.

    `list_id: str`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

    `segment_id: str`
    :   The type of the None singleton.

<a id="SegmentsGetParams"></a>

`SegmentsGetParams(*args, **kwargs)`
:   Parameters for segments.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `list_id: str`
    :   The type of the None singleton.

    `segment_id: str`
    :   The type of the None singleton.

<a id="SegmentsListParams"></a>

`SegmentsListParams(*args, **kwargs)`
:   Parameters for segments.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `before_created_at: str`
    :   The type of the None singleton.

    `before_updated_at: str`
    :   The type of the None singleton.

    `count: int`
    :   The type of the None singleton.

    `list_id: str`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.

    `since_created_at: str`
    :   The type of the None singleton.

    `since_updated_at: str`
    :   The type of the None singleton.

    `type: str`
    :   The type of the None singleton.

<a id="TagsListParams"></a>

`TagsListParams(*args, **kwargs)`
:   Parameters for tags.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `list_id: str`
    :   The type of the None singleton.

    `name: str`
    :   The type of the None singleton.

<a id="UnsubscribesListParams"></a>

`UnsubscribesListParams(*args, **kwargs)`
:   Parameters for unsubscribes.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `campaign_id: str`
    :   The type of the None singleton.

    `count: int`
    :   The type of the None singleton.

    `offset: int`
    :   The type of the None singleton.