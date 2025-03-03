# HubSpot

<HideInUI>

This page contains the setup guide and reference information for the [HubSpot](https://www.hubspot.com/) source connector.

</HideInUI>

## Prerequisites

- HubSpot Account

<!-- env:oss -->

- **For Airbyte Open Source**: Private App with Access Token
<!-- /env:oss -->

## Setup guide

### Step 1: Set up HubSpot

<!-- env:cloud -->

**For Airbyte Cloud:**

**- OAuth** (Recommended). We highly recommend you use OAuth rather than Private App authentication, as it significantly simplifies the setup process.

**- Private App:** If you are using a Private App, you will need to use your Access Token to set up the connector. Please refer to the [official HubSpot documentation](https://developers.hubspot.com/docs/api/private-apps) to learn how to obtain the access token.

<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

**- Private App setup** (Recommended): If you are authenticating via a Private App, you will need to use your Access Token to set up the connector. Please refer to the [official HubSpot documentation](https://developers.hubspot.com/docs/api/private-apps) to learn how to obtain the access token.

**- OAuth setup:** If you are using Oauth to authenticate on Airbyte Open Source, please refer to [Hubspot's detailed walkthrough](https://developers.hubspot.com/docs/api/working-with-oauth). To set up the connector, you will need to acquire your:

- Client ID
- Client Secret
- Refresh Token
<!-- /env:oss -->

More information on HubSpot authentication methods can be found
[here](https://developers.hubspot.com/docs/api/intro-to-auth).

### Step 2: Configure the scopes for your streams (Private App only)

These instructions are only relevant if you are using a **Private App** for authentication. You can ignore this if you are authenticating via OAuth.

To set up a Private App, you must manually configure scopes to ensure Airbyte can sync all available data. Each scope relates to a specific stream or streams. Please refer to [Hubspot's page on scopes](https://legacydocs.hubspot.com/docs/methods/oauth2/initiate-oauth-integration#scopes) for instructions.

<details>
  <summary>Expand to review scopes</summary>


| Stream                      | Required Scope                                                                                               |
| :-------------------------- | :----------------------------------------------------------------------------------------------------------- |
| `campaigns`                 | `content`                                                                                                    |
| `companies`                 | `crm.objects.companies.read`, `crm.schemas.companies.read`                                                   |
| `contact_lists`             | `crm.lists.read`                                                                                             |
| `contacts`                  | `crm.objects.contacts.read`                                                                                  |
| `contacts_list_memberships` | `crm.objects.contacts.read`                                                                                  |
| `contacts_form_submissions` | `crm.objects.contacts.read`                                                                                  |
| `contacts_web_analytics`    | `crm.objects.contacts.read`, `business-intelligence`                                                         |
| Custom CRM Objects          | `crm.objects.custom.read`                                                                                    |
| `deal_pipelines`            | `crm.objects.contacts.read`                                                                                  |
| `deals`                     | `crm.objects.deals.read`, `crm.schemas.deals.read`                                                           |
| `deals_archived`            | `crm.objects.deals.read`, `crm.schemas.deals.read`                                                           |
| `email_events`              | `content`                                                                                                    |
| `email_subscriptions`       | `content`                                                                                                    |
| `engagements`               | `crm.objects.companies.read`, `crm.objects.contacts.read`, `crm.objects.deals.read`, `tickets`, `e-commerce` |
| `engagements_emails`        | `sales-email-read`                                                                                           |
| `forms`                     | `forms`                                                                                                      |
| `form_submissions`          | `forms`                                                                                                      |
| `goals`                     | `crm.objects.goals.read`                                                                                     |
| `leads`                     | `crm.objects.leads.read`, `crm.schemas.leads.read`                                                   |
| `line_items`                | `e-commerce`                                                                                                 |
| `owners`                    | `crm.objects.owners.read`                                                                                    |
| `products`                  | `e-commerce`                                                                                                 |
| `property_history`          | `crm.objects.contacts.read`                                                                                  |
| `subscription_changes`      | `content`                                                                                                    |
| `tickets`                   | `tickets`                                                                                                    |
| `workflows`                 | `automation`                                                                                                 |

</details>

### Step 3: Set up the HubSpot connector in Airbyte

<!-- env:cloud -->

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select HubSpot from the Source type dropdown.
4. Enter a name for the HubSpot connector.
5. From the **Authentication** dropdown, select your chosen authentication method:
   - (Recommended) To authenticate using OAuth, select **OAuth** and click **Authenticate your HubSpot account** to sign in with HubSpot and authorize your account.

     :::note HubSpot Authentication issues
     You may encounter an error during the authentication process in the popup window with the message `An invalid scope name was provided`. To resolve this, close the window and retry authentication.
     :::
   - (Not Recommended) To authenticate using a Private App, select **Private App** and enter the Access Token for your HubSpot account.

<FieldAnchor field="start_date">

6. For **Start date**, use the provided datepicker or enter the date in the following format: `yyyy-mm-ddThh:mm:ssZ`. Data added on and after this date will be replicated. If this is not set, "2006-06-01T00:00:00Z" (the date Hubspot was created) will be used as a start date.

</FieldAnchor>

7. Click **Set up source** and wait for the tests to complete.
<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. From the Airbyte UI, click **Sources**, then click on **+ New Source** and select **HubSpot** from the list of available sources.
3. Enter a **Source name** of your choosing.
4. From the **Authentication** dropdown, select your chosen authentication method:
   - (Recommended) To authenticate using a Private App, select **Private App** and enter the Access Token for your HubSpot account.
   - (Not Recommended:) To authenticate using OAuth, select **OAuth** and enter your Client ID, Client Secret, and Refresh Token.
5. For **Start date**, use the provided datepicker or enter the date in the following format:
   `yyyy-mm-ddThh:mm:ssZ`. The data added on and after this date will be replicated. If not set, "2006-06-01T00:00:00Z" (Hubspot creation date) will be used as start date. It's recommended to provide relevant to your data start date value to optimize synchronization.
6. Click **Set up source** and wait for the tests to complete.

<FieldAnchor field="enable_experimental_streams">

### Experimental streams

[Web Analytics](https://developers.hubspot.com/docs/api/events/web-analytics) streams may be enabled as an experimental feature. Note that these streams use a Hubspot API that is currently in beta, and they may be modified or unstable as the API continues to develop.

</FieldAnchor>

<HideInUI>

## Supported sync modes

The HubSpot source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- Full Refresh
- Incremental

:::note
There are two types of incremental sync:

1. Incremental (standard server-side, where API returns only the data updated or generated since the last sync)
2. Client-Side Incremental (API returns all available data and connector filters out only new records)
   :::

## Supported Streams

The HubSpot source connector supports the following streams:

- [Campaigns](https://developers.hubspot.com/docs/methods/email/get_campaign_data) \(Client-Side Incremental\)
- [Companies](https://developers.hubspot.com/docs/api/crm/companies) \(Incremental\)
- [Contact Lists](http://developers.hubspot.com/docs/methods/lists/get_lists) \(Incremental\)
- [Contacts](https://developers.hubspot.com/docs/methods/contacts/get_contacts) \(Incremental\)
- [Contacts List Memberships](https://legacydocs.hubspot.com/docs/methods/contacts/get_contacts)
- [Contacts Form Submissions](https://legacydocs.hubspot.com/docs/methods/contacts/get_contacts)
- [Contacts Merged Audit](https://legacydocs.hubspot.com/docs/methods/contacts/get_batch_by_vid)
- [Deal Pipelines](https://developers.hubspot.com/docs/methods/pipelines/get_pipelines_for_object_type) \(Client-Side Incremental\)
- [Deals](https://developers.hubspot.com/docs/api/crm/deals) \(including Contact associations\) \(Incremental\)
  - Records that have been deleted (archived) and stored in HubSpot's recycle bin will only be kept for 90 days, see [response from HubSpot Team](https://community.hubspot.com/t5/APIs-Integrations/Archived-deals-deleted-or-different/m-p/714157)
- [Deals Archived](https://developers.hubspot.com/docs/api/crm/deals) \(including Contact associations\) \(Incremental\)
- [Email Events](https://developers.hubspot.com/docs/methods/email/get_events) \(Incremental\)
- [Email Subscriptions](https://developers.hubspot.com/docs/methods/email/get_subscriptions)
- [Engagements](https://legacydocs.hubspot.com/docs/methods/engagements/get-all-engagements) \(Incremental\)
- [Engagements Calls](https://developers.hubspot.com/docs/api/crm/calls) \(Incremental\)
- [Engagements Emails](https://developers.hubspot.com/docs/api/crm/email) \(Incremental\)
- [Engagements Meetings](https://developers.hubspot.com/docs/api/crm/meetings) \(Incremental\)
- [Engagements Notes](https://developers.hubspot.com/docs/api/crm/notes) \(Incremental\)
- [Engagements Tasks](https://developers.hubspot.com/docs/api/crm/tasks) \(Incremental\)
- [Forms](https://developers.hubspot.com/docs/api/marketing/forms) \(Client-Side Incremental\)
- [Form Submissions](https://legacydocs.hubspot.com/docs/methods/forms/get-submissions-for-a-form) \(Client-Side Incremental\)
- [Goals](https://developers.hubspot.com/docs/api/crm/goals) \(Incremental\)
- [Leads](https://developers.hubspot.com/docs/api/crm/leads) \(Incremental\)
- [Line Items](https://developers.hubspot.com/docs/api/crm/line-items) \(Incremental\)
- [Marketing Emails](https://legacydocs.hubspot.com/docs/methods/cms_email/get-all-marketing-email-statistics)
- [Owners](https://developers.hubspot.com/docs/methods/owners/get_owners) \(Client-Side Incremental\)
- [Owners Archived](https://legacydocs.hubspot.com/docs/methods/owners/get_owners) \(Client-Side Incremental)
- [Products](https://developers.hubspot.com/docs/api/crm/products) \(Incremental\)
- [Contacts Property History](https://legacydocs.hubspot.com/docs/methods/contacts/get_contacts) \(Client-Side Incremental\)
- [Companies Property History](https://legacydocs.hubspot.com/docs/methods/companies/get-all-companies) \(Client-Side Incremental\)
- [Deals Property History](https://legacydocs.hubspot.com/docs/methods/deals/get-all-deals) \(Client-Side Incremental\)
- [Subscription Changes](https://developers.hubspot.com/docs/methods/email/get_subscriptions_timeline) \(Incremental\)
- [Tickets](https://developers.hubspot.com/docs/api/crm/tickets) \(Incremental\)
- [Ticket Pipelines](https://developers.hubspot.com/docs/api/crm/pipelines) \(Client-Side Incremental\)
- [Workflows](https://legacydocs.hubspot.com/docs/methods/workflows/v3/get_workflows) \(Client-Side Incremental\)
- [ContactsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) \(Incremental\)
- [CompaniesWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) \(Incremental\)
- [DealsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) \(Incremental\)
- [TicketsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) \(Incremental\)
- [EngagementsCallsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) \(Incremental\)
- [EngagementsEmailsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) \(Incremental\)
- [EngagementsMeetingsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) \(Incremental\)
- [EngagementsNotesWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) \(Incremental\)
- [EngagementsTasksWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) \(Incremental\)
- [GoalsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) \(Incremental\)
- [LineItemsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) \(Incremental\)
- [ProductsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) \(Incremental\)

### Entity-Relationship Diagram (ERD)
<EntityRelationshipDiagram></EntityRelationshipDiagram>

### Notes on the `property_history` streams

`Property_history` streams can be synced using an `Incremental` sync mode, which uses a cursor timestamp to determine which records have been updated since the previous sync. Within these streams, some fields types (ex. `CALCULATED` type) will always have a cursor timstamp that mirrors the time of the latest sync. This results in each sync including many more records than were necessarily changed since the previous sync.

### Notes on the `engagements` stream

1. Objects in the `engagements` stream can have one of the following types: `note`, `email`, `task`, `meeting`, `call`. Depending on the type of engagement, different properties are set for that object in the `engagements_metadata` table in the destination:

- A `call` engagement has a corresponding `engagements_metadata` object with non-null values in the `toNumber`, `fromNumber`, `status`, `externalId`, `durationMilliseconds`, `externalAccountId`, `recordingUrl`, `body`, and `disposition` columns.
- An `email` engagement has a corresponding `engagements_metadata` object with non-null values in the `subject`, `html`, and `text` columns. In addition, there will be records in four related tables, `engagements_metadata_from`, `engagements_metadata_to`, `engagements_metadata_cc`, `engagements_metadata_bcc`.
- A `meeting` engagement has a corresponding `engagements_metadata` object with non-null values in the `body`, `startTime`, `endTime`, and `title` columns.
- A `note` engagement has a corresponding `engagements_metadata` object with non-null values in the `body` column.
- A `task` engagement has a corresponding `engagements_metadata` object with non-null values in the `body`, `status`, and `forObjectType` columns.

2. The `engagements` stream uses two different APIs based on the length of time since the last sync and the number of records which Airbyte hasn't yet synced.

- **EngagementsRecent** if the following two criteria are met:
  - The last sync was performed within the last 30 days
  - Fewer than 10,000 records are being synced
- **EngagementsAll** if either of these criteria are not met.

Because of this, the `engagements` stream can be slow to sync if it hasn't synced within the last 30 days and/or is generating large volumes of new data. To accomodate for this limitation, we recommend scheduling more frequent syncs.

### Notes on the `Forms` and `Form Submissions` stream

This stream only syncs marketing forms. If you need other forms types, sync `Contacts Form Submissions`.

### Notes on the `Custom CRM` Objects

Custom CRM Objects and Custom Web Analytics will appear as streams available for sync, alongside the standard objects listed above.

If you set up your connections before April 15th, 2023 (on Airbyte Cloud) or before 0.8.0 (OSS) then you'll need to do some additional work to sync custom CRM objects.

First you need to give the connector some additional permissions:

- **If you are using OAuth on Airbyte Cloud** go to the Hubspot source settings page in the Airbyte UI and re-authenticate via OAuth to allow Airbyte the permissions to access custom objects.

- **If you are using OAuth on OSS or Private App auth** go into the Hubspot UI where you created your Private App or OAuth application and add the `crm.objects.custom.read` scope to your app's scopes. See HubSpot's instructions [here](https://developers.hubspot.com/docs/api/working-with-oauth#scopes).

Then, go to the schema tab of your connection and click **refresh source schema** to pull in those new streams for syncing.

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about Hubspot connector limitations and troubleshooting.
</summary>

### Connector limitations

### Rate limiting

The connector is restricted by normal HubSpot [rate limitations](https://legacydocs.hubspot.com/apps/api_guidelines).

| Product tier                | Limits                                  |
| :-------------------------- | :-------------------------------------- |
| `Free & Starter`            | Burst: 100/10 seconds, Daily: 250,000   |
| `Professional & Enterprise` | Burst: 150/10 seconds, Daily: 500,000   |
| `API add-on (any tier)`     | Burst: 200/10 seconds, Daily: 1,000,000 |

### Troubleshooting

- **Enabling streams:** Some streams, such as `workflows`, need to be enabled before they can be read using a connector authenticated using an `API Key`. If reading a stream that is not enabled, a log message returned to the output and the sync operation will only sync the other streams available.

  Example of the output message when trying to read `workflows` stream with missing permissions for the `API Key`:

  ```json
  {
    "type": "LOG",
    "log": {
      "level": "WARN",
      "message": "Stream `workflows` cannot be proceed. This API Key (EXAMPLE_API_KEY) does not have proper permissions! (requires any of [automation-access])"
    }
  }
  ```

- **Hubspot object labels** In Hubspot, a label can be applied to a stream that differs from the original API name of the stream. Hubspot's UI shows the label of the stream, whereas Airbyte shows the name of the stream. If you are having issues seeing a particular stream your user should have access to, search for the `name` of the Hubspot object instead.

- **Unnesting top level properties**: Since version 1.5.0, in order to offer users access to nested fields, we also denest the top-level fields into individual fields in the destination. This is most commonly observed in the `properties` field, which is now split into each attribute in the destination.

  For instance:

  ```json
  {
    "id": 1,
    "updatedAt": "2020-01-01",
    "properties": {
      "hs_note_body": "World's best boss",
      "hs_created_by": "Michael Scott"
    }
  }
  ```

  becomes

  ```json
  {
    "id": 1,
    "updatedAt": "2020-01-01",
    "properties": {
      "hs_note_body": "World's best boss",
      "hs_created_by": "Michael Scott"
    },
    "properties_hs_note_body": "World's best boss",
    "properties_hs_created_by": "Michael Scott"
  }
  ```

- **403 Forbidden Error**

  - Hubspot has **scopes** for each API call.
  - Each stream is tied to a scope and will need access to that scope to sync data.
  - Review the Hubspot OAuth scope documentation [here](https://developers.hubspot.com/docs/api/working-with-oauth#scopes).
  - Additional permissions:

    `feedback_submissions`: Service Hub Professional account

    `marketing_emails`: Market Hub Starter account

    `workflows`: Sales, Service, and Marketing Hub Professional accounts

- Check out common troubleshooting issues for the Hubspot source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

</details>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                          |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 4.4.9 | 2025-02-01 | [52729](https://github.com/airbytehq/airbyte/pull/52729) | Update dependencies |
| 4.4.8 | 2025-01-25 | [52295](https://github.com/airbytehq/airbyte/pull/52295) | Update dependencies |
| 4.4.7 | 2025-01-11 | [51146](https://github.com/airbytehq/airbyte/pull/51146) | Update dependencies |
| 4.4.6 | 2025-01-04 | [50898](https://github.com/airbytehq/airbyte/pull/50898) | Update dependencies |
| 4.4.5 | 2024-12-28 | [50669](https://github.com/airbytehq/airbyte/pull/50669) | Update dependencies |
| 4.4.4 | 2024-12-21 | [50138](https://github.com/airbytehq/airbyte/pull/50138) | Update dependencies |
| 4.4.3 | 2024-12-14 | [48984](https://github.com/airbytehq/airbyte/pull/48984) | Update dependencies |
| 4.4.2 | 2024-12-10 | [48480](https://github.com/airbytehq/airbyte/pull/48480) | Adds individual read scopes to LineItems Stream |
| 4.4.1 | 2024-11-25 | [48662](https://github.com/airbytehq/airbyte/pull/48662) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 4.4.0 | 2024-11-18 | [48548](https://github.com/airbytehq/airbyte/pull/48548) | Promoting release candidate 4.4.0-rc.1 to a main version. |
| 4.4.0-rc.1 | 2024-11-18 | [48472](https://github.com/airbytehq/airbyte/pull/48472) | Adds support to maintain use of legacy fields for `Contacts`, `Deals`, and `DealsArchived` streams: `hs_lifecyclestage_{stage_id}_date`, `hs_date_entered_{stage_id}`, `hs_date_exited_{stage_id}`, `hs_time_in_{stage_id}`. |
| 4.3.0  | 2024-11-15 | [44481](https://github.com/airbytehq/airbyte/pull/44481) | Add `Leads` stream |
| 4.2.26 | 2024-11-04 | [48199](https://github.com/airbytehq/airbyte/pull/48199) | Update dependencies |
| 4.2.25 | 2024-10-29 | [47028](https://github.com/airbytehq/airbyte/pull/47028) | Update dependencies |
| 4.2.24 | 2024-10-12 | [46827](https://github.com/airbytehq/airbyte/pull/46827) | Update dependencies |
| 4.2.23 | 2024-10-05 | [46494](https://github.com/airbytehq/airbyte/pull/46494) | Update dependencies |
| 4.2.22 | 2024-09-28 | [46160](https://github.com/airbytehq/airbyte/pull/46160) | Update dependencies |
| 4.2.21 | 2024-09-23 | [42688](https://github.com/airbytehq/airbyte/pull/44899) | Fix incremental search to use primary key as placeholder instead of lastModifiedDate |
| 4.2.20 | 2024-09-21 | [45753](https://github.com/airbytehq/airbyte/pull/45753) | Update dependencies |
| 4.2.19 | 2024-09-14 | [45018](https://github.com/airbytehq/airbyte/pull/45018) | Update dependencies |
| 4.2.18 | 2024-08-24 | [43762](https://github.com/airbytehq/airbyte/pull/43762) | Update dependencies |
| 4.2.17 | 2024-08-21 | [44538](https://github.com/airbytehq/airbyte/pull/44538) | Fix issue with CRM search streams when they have no `associations` |
| 4.2.16 | 2024-08-20 | [42919](https://github.com/airbytehq/airbyte/pull/42919) | Add support for Deal Splits |
| 4.2.15 | 2024-08-08 | [43381](https://github.com/airbytehq/airbyte/pull/43381) | Fix associations retrieval for Engagements streams (calls, meetings, notes, tasks, emails) in Incremental with existing state |
| 4.2.14 | 2024-07-27 | [42688](https://github.com/airbytehq/airbyte/pull/42688) | Update dependencies |
| 4.2.13 | 2024-07-20 | [42264](https://github.com/airbytehq/airbyte/pull/42264) | Update dependencies |
| 4.2.12 | 2024-07-13 | [41766](https://github.com/airbytehq/airbyte/pull/41766) | Update dependencies |
| 4.2.11 | 2024-07-10 | [41558](https://github.com/airbytehq/airbyte/pull/41558) | Update dependencies |
| 4.2.10 | 2024-07-09 | [41286](https://github.com/airbytehq/airbyte/pull/41286) | Update dependencies |
| 4.2.9 | 2024-07-08 | [41045](https://github.com/airbytehq/airbyte/pull/41045) | Use latest `CDK` version possible |
| 4.2.8 | 2024-07-06 | [40923](https://github.com/airbytehq/airbyte/pull/40923) | Update dependencies |
| 4.2.7 | 2024-06-25 | [40441](https://github.com/airbytehq/airbyte/pull/40441) | Update dependencies |
| 4.2.6 | 2024-06-22 | [40126](https://github.com/airbytehq/airbyte/pull/40126) | Update dependencies |
| 4.2.5 | 2024-06-17 | [39432](https://github.com/airbytehq/airbyte/pull/39432) | Remove references to deprecated state method |
| 4.2.4 | 2024-06-10 | [38800](https://github.com/airbytehq/airbyte/pull/38800) | Retry hubspot _parse_and_handle_errors on JSON decode errors |
| 4.2.3 | 2024-06-06 | [39314](https://github.com/airbytehq/airbyte/pull/39314) | Added missing schema types for the `Workflows` stream schema |
| 4.2.2 | 2024-06-04 | [38981](https://github.com/airbytehq/airbyte/pull/38981) | [autopull] Upgrade base image to v1.2.1 |
| 4.2.1 | 2024-05-30 | [38024](https://github.com/airbytehq/airbyte/pull/38024) | etry when attempting to get scopes |
| 4.2.0 | 2024-05-24 | [38049](https://github.com/airbytehq/airbyte/pull/38049) | Add resumable full refresh support to `contacts_form_submissions` and `contacts_merged_audit` streams |
| 4.1.5 | 2024-05-17 | [38243](https://github.com/airbytehq/airbyte/pull/38243) | Replace AirbyteLogger with logging.Logger |
| 4.1.4 | 2024-05-16 | [38286](https://github.com/airbytehq/airbyte/pull/38286) | Added default schema normalization for the  `Tickets` stream, to ensure the data types |
| 4.1.3 | 2024-05-13 | [38128](https://github.com/airbytehq/airbyte/pull/38128) | contacts_list_memberships as semi-incremental stream |
| 4.1.2 | 2024-04-24 | [36642](https://github.com/airbytehq/airbyte/pull/36642) | Schema descriptions and CDK 0.80.0 |
| 4.1.1 | 2024-04-11 | [35945](https://github.com/airbytehq/airbyte/pull/35945) | Add integration tests |
| 4.1.0 | 2024-03-27 | [36541](https://github.com/airbytehq/airbyte/pull/36541) | Added test configuration features, fixed type hints |
| 4.0.0 | 2024-03-10 | [35662](https://github.com/airbytehq/airbyte/pull/35662) | Update `Deals Property History` and `Companies Property History` schemas |
| 3.3.0 | 2024-02-16 | [34597](https://github.com/airbytehq/airbyte/pull/34597) | Make start date not required, sync all data from default value if it's not provided |
| 3.2.0 | 2024-02-15 | [35328](https://github.com/airbytehq/airbyte/pull/35328) | Add mailingIlsListsIncluded and mailingIlsListsExcluded fields to Marketing emails stream schema |
| 3.1.1 | 2024-02-12 | [35165](https://github.com/airbytehq/airbyte/pull/35165) | Manage dependencies with Poetry. |
| 3.1.0 | 2024-02-05 | [34829](https://github.com/airbytehq/airbyte/pull/34829) | Add `Contacts Form Submissions` stream |
| 3.0.1 | 2024-01-29 | [34635](https://github.com/airbytehq/airbyte/pull/34635) | Fix pagination for `CompaniesPropertyHistory` stream |
| 3.0.0 | 2024-01-25 | [34492](https://github.com/airbytehq/airbyte/pull/34492) | Update `marketing_emails` stream schema |
| 2.0.2 | 2023-12-15 | [33844](https://github.com/airbytehq/airbyte/pull/33844) | Make property_history PK combined to support Incremental/Deduped sync type |
| 2.0.1 | 2023-12-15 | [33527](https://github.com/airbytehq/airbyte/pull/33527) | Make query string calculated correctly for PropertyHistory streams to avoid 414 HTTP Errors |
| 2.0.0 | 2023-12-08 | [33266](https://github.com/airbytehq/airbyte/pull/33266) | Add ContactsPropertyHistory, CompaniesPropertyHistory, DealsPropertyHistory streams |
| 1.9.0 | 2023-12-04 | [33042](https://github.com/airbytehq/airbyte/pull/33042) | Add Web Analytics streams |
| 1.8.0 | 2023-11-23 | [32778](https://github.com/airbytehq/airbyte/pull/32778) | Extend `PropertyHistory` stream to support incremental sync |
| 1.7.0 | 2023-11-01 | [32035](https://github.com/airbytehq/airbyte/pull/32035) | Extend the `Forms` stream schema |
| 1.6.1 | 2023-10-20 | [31644](https://github.com/airbytehq/airbyte/pull/31644) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 1.6.0 | 2023-10-19 | [31606](https://github.com/airbytehq/airbyte/pull/31606) | Add new field `aifeatures` to the `marketing emails` stream schema |
| 1.5.1 | 2023-10-04 | [31050](https://github.com/airbytehq/airbyte/pull/31050) | Add type transformer for `Engagements` stream |
| 1.5.0 | 2023-09-11 | [30322](https://github.com/airbytehq/airbyte/pull/30322) | Unnest stream schemas |
| 1.4.1 | 2023-08-22 | [29715](https://github.com/airbytehq/airbyte/pull/29715) | Fix python package configuration stream |
| 1.4.0 | 2023-08-11 | [29249](https://github.com/airbytehq/airbyte/pull/29249) | Add `OwnersArchived` stream |
| 1.3.3 | 2023-08-10 | [29248](https://github.com/airbytehq/airbyte/pull/29248) | Specify `threadId` in `engagements` stream to type string |
| 1.3.2 | 2023-08-10 | [29326](https://github.com/airbytehq/airbyte/pull/29326) | Add primary keys to streams `ContactLists` and `PropertyHistory` |
| 1.3.1 | 2023-08-08 | [29211](https://github.com/airbytehq/airbyte/pull/29211) | Handle 400 and 403 errors without interruption of the sync |
| 1.3.0 | 2023-08-01 | [28909](https://github.com/airbytehq/airbyte/pull/28909) | Add handling of source connection errors |
| 1.2.0 | 2023-07-27 | [27091](https://github.com/airbytehq/airbyte/pull/27091) | Add new stream `ContactsMergedAudit` |
| 1.1.2 | 2023-07-27 | [28558](https://github.com/airbytehq/airbyte/pull/28558) | Improve error messages during connector setup |
| 1.1.1 | 2023-07-25 | [28705](https://github.com/airbytehq/airbyte/pull/28705) | Fix retry handler for token expired error |
| 1.1.0 | 2023-07-18 | [28349](https://github.com/airbytehq/airbyte/pull/28349) | Add unexpected fields in schemas of streams `email_events`, `email_subscriptions`, `engagements`, `campaigns` |
| 1.0.1 | 2023-06-23 | [27658](https://github.com/airbytehq/airbyte/pull/27658) | Use fully qualified name to retrieve custom objects |
| 1.0.0 | 2023-06-08 | [27161](https://github.com/airbytehq/airbyte/pull/27161) | Fix increment sync for engagements stream, 'Recent' API is used for recent syncs of last recent 30 days and less than 10k records, otherwise full sync if performed by 'All' API |
| 0.9.0 | 2023-06-26 | [27726](https://github.com/airbytehq/airbyte/pull/27726) | License Update: Elv2 |
| 0.8.4   | 2023-05-17 | [25667](https://github.com/airbytehq/airbyte/pull/26082) | Fixed bug with wrong parsing of boolean encoded like "false" parsed as True                                                                                                      |
| 0.8.3   | 2023-05-31 | [26831](https://github.com/airbytehq/airbyte/pull/26831) | Remove authSpecification from connector specification in favour of advancedAuth                                                                                                  |
| 0.8.2   | 2023-05-16 | [26418](https://github.com/airbytehq/airbyte/pull/26418) | Add custom availability strategy which catches permission errors from parent streams                                                                                             |
| 0.8.1   | 2023-05-29 | [26719](https://github.com/airbytehq/airbyte/pull/26719) | Handle issue when `state` value is literally `"" (empty str)`                                                                                                                    |
| 0.8.0   | 2023-04-10 | [16032](https://github.com/airbytehq/airbyte/pull/16032) | Add new stream `Custom Object`                                                                                                                                                   |
| 0.7.0   | 2023-04-10 | [24450](https://github.com/airbytehq/airbyte/pull/24450) | Add new stream `Goals`                                                                                                                                                           |
| 0.6.2   | 2023-04-28 | [25667](https://github.com/airbytehq/airbyte/pull/25667) | Fix bug with `Invalid Date` like `2000-00-00T00:00:00Z` while settip up the connector                                                                                            |
| 0.6.1   | 2023-04-10 | [21423](https://github.com/airbytehq/airbyte/pull/21423) | Update scope for `DealPipelines` stream to only `crm.objects.contacts.read`                                                                                                      |
| 0.6.0   | 2023-04-07 | [24980](https://github.com/airbytehq/airbyte/pull/24980) | Add new stream `DealsArchived`                                                                                                                                                   |
| 0.5.2   | 2023-04-07 | [24915](https://github.com/airbytehq/airbyte/pull/24915) | Fix field key parsing (replace whitespace with uderscore)                                                                                                                        |
| 0.5.1   | 2023-04-05 | [22982](https://github.com/airbytehq/airbyte/pull/22982) | Specified date formatting in specification                                                                                                                                       |
| 0.5.0   | 2023-03-30 | [24711](https://github.com/airbytehq/airbyte/pull/24711) | Add incremental sync support for `campaigns`, `deal_pipelines`, `ticket_pipelines`, `forms`, `form_submissions`, `form_submissions`, `workflows`, `owners`                       |
| 0.4.0   | 2023-03-31 | [22910](https://github.com/airbytehq/airbyte/pull/22910) | Add `email_subscriptions` stream                                                                                                                                                 |
| 0.3.4   | 2023-03-28 | [24641](https://github.com/airbytehq/airbyte/pull/24641) | Convert to int only numeric values                                                                                                                                               |
| 0.3.3   | 2023-03-27 | [24591](https://github.com/airbytehq/airbyte/pull/24591) | Fix pagination for `marketing emails` stream                                                                                                                                     |
| 0.3.2   | 2023-02-07 | [22479](https://github.com/airbytehq/airbyte/pull/22479) | Turn on default HttpAvailabilityStrategy                                                                                                                                         |
| 0.3.1   | 2023-01-27 | [22009](https://github.com/airbytehq/airbyte/pull/22009) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                                                                                      |
| 0.3.0   | 2022-10-27 | [18546](https://github.com/airbytehq/airbyte/pull/18546) | Sunsetting API Key authentication. `Quotes` stream is no longer available                                                                                                        |
| 0.2.2   | 2022-10-03 | [16914](https://github.com/airbytehq/airbyte/pull/16914) | Fix 403 forbidden error validation                                                                                                                                               |
| 0.2.1   | 2022-09-26 | [17120](https://github.com/airbytehq/airbyte/pull/17120) | Migrate to per-stream state.                                                                                                                                                     |
| 0.2.0   | 2022-09-13 | [16632](https://github.com/airbytehq/airbyte/pull/16632) | Remove Feedback Submissions stream as the one using unstable (beta) API.                                                                                                         |
| 0.1.83  | 2022-09-01 | [16214](https://github.com/airbytehq/airbyte/pull/16214) | Update Tickets, fix missing properties and change how state is updated.                                                                                                          |
| 0.1.82  | 2022-08-18 | [15110](https://github.com/airbytehq/airbyte/pull/15110) | Check if it has a state on search streams before first sync                                                                                                                      |
| 0.1.81  | 2022-08-05 | [15354](https://github.com/airbytehq/airbyte/pull/15354) | Fix `Deals` stream schema                                                                                                                                                        |
| 0.1.80  | 2022-08-01 | [15156](https://github.com/airbytehq/airbyte/pull/15156) | Fix 401 error while retrieving associations using OAuth                                                                                                                          |
| 0.1.79  | 2022-07-28 | [15144](https://github.com/airbytehq/airbyte/pull/15144) | Revert v0.1.78 due to permission issues                                                                                                                                          |
| 0.1.78  | 2022-07-28 | [15099](https://github.com/airbytehq/airbyte/pull/15099) | Fix to fetch associations when using incremental mode                                                                                                                            |
| 0.1.77  | 2022-07-26 | [15035](https://github.com/airbytehq/airbyte/pull/15035) | Make PropertyHistory stream read historic data not limited to 30 days                                                                                                            |
| 0.1.76  | 2022-07-25 | [14999](https://github.com/airbytehq/airbyte/pull/14999) | Partially revert changes made in v0.1.75                                                                                                                                         |
| 0.1.75  | 2022-07-18 | [14744](https://github.com/airbytehq/airbyte/pull/14744) | Remove override of private CDK method                                                                                                                                            |
| 0.1.74  | 2022-07-25 | [14412](https://github.com/airbytehq/airbyte/pull/14412) | Add private app authentication                                                                                                                                                   |
| 0.1.73  | 2022-07-13 | [14666](https://github.com/airbytehq/airbyte/pull/14666) | Decrease number of http requests made, disable Incremental mode for PropertyHistory stream                                                                                       |
| 0.1.72  | 2022-06-24 | [14054](https://github.com/airbytehq/airbyte/pull/14054) | Extended error logging                                                                                                                                                           |
| 0.1.71  | 2022-06-24 | [14102](https://github.com/airbytehq/airbyte/pull/14102) | Removed legacy `AirbyteSentry` dependency from the code                                                                                                                          |
| 0.1.70  | 2022-06-16 | [13837](https://github.com/airbytehq/airbyte/pull/13837) | Fix the missing data in CRM streams issue                                                                                                                                        |
| 0.1.69  | 2022-06-10 | [13691](https://github.com/airbytehq/airbyte/pull/13691) | Fix the `URI Too Long` issue                                                                                                                                                     |
| 0.1.68  | 2022-06-08 | [13596](https://github.com/airbytehq/airbyte/pull/13596) | Fix for the `property_history` which did not emit records                                                                                                                        |
| 0.1.67  | 2022-06-07 | [13566](https://github.com/airbytehq/airbyte/pull/13566) | Report which scopes are missing to the user                                                                                                                                      |
| 0.1.66  | 2022-06-05 | [13475](https://github.com/airbytehq/airbyte/pull/13475) | Scope `crm.objects.feedback_submissions.read` added for `feedback_submissions` stream                                                                                            |
| 0.1.65  | 2022-06-03 | [13455](https://github.com/airbytehq/airbyte/pull/13455) | Discover only returns streams for which required scopes were granted                                                                                                             |
| 0.1.64  | 2022-06-03 | [13218](https://github.com/airbytehq/airbyte/pull/13218) | Transform `contact_lists` data to comply with schema                                                                                                                             |
| 0.1.63  | 2022-06-02 | [13320](https://github.com/airbytehq/airbyte/pull/13320) | Fix connector incremental state handling                                                                                                                                         |
| 0.1.62  | 2022-06-01 | [13383](https://github.com/airbytehq/airbyte/pull/13383) | Add `line items` to `deals` stream                                                                                                                                               |
| 0.1.61  | 2022-05-25 | [13381](https://github.com/airbytehq/airbyte/pull/13381) | Requests scopes as optional instead of required                                                                                                                                  |
| 0.1.60  | 2022-05-25 | [13159](https://github.com/airbytehq/airbyte/pull/13159) | Use RFC3339 datetime                                                                                                                                                             |
| 0.1.59  | 2022-05-10 | [12711](https://github.com/airbytehq/airbyte/pull/12711) | Ensure oauth2.0 token has all needed scopes in "check" command                                                                                                                   |
| 0.1.58  | 2022-05-04 | [12482](https://github.com/airbytehq/airbyte/pull/12482) | Update input configuration copy                                                                                                                                                  |
| 0.1.57  | 2022-05-04 | [12198](https://github.com/airbytehq/airbyte/pull/12198) | Add deals associations for quotes                                                                                                                                                |
| 0.1.56  | 2022-05-02 | [12515](https://github.com/airbytehq/airbyte/pull/12515) | Extra logs for troubleshooting 403 errors                                                                                                                                        |
| 0.1.55  | 2022-04-28 | [12424](https://github.com/airbytehq/airbyte/pull/12424) | Correct schema for ticket_pipeline stream                                                                                                                                        |
| 0.1.54  | 2022-04-28 | [12335](https://github.com/airbytehq/airbyte/pull/12335) | Mock time slep in unit test s                                                                                                                                                    |
| 0.1.53  | 2022-04-20 | [12230](https://github.com/airbytehq/airbyte/pull/12230) | Change spec json to yaml format                                                                                                                                                  |
| 0.1.52  | 2022-03-25 | [11423](https://github.com/airbytehq/airbyte/pull/11423) | Add tickets associations to engagements streams                                                                                                                                  |
| 0.1.51  | 2022-03-24 | [11321](https://github.com/airbytehq/airbyte/pull/11321) | Fix updated at field non exists issue                                                                                                                                            |
| 0.1.50  | 2022-03-22 | [11266](https://github.com/airbytehq/airbyte/pull/11266) | Fix Engagements Stream Pagination                                                                                                                                                |
| 0.1.49  | 2022-03-17 | [11218](https://github.com/airbytehq/airbyte/pull/11218) | Anchor hyperlink in input configuration                                                                                                                                          |
| 0.1.48  | 2022-03-16 | [11105](https://github.com/airbytehq/airbyte/pull/11105) | Fix float numbers, upd docs                                                                                                                                                      |
| 0.1.47  | 2022-03-15 | [11121](https://github.com/airbytehq/airbyte/pull/11121) | Add partition keys where appropriate                                                                                                                                             |
| 0.1.46  | 2022-03-14 | [10700](https://github.com/airbytehq/airbyte/pull/10700) | Handle 10k+ records reading in Hubspot streams                                                                                                                                   |
| 0.1.45  | 2022-03-04 | [10707](https://github.com/airbytehq/airbyte/pull/10707) | Remove stage history from deals stream to increase efficiency                                                                                                                    |
| 0.1.44  | 2022-02-24 | [9027](https://github.com/airbytehq/airbyte/pull/9027)   | Add associations companies to deals, ticket and contact stream                                                                                                                   |
| 0.1.43  | 2022-02-24 | [10576](https://github.com/airbytehq/airbyte/pull/10576) | Cast timestamp to date/datetime                                                                                                                                                  |
| 0.1.42  | 2022-02-22 | [10492](https://github.com/airbytehq/airbyte/pull/10492) | Add `date-time` format to datetime fields                                                                                                                                        |
| 0.1.41  | 2022-02-21 | [10177](https://github.com/airbytehq/airbyte/pull/10177) | Migrate to CDK                                                                                                                                                                   |
| 0.1.40  | 2022-02-10 | [10142](https://github.com/airbytehq/airbyte/pull/10142) | Add associations to ticket stream                                                                                                                                                |
| 0.1.39  | 2022-02-10 | [10055](https://github.com/airbytehq/airbyte/pull/10055) | Bug fix: reading not initialized stream                                                                                                                                          |
| 0.1.38  | 2022-02-03 | [9786](https://github.com/airbytehq/airbyte/pull/9786)   | Add new streams for engagements(calls, emails, meetings, notes and tasks)                                                                                                        |
| 0.1.37  | 2022-01-27 | [9555](https://github.com/airbytehq/airbyte/pull/9555)   | Getting form_submission for all forms                                                                                                                                            |
| 0.1.36  | 2022-01-22 | [7784](https://github.com/airbytehq/airbyte/pull/7784)   | Add Property History Stream                                                                                                                                                      |
| 0.1.35  | 2021-12-24 | [9081](https://github.com/airbytehq/airbyte/pull/9081)   | Add Feedback Submissions stream and update Ticket Pipelines stream                                                                                                               |
| 0.1.34  | 2022-01-20 | [9641](https://github.com/airbytehq/airbyte/pull/9641)   | Add more fields for `email_events` stream                                                                                                                                        |
| 0.1.33  | 2022-01-14 | [8887](https://github.com/airbytehq/airbyte/pull/8887)   | More efficient support for incremental updates on Companies, Contact, Deals and Engagement streams                                                                               |
| 0.1.32  | 2022-01-13 | [8011](https://github.com/airbytehq/airbyte/pull/8011)   | Add new stream form_submissions                                                                                                                                                  |
| 0.1.31  | 2022-01-11 | [9385](https://github.com/airbytehq/airbyte/pull/9385)   | Remove auto-generated `properties` from `Engagements` stream                                                                                                                     |
| 0.1.30  | 2021-01-10 | [9129](https://github.com/airbytehq/airbyte/pull/9129)   | Created Contacts list memberships streams                                                                                                                                        |
| 0.1.29  | 2021-12-17 | [8699](https://github.com/airbytehq/airbyte/pull/8699)   | Add incremental sync support for `companies`, `contact_lists`, `contacts`, `deals`, `line_items`, `products`, `quotes`, `tickets` streams                                        |
| 0.1.28  | 2021-12-15 | [8429](https://github.com/airbytehq/airbyte/pull/8429)   | Update fields and descriptions                                                                                                                                                   |
| 0.1.27  | 2021-12-09 | [8658](https://github.com/airbytehq/airbyte/pull/8658)   | Fix config backward compatibility issue by allowing additional properties in the spec                                                                                            |
| 0.1.26  | 2021-11-30 | [8329](https://github.com/airbytehq/airbyte/pull/8329)   | Remove 'skip_dynamic_fields' config param                                                                                                                                        |
| 0.1.25  | 2021-11-23 | [8216](https://github.com/airbytehq/airbyte/pull/8216)   | Add skip dynamic fields for testing only                                                                                                                                         |
| 0.1.24  | 2021-11-09 | [7683](https://github.com/airbytehq/airbyte/pull/7683)   | Fix name issue 'Hubspot' -> 'HubSpot'                                                                                                                                            |
| 0.1.23  | 2021-11-08 | [7730](https://github.com/airbytehq/airbyte/pull/7730)   | Fix OAuth flow schema                                                                                                                                                            |
| 0.1.22  | 2021-11-03 | [7562](https://github.com/airbytehq/airbyte/pull/7562)   | Migrate Hubspot source to CDK structure                                                                                                                                          |
| 0.1.21  | 2021-10-27 | [7405](https://github.com/airbytehq/airbyte/pull/7405)   | Change of package `import` from `urllib` to `urllib.parse`                                                                                                                       |
| 0.1.20  | 2021-10-26 | [7393](https://github.com/airbytehq/airbyte/pull/7393)   | Hotfix for `split_properties` function, add the length of separator symbol `,`(`%2C` in HTTP format) to the checking of the summary URL length                                   |
| 0.1.19  | 2021-10-26 | [6954](https://github.com/airbytehq/airbyte/pull/6954)   | Fix issue with getting `414` HTTP error for streams                                                                                                                              |
| 0.1.18  | 2021-10-18 | [5840](https://github.com/airbytehq/airbyte/pull/5840)   | Add new marketing emails (with statistics) stream                                                                                                                                |
| 0.1.17  | 2021-10-14 | [6995](https://github.com/airbytehq/airbyte/pull/6995)   | Update `discover` method: disable `quotes` stream when using OAuth config                                                                                                        |
| 0.1.16  | 2021-09-27 | [6465](https://github.com/airbytehq/airbyte/pull/6465)   | Implement OAuth support. Use CDK authenticator instead of connector specific authenticator                                                                                       |
| 0.1.15  | 2021-09-23 | [6374](https://github.com/airbytehq/airbyte/pull/6374)   | Use correct schema for `owners` stream                                                                                                                                           |
| 0.1.14  | 2021-09-08 | [5693](https://github.com/airbytehq/airbyte/pull/5693)   | Include deal_to_contact association when pulling deal stream and include contact ID in contact stream                                                                            |
| 0.1.13  | 2021-09-08 | [5834](https://github.com/airbytehq/airbyte/pull/5834)   | Fix array fields without items property in schema                                                                                                                                |
| 0.1.12  | 2021-09-02 | [5798](https://github.com/airbytehq/airbyte/pull/5798)   | Treat empty string values as None for field with format to fix normalization errors                                                                                              |
| 0.1.11  | 2021-08-26 | [5685](https://github.com/airbytehq/airbyte/pull/5685)   | Remove all date-time format from schemas                                                                                                                                         |
| 0.1.10  | 2021-08-17 | [5463](https://github.com/airbytehq/airbyte/pull/5463)   | Fix fail on reading stream using `API Key` without required permissions                                                                                                          |
| 0.1.9   | 2021-08-11 | [5334](https://github.com/airbytehq/airbyte/pull/5334)   | Fix empty strings inside float datatype                                                                                                                                          |
| 0.1.8   | 2021-08-06 | [5250](https://github.com/airbytehq/airbyte/pull/5250)   | Fix issue with printing exceptions                                                                                                                                               |
| 0.1.7   | 2021-07-27 | [4913](https://github.com/airbytehq/airbyte/pull/4913)   | Update fields schema                                                                                                                                                             |

</details>

</HideInUI>
