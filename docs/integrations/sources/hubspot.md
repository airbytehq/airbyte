# HubSpot

## Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |

## Troubleshooting

Check out common troubleshooting issues for the HubSpot connector on our Discourse [here](https://discuss.airbyte.io/tags/c/connector/11/source-hubspot).

## Supported Streams

This source is capable of syncing the following tables and their data:

* [Campaigns](https://developers.hubspot.com/docs/methods/email/get_campaign_data)
* [Companies](https://developers.hubspot.com/docs/api/crm/companies) \(Incremental\)
* [Contact Lists](http://developers.hubspot.com/docs/methods/lists/get_lists) \(Incremental\)
* [Contacts](https://developers.hubspot.com/docs/methods/contacts/get_contacts) \(Incremental\)
* [Contacts list memberships](https://legacydocs.hubspot.com/docs/methods/contacts/get_contacts)
* [Deal Pipelines](https://developers.hubspot.com/docs/methods/pipelines/get_pipelines_for_object_type)
* [Deals](https://developers.hubspot.com/docs/api/crm/deals) \(including Contact associations\) \(Incremental\)
* [Email Events](https://developers.hubspot.com/docs/methods/email/get_events) \(Incremental\)
* [Engagements](https://legacydocs.hubspot.com/docs/methods/engagements/get-all-engagements)
* [Forms](https://developers.hubspot.com/docs/api/marketing/forms)
* [Line Items](https://developers.hubspot.com/docs/api/crm/line-items) \(Incremental\)
* [Marketing Emails](https://legacydocs.hubspot.com/docs/methods/cms_email/get-all-marketing-email-statistics)
* [Owners](https://developers.hubspot.com/docs/methods/owners/get_owners)
* [Products](https://developers.hubspot.com/docs/api/crm/products) \(Incremental\)
* [Quotes](https://developers.hubspot.com/docs/api/crm/quotes) \(Incremental\)
* [Subscription Changes](https://developers.hubspot.com/docs/methods/email/get_subscriptions_timeline) \(Incremental\)
* [Tickets](https://developers.hubspot.com/docs/api/crm/tickets) \(Incremental\)
* [Workflows](https://legacydocs.hubspot.com/docs/methods/workflows/v3/get_workflows)

### A note on the `engagements` stream
Objects in the `engagements` stream can have one of the following types: `note`, `email`, `task`, `meeting`, `call`.

Depending on the type of engagement, different properties will be set for that object in the `engagements_metadata` table in the destination.

* A `call` engagement will have a corresponding `engagements_metadata` object with non-null values in the `toNumber`, `fromNumber`, `status`, `externalId`, `durationMilliseconds`, `externalAccountId`, `recordingUrl`, `body`, and `disposition` columns.
* An `email` engagement will have a corresponding `engagements_metadata` object with with non-null values in the `subject`, `html`, and `text` columns. In addition, there will be records in four related tables, `engagements_metadata_from`, `engagements_metadata_to`, `engagements_metadata_cc`, `engagements_metadata_bcc`.
* A `meeting` engagement will have a corresponding `engagements_metadata` object with non-null values in the `body`, `startTime`, `endTime`, and `title` columns.
* A `note` engagement will have a corresponding `engagements_metadata` object with non-null values in the `body` column.
* A `task` engagement will have a corresponding `engagements_metadata` object with non-null values in the `body`, `status`, and `forObjectType` columns.


**Note**: HubSpot API currently only supports `quotes` endpoint using API Key, using Oauth it is impossible to access this stream (as reported by [community.hubspot.com](https://community.hubspot.com/t5/APIs-Integrations/Help-with-using-Feedback-CRM-API-and-Quotes-CRM-API/m-p/449104/highlight/true#M44411)).

## Getting Started \(Airbyte Open-Source / Airbyte Cloud\)

#### Requirements

* HubSpot Account
* Api credentials
* If using Oauth, [scopes](https://legacydocs.hubspot.com/docs/methods/oauth2/initiate-oauth-integration#scopes) enabled for the streams you want to sync

{% hint style="info" %}
HubSpot's API will [rate limit](https://developers.hubspot.com/docs/api/usage-details) the amount of records you can sync daily, so make sure that you are on the appropriate plan if you are planning on syncing more than 250,000 records per day.
{% endhint %}

This connector supports only authentication with API Key. To obtain API key for the account go to settings -&gt; integrations \(under the account banner\) -&gt; api key. If you already have an api key you can use that. Otherwise generated a new one. See [docs](https://knowledge.hubspot.com/integrations/how-do-i-get-my-hubspot-api-key) for more details.

## Rate Limiting & Performance

The connector is restricted by normal HubSpot [rate limitations](https://legacydocs.hubspot.com/apps/api_guidelines).

When connector reads the stream using `API Key` that doesn't have neccessary permissions to read particular stream, like `workflows`, which requires to be enabled in order to be processed, the log message returned to the output and sync operation goes on with other streams available.

Example of the output message when trying to read `workflows` stream with missing permissions for the `API Key`:

```text
{
    "type": "LOG",
    "log": {
        "level": "WARN",
        "message": 'Stream `workflows` cannot be procced. This hapikey (EXAMPLE_API_KEY) does not have proper permissions! (requires any of [automation-access])'
    }
}
```

### Required scopes

If you are using Oauth, most of the streams require the appropriate [scopes](https://legacydocs.hubspot.com/docs/methods/oauth2/initiate-oauth-integration#scopes) enabled for the API account.

| Stream | Required Scope |
| :--- | :--- |
| `campaigns` | `content` |
| `companies` | `contacts` |
| `contact_lists` | `contacts` |
| `contacts` | `contacts` |
| `contacts_list_memberships` | `contacts` |
| `deal_pipelines` | either the `contacts` scope \(to fetch deals pipelines\) or the `tickets` scope. |
| `deals` | `contacts` |
| `email_events` | `content` |
| `engagements` | `contacts` |
| `forms` | `forms` |
| `form_submissions`| `forms` |
| `line_items` | `e-commerce` |
| `owners` | `contacts` |
| `products` | `e-commerce` |
| `property_history` | `contacts` |
| `quotes` | no scope required |
| `subscription_changes` | `content` |
| `tickets` | `tickets` |
| `workflows` | `automation` |

## Changelog

| Version | Date       | Pull Request | Subject                                                                                                                                        |
|:--------|:-----------| :--- |:-----------------------------------------------------------------------------------------------------------------------------------------------|
| 0.1.38  | 2022-02-03 | [9786](https://github.com/airbytehq/airbyte/pull/9786) | Add new streams for engagements(calls, emails, meetings, notes and tasks) |
| 0.1.37  | 2022-01-27 | [9555](https://github.com/airbytehq/airbyte/pull/9555) | Getting form_submission for all forms |
| 0.1.36  | 2022-01-22 | [7784](https://github.com/airbytehq/airbyte/pull/7784) | Add Property History Stream |
| 0.1.35  | 2021-12-24 | [9081](https://github.com/airbytehq/airbyte/pull/9081) | Add Feedback Submissions stream and update Ticket Pipelines stream |
| 0.1.34  | 2022-01-20 | [9641](https://github.com/airbytehq/airbyte/pull/9641) | Add more fields for `email_events` stream |
| 0.1.33  | 2022-01-14 | [8887](https://github.com/airbytehq/airbyte/pull/8887) | More efficient support for incremental updates on Companies, Contact, Deals and Engagement streams |
| 0.1.32  | 2022-01-13 | [8011](https://github.com/airbytehq/airbyte/pull/8011) | Add new stream form_submissions                                                                                   |
| 0.1.31  | 2022-01-11 | [9385](https://github.com/airbytehq/airbyte/pull/9385) | Remove auto-generated `properties` from `Engagements` stream                                                                                   |
| 0.1.30  | 2021-01-10 | [9129](https://github.com/airbytehq/airbyte/pull/9129) | Created Contacts list memberships streams                                                                                                      |
| 0.1.29  | 2021-12-17 | [8699](https://github.com/airbytehq/airbyte/pull/8699) | Add incremental sync support for `companies`, `contact_lists`, `contacts`, `deals`, `line_items`, `products`, `quotes`, `tickets` streams      |
| 0.1.28  | 2021-12-15 | [8429](https://github.com/airbytehq/airbyte/pull/8429) | Update fields and descriptions                                                                                                                 |
| 0.1.27  | 2021-12-09 | [8658](https://github.com/airbytehq/airbyte/pull/8658) | Fixed config backward compatibility issue by allowing additional properties in the spec                                                        |
| 0.1.26  | 2021-11-30 | [8329](https://github.com/airbytehq/airbyte/pull/8329) | Removed 'skip_dynamic_fields' config param                                                                                                     |
| 0.1.25  | 2021-11-23 | [8216](https://github.com/airbytehq/airbyte/pull/8216) | Add skip dynamic fields for testing only                                                                                                       |
| 0.1.24  | 2021-11-09 | [7683](https://github.com/airbytehq/airbyte/pull/7683) | Fix name issue 'Hubspot' -> 'HubSpot'                                                                                                          |
| 0.1.23  | 2021-11-08 | [7730](https://github.com/airbytehq/airbyte/pull/7730) | Fix oAuth flow schema                                                                                                                          |
| 0.1.22  | 2021-11-03 | [7562](https://github.com/airbytehq/airbyte/pull/7562) | Migrate Hubspot source to CDK structure                                                                                                        |
| 0.1.21  | 2021-10-27 | [7405](https://github.com/airbytehq/airbyte/pull/7405) | Change of package `import` from `urllib` to `urllib.parse`                                                                                     |
| 0.1.20  | 2021-10-26 | [7393](https://github.com/airbytehq/airbyte/pull/7393) | Hotfix for `split_properties` function, add the length of separator symbol `,`(`%2C` in HTTP format) to the checking of the summary URL length |
| 0.1.19  | 2021-10-26 | [6954](https://github.com/airbytehq/airbyte/pull/6954) | Fix issue with getting `414` HTTP error for streams                                                                                            |
| 0.1.18  | 2021-10-18 | [5840](https://github.com/airbytehq/airbyte/pull/5840) | Add new marketing emails (with statistics) stream                                                                                              |
| 0.1.17  | 2021-10-14 | [6995](https://github.com/airbytehq/airbyte/pull/6995) | Update `discover` method: disable `quotes` stream when using OAuth config                                                                      |
| 0.1.16  | 2021-09-27 | [6465](https://github.com/airbytehq/airbyte/pull/6465) | Implement OAuth support. Use CDK authenticator instead of connector specific authenticator                                                     |
| 0.1.15  | 2021-09-23 | [6374](https://github.com/airbytehq/airbyte/pull/6374) | Use correct schema for `owners` stream                                                                                                         |
| 0.1.14  | 2021-09-08 | [5693](https://github.com/airbytehq/airbyte/pull/5693) | Include deal\_to\_contact association when pulling deal stream and include contact ID in contact stream                                        |
| 0.1.13  | 2021-09-08 | [5834](https://github.com/airbytehq/airbyte/pull/5834) | Fixed array fields without items property in schema                                                                                            |
| 0.1.12  | 2021-09-02 | [5798](https://github.com/airbytehq/airbyte/pull/5798) | Treat empty string values as None for field with format to fix normalization errors                                                            |
| 0.1.11  | 2021-08-26 | [5685](https://github.com/airbytehq/airbyte/pull/5685) | Remove all date-time format from schemas                                                                                                       |
| 0.1.10  | 2021-08-17 | [5463](https://github.com/airbytehq/airbyte/pull/5463) | Fix fail on reading stream using `API Key` without required permissions                                                                        |
| 0.1.9   | 2021-08-11 | [5334](https://github.com/airbytehq/airbyte/pull/5334) | Fix empty strings inside float datatype                                                                                                        |
| 0.1.8   | 2021-08-06 | [5250](https://github.com/airbytehq/airbyte/pull/5250) | Fix issue with printing exceptions                                                                                                             |
| 0.1.7   | 2021-07-27 | [4913](https://github.com/airbytehq/airbyte/pull/4913) | Update fields schema                                                                                                                           |
