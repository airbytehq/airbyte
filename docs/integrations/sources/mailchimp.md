# Mailchimp

This page guides you through setting up the Mailchimp source connector.

## Prerequisite

You can use [OAuth](https://mailchimp.com/developer/marketing/guides/access-user-data-oauth-2/) or an API key to authenticate your Mailchimp account. If you choose to authenticate with OAuth, [register](https://mailchimp.com/developer/marketing/guides/access-user-data-oauth-2/#register-your-application) your Mailchimp account.

## Set up the Mailchimp source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**. 
3. On the Set up the source page, select **Mailchimp** from the Source type dropdown.
4. Enter a name for your source.

6. You can use OAuth or an API key to authenticate your Mailchimp account. We recommend using OAuth for Airbyte Cloud and an API key for Airbyte Open Source.
    - To authenticate using OAuth for Airbyte Cloud, ensure you have [registered your Mailchimp account](#prerequisite) and then click **Authenticate your Mailchimp account** to sign in with Mailchimp and authorize your account. 
    - To authenticate using an API key for Airbyte Open Source, select **API key** from the Authentication dropdown and enter the [API key](https://mailchimp.com/developer/marketing/guides/quick-start/#generate-your-api-key) for your Mailchimp account.    
    :::note
    Check the [performance considerations](#performance-considerations) before using an API key.
    :::
7. Click **Set up source**.

## Supported sync modes

The Mailchimp source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-mode):

 - Full Refresh
 - Incremental

Airbyte doesn't support Incremental Deletes for the `Campaigns`, `Lists`, and `Email Activity` streams because Mailchimp doesn't provide any information about deleted data in these streams.

## Performance considerations

[Mailchimp does not impose rate limits](https://mailchimp.com/developer/guides/marketing-api-conventions/#throttling) on how much data is read from its API in a single sync process. However, Mailchimp enforces a maximum of 10 simultaneous connections to its API, which means that Airbyte is unable to run more than 10 concurrent syncs from Mailchimp using API keys generated from the same account.

## Supported streams

The Mailchimp source connector supports the following streams:

**[Lists](https://mailchimp.com/developer/api/marketing/lists/get-list-info) Stream**

```
{
  "id": "q1w2e3r4t5",
  "web_id": 000001,
  "name": "Newsletter Subscribers",
  "contact": {
    "company": "",
    "address1": "",
    "address2": "",
    "city": "San Francisco",
    "state": "CA",
    "zip": "00000-1111",
    "country": "US",
    "phone": ""
  },
  "permission_reminder": "You are receiving this email because you opted in via our website.",
  "use_archive_bar": true,
  "campaign_defaults": {
    "from_name": "Airbyte Community",
    "from_email": "hey@email.com",
    "subject": "",
    "language": "en"
  },
  "notify_on_subscribe": "",
  "notify_on_unsubscribe": "",
  "date_created": "2020-09-17T04:48:49+00:00",
  "list_rating": 3,
  "email_type_option": false,
  "subscribe_url_short": "http://eepurl.com/hfpWAr",
  "subscribe_url_long": "https://daxtarity.us2.list-manage.com/subscribe?u=q1q1q1q1q1q1q1q1q1q&id=q1w2e3r4t5",
  "beamer_address": "us2-00000000-qqqqqqqqq@inbound.mailchimp.com",
  "visibility": "prv",
  "double_optin": false,
  "has_welcome": false,
  "marketing_permissions": false,
  "modules": [],
  "stats": {
    "member_count": 4204,
    "unsubscribe_count": 194,
    "cleaned_count": 154,
    "member_count_since_send": 91,
    "unsubscribe_count_since_send": 19,
    "cleaned_count_since_send": 23,
    "campaign_count": 27,
    "campaign_last_sent": "2022-04-01T14:29:31+00:00",
    "merge_field_count": 5,
    "avg_sub_rate": 219,
    "avg_unsub_rate": 10,
    "target_sub_rate": 18,
    "open_rate": 39.478173607626694,
    "click_rate": 8.504017780817234,
    "last_sub_date": "2022-04-12T07:39:29+00:00",
    "last_unsub_date": "2022-04-11T08:08:07+00:00"
  },
  "_links": [
    {
      "rel": "self",
      "href": "https://us2.api.mailchimp.com/3.0/lists/q1w2e3r4t5",
      "method": "GET",
      "targetSchema": "https://us2.api.mailchimp.com/schema/3.0/Definitions/Lists/Response.json"
    }
  ]
}
```

**[Campaigns](https://mailchimp.com/developer/api/marketing/campaigns/get-campaign-info/) Stream**

```
{
    "id": "q1w2e3r4t5", 
    "web_id": 0000000, 
    "type": "regular", 
    "create_time": "2020-11-03T22:46:43+00:00", 
    "archive_url": "http://eepurl.com/hhSLxH", 
    "long_archive_url": "https://mailchi.mp/xxxxxxxx/weekly-bytes-learnings-from-soft-launch-and-our-vision-0000000", 
    "status": "sent", 
    "emails_sent": 89, 
    "send_time": "2020-11-05T16:15:00+00:00", 
    "content_type": "template", 
    "needs_block_refresh": false, 
    "resendable": true, 
    "recipients": {
        "list_id": "1q2w3e4r", 
        "list_is_active": true, 
        "list_name": "Newsletter Subscribers", 
        "segment_text": "",     
        "recipient_count": 89
    }, 
    "settings": {
        "subject_line": "Some subject", 
        "preview_text": "Text", 
        "title": "Newsletter", 
        "from_name": "Weekly Bytes from Airbyte", 
        "reply_to": "hey@email.com", 
        "use_conversation": false, 
        "to_name": "", 
        "folder_id": "", 
        "authenticate": true, 
        "auto_footer": false, 
        "inline_css": false, 
        "auto_tweet": false, 
        "fb_comments": true, 
        "timewarp": false, 
        "template_id": 0000000, 
        "drag_and_drop": false
    }, 
    "tracking": {
        "opens": true, 
        "html_clicks": true, 
        "text_clicks": false, 
        "goal_tracking": false, 
        "ecomm360": false, 
        "google_analytics": "", 
        "clicktale": ""
    }, 
    "report_summary": {
        "opens": 46, 
        "unique_opens": 33, 
        "open_rate": 0.0128372, 
        "clicks": 13, 
        "subscriber_clicks": 7, 
        "click_rate": 0.0383638, 
        "ecommerce": {
            "total_orders": 0, 
            "total_spent": 0, 
            "total_revenue": 0
        }
    }, 
    "delivery_status": {
        "enabled": false
    }, 
    "_links": [
        {
            "rel": "parent", 
            "href": "https://us2.api.mailchimp.com/3.0/campaigns", 
            "method": "GET", 
            "targetSchema": "https://us2.api.mailchimp.com/schema/3.0/Definitions/Campaigns/CollectionResponse.json", 
            "schema": "https://us2.api.mailchimp.com/schema/3.0/Paths/Campaigns/Collection.json"
        }
    ]
}
```

**[Email Activity](https://mailchimp.com/developer/marketing/api/email-activity-reports/) Stream**

```
{
  "campaign_id": "q1w2q1w2q1w2",
  "list_id": "123qwe",
  "list_is_active": true,
  "email_id": "qwerty123456",
  "email_address": "email@email.com",
  "_links": [
    {
      "rel": "parent",
      "href": "https://us2.api.mailchimp.com/3.0/reports/q1w2q1w2q1w2/email-activity",
      "method": "GET",
      "targetSchema": "https://us2.api.mailchimp.com/schema/3.0/Definitions/Reports/EmailActivity/CollectionResponse.json"
    }
  ],
  "action": "open",
  "timestamp": "2020-10-08T22:15:43+00:00",
  "ip": "00.000.00.5"
}
```

### A note on the primary keys 

The `Lists` and `Campaigns` streams have `id` as the primary key. The `Email Activity` stream doesn't have a primary key because Mailchimp does not provide one. 

## Data type mapping

| Integration Type           | Airbyte Type | Notes                                                                               |
|:---------------------------|:-------------|:------------------------------------------------------------------------------------|
| `array`                    | `array`      | the type of elements in the array is determined based on the mappings in this table |
| `date`, `time`, `datetime` | `string`     |                                                                                     |
| `int`, `float`, `number`   | `number`     |                                                                                     |
| `object`                   | `object`     | properties within objects are mapped based on the mappings in this table            |
| `string`                   | `string`     |                                                                                     |

## Tutorials

Now that you have set up the Mailchimp source connector, check out the following Mailchimp tutorial:

- [Build a data ingestion pipeline from Mailchimp to Snowflake](https://airbyte.com/tutorials/data-ingestion-pipeline-mailchimp-snowflake)

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                    |
|---------|------------|----------------------------------------------------------|----------------------------------------------------------------------------|
| 0.4.0   | 2023-04-11 | [23290](https://github.com/airbytehq/airbyte/pull/23290) | Add Automations stream                                                         |
| 0.3.5   | 2023-02-28 | [23464](https://github.com/airbytehq/airbyte/pull/23464) | Add Reports stream                                                         |
| 0.3.4   | 2023-02-06 | [22405](https://github.com/airbytehq/airbyte/pull/22405) | Revert extra logging                                                       |
| 0.3.3   | 2023-02-01 | [22228](https://github.com/airbytehq/airbyte/pull/22228) | Add extra logging                                                          |
| 0.3.2   | 2023-01-27 | [22014](https://github.com/airbytehq/airbyte/pull/22014) | Set `AvailabilityStrategy` for streams explicitly to `None`                |
| 0.3.1   | 2022-12-20 | [20720](https://github.com/airbytehq/airbyte/pull/20720) | Use stream slices as a source for request params instead of a stream state |
| 0.3.0   | 2022-11-07 | [19023](https://github.com/airbytehq/airbyte/pull/19023) | Set primary key for Email Activity stream.                                 |
| 0.2.15  | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states.                                              |
| 0.2.14  | 2022-04-12 | [11352](https://github.com/airbytehq/airbyte/pull/11352) | Update documentation                                                       |
| 0.2.13  | 2022-04-11 | [11632](https://github.com/airbytehq/airbyte/pull/11632) | Add unit tests                                                             |
| 0.2.12  | 2022-03-17 | [10975](https://github.com/airbytehq/airbyte/pull/10975) | Fix campaign's stream normalization                                        |
| 0.2.11  | 2021-12-24 | [7159](https://github.com/airbytehq/airbyte/pull/7159)   | Add oauth2.0 support                                                       |
| 0.2.10  | 2021-12-21 | [9000](https://github.com/airbytehq/airbyte/pull/9000)   | Update connector fields title/description                                  |
| 0.2.9   | 2021-12-13 | [7975](https://github.com/airbytehq/airbyte/pull/7975)   | Updated JSON schemas                                                       |
| 0.2.8   | 2021-08-17 | [5481](https://github.com/airbytehq/airbyte/pull/5481)   | Remove date-time type from some fields                                     |
| 0.2.7   | 2021-08-03 | [5137](https://github.com/airbytehq/airbyte/pull/5137)   | Source Mailchimp: fix primary key for email activities                     |
| 0.2.6   | 2021-07-28 | [5024](https://github.com/airbytehq/airbyte/pull/5024)   | Source Mailchimp: handle records with no no "activity" field in response   |
| 0.2.5   | 2021-07-08 | [4621](https://github.com/airbytehq/airbyte/pull/4621)   | Mailchimp fix url-base                                                     |
| 0.2.4   | 2021-06-09 | [4285](https://github.com/airbytehq/airbyte/pull/4285)   | Use datacenter URL parameter from apikey                                   |
| 0.2.3   | 2021-06-08 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Add AIRBYTE\_ENTRYPOINT for Kubernetes support                             |
| 0.2.2   | 2021-06-08 | [3415](https://github.com/airbytehq/airbyte/pull/3415)   | Get Members activities                                                     |
| 0.2.1   | 2021-04-03 | [2726](https://github.com/airbytehq/airbyte/pull/2726)   | Fix base connector versioning                                              |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238)   | Protocol allows future/unknown properties                                  |
| 0.1.4   | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046)   | Add connectors using an index YAML file                                    |
