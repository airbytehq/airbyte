# HubSpot

This page contains the setup guide and reference information for HubSpot.

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Namespaces | No |

There are two types of incremental sync:

* Incremental (standard server-side, where API returns only the data updated or generated since the last sync)
* Client-Side Incremental (API returns all available data and connector filters out only new records)

## Prerequisites

* A private HubSpot app with Access Token, OR

## Setup guide

### Step 1: Create a HubSpot App

Follow these [instructions](https://developers.hubspot.com/docs/api/private-apps) or the below steps to create a HubSpot App and obtain the Access Token needed to set up the source in Daspire.

1. In your HubSpot account, click the **settings icon** in the top navigation bar.
![HubSpot Settings](/docs/setup-guide/assets/images/hubspot-settings.jpg "HubSpot Settings")

2. In the left sidebar menu, navigate to **Integrations > Private Apps**.
![HubSpot Private Apps](/docs/setup-guide/assets/images/hubspot-private-apps.jpg "HubSpot Private Apps")

3. Click **Create private app**.

4. On the **Basic Info** tab, enter your app's name.

5. Click the **Scopes** tab. Select the Read checkbox for each scope you want your private app to be able to access.

  > NOTE: Daspire needs the following Scopes to be able to sync all the streams listed below.

| Stream | Scope |
| --- | --- |
| `campaigns` | `content` |
| `companies` | `crm.objects.companies.read`, `crm.schemas.companies.read` |
| `contact_lists` | `crm.objects.lists.read` |
| `contacts` | `crm.objects.contacts.read` |
| `contacts_list_memberships` | `crm.objects.contacts.read` |
| Custom CRM Objects | `crm.objects.custom.read` |
| `deal_pipelines` | `crm.objects.contacts.read` |
| `deals` | `crm.objects.deals.read`, `crm.schemas.deals.read` |
| `deals_archived` | `crm.objects.deals.read`, `crm.schemas.deals.read` |
| `email_events` | `content` |
| `email_subscriptions` | `content` |
| `engagements` | `crm.objects.companies.read`, `crm.objects.contacts.read`, `crm.objects.deals.read`, `tickets`, `e-commerce` |
| `engagements_emails` | `sales-email-read` |
| `forms` | `forms` |
| `form_submissions` | `forms` |
| `goals` | `crm.objects.goals.read` |
| `line_items` | `e-commerce` |
| `owners` | `crm.objects.owners.read` |
| `products` | `e-commerce` |
| `property_history` | `crm.objects.contacts.read` |
| `subscription_changes` | `content` |
| `tickets` | `tickets` |
| `workflows` | `automation` |

6. After you're done configuring your app, click **Create app** on the top right.
![HubSpot Create Private App](/docs/setup-guide/assets/images/hubspot-create-app.jpg "HubSpot Create Private App")

7. Once your private app is created, you will get an **Access Token**. Copy that. You will use it to set up the source in Daspire.
![HubSpot Access Token](/docs/setup-guide/assets/images/hubspot-access-token.jpg "HubSpot Access Token")

### Step 2: Set up HubSpot in Daspire

1. Select **HubSpot** from the Source list.

2. Enter a **Source Name**.

3. To authenticate using a Private App, enter the **Access Token** for your HubSpot account you obtained in Step 1.

4. For **Start date**, enter the date in the following format: `yyyy-mm-ddThh:mm:ssZ`. The data added on and after this date will be replicated.

5. Click **Save & Test**.

## Supported streams

This source is capable of syncing the following streams:

* [Campaigns](https://developers.hubspot.com/docs/methods/email/get_campaign_data) (Client-Side Incremental)
* [Companies](https://developers.hubspot.com/docs/api/crm/companies) (Incremental)
* [Contact Lists](http://developers.hubspot.com/docs/methods/lists/get_lists) (Incremental)
* [Contacts](https://developers.hubspot.com/docs/methods/contacts/get_contacts) (Incremental)
* [Contacts List Memberships](https://legacydocs.hubspot.com/docs/methods/contacts/get_contacts)
* [Deal Pipelines](https://developers.hubspot.com/docs/methods/pipelines/get_pipelines_for_object_type) (Client-Side Incremental)
* [Deals](https://developers.hubspot.com/docs/api/crm/deals) (including Contact associations) (Incremental)
* [Deals Archived](https://developers.hubspot.com/docs/api/crm/deals) (including Contact associations) (Incremental)
* [Email Events](https://developers.hubspot.com/docs/methods/email/get_events) (Incremental)
* [Email Subscriptions](https://developers.hubspot.com/docs/methods/email/get_subscriptions)
* [Engagements](https://legacydocs.hubspot.com/docs/methods/engagements/get-all-engagements) (Incremental)
* [Engagements Calls](https://developers.hubspot.com/docs/api/crm/calls) (Incremental)
* [Engagements Emails](https://developers.hubspot.com/docs/api/crm/email) (Incremental)
* [Engagements Meetings](https://developers.hubspot.com/docs/api/crm/meetings) (Incremental)
* [Engagements Notes](https://developers.hubspot.com/docs/api/crm/notes) (Incremental)
* [Engagements Tasks](https://developers.hubspot.com/docs/api/crm/tasks) (Incremental)
* [Forms](https://developers.hubspot.com/docs/api/marketing/forms) (Client-Side Incremental)
* [Form Submissions](https://legacydocs.hubspot.com/docs/methods/forms/get-submissions-for-a-form) (Client-Side Incremental)
* [Goals](https://developers.hubspot.com/docs/api/crm/goals) (Incremental)
* [Line Items](https://developers.hubspot.com/docs/api/crm/line-items) (Incremental)
* [Marketing Emails](https://legacydocs.hubspot.com/docs/methods/cms_email/get-all-marketing-email-statistics)
* [Owners](https://developers.hubspot.com/docs/methods/owners/get_owners) (Client-Side Incremental)
* [Products](https://developers.hubspot.com/docs/api/crm/products) (Incremental)
* [Property History](https://legacydocs.hubspot.com/docs/methods/contacts/get_contacts) (Incremental)
* [Subscription Changes](https://developers.hubspot.com/docs/methods/email/get_subscriptions_timeline) (Incremental)
* [Tickets](https://developers.hubspot.com/docs/api/crm/tickets) (Incremental)
* [Ticket Pipelines](https://developers.hubspot.com/docs/api/crm/pipelines) (Client-Side Incremental)
* [Workflows](https://legacydocs.hubspot.com/docs/methods/workflows/v3/get_workflows) (Client-Side Incremental)
* [ContactsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) (Incremental)
* [CompaniesWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) (Incremental)
* [DealsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) (Incremental)
* [TicketsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) (Incremental)
* [EngagementsCallsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) (Incremental)
* [EngagementsEmailsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) (Incremental)
* [EngagementsMeetingsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) (Incremental)
* [EngagementsNotesWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) (Incremental)
* [EngagementsTasksWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) (Incremental)
* [GoalsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) (Incremental)
* [LineItemsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) (Incremental)
* [ProductsWebAnalytics](https://developers.hubspot.com/docs/api/events/web-analytics) (Incremental)

### Notes on the `engagements` stream

1. Objects in the `engagements` stream can have one of the following types: `note`, `email`, `task`, `meeting`, `call`. Depending on the type of engagement, different properties are set for that object in the `engagements_metadata` table in the destination:

  * A `call` engagement has a corresponding `engagements_metadata` object with non-null values in the `toNumber`, `fromNumber`, `status`, `externalId`, `durationMilliseconds`, `externalAccountId`, `recordingUrl`, `body`, and `disposition` columns.
  * An `email` engagement has a corresponding `engagements_metadata` object with non-null values in the `subject`, `html`, and `text` columns. In addition, there will be records in four related tables, `engagements_metadata_from`, `engagements_metadata_to`, `engagements_metadata_cc`, `engagements_metadata_bcc`.
  * A `meeting` engagement has a corresponding `engagements_metadata` object with non-null values in the `body`, `startTime`, `endTime`, and `title` columns.
  * A `note` engagement has a corresponding `engagements_metadata` object with non-null values in the `body` column.
  * A `task` engagement has a corresponding `engagements_metadata` object with non-null values in the `body`, `status`, and `forObjectType` columns.

2. The `engagements` stream uses two different APIs based on the length of time since the last sync and the number of records which Daspire hasn't yet synced.

  * `EngagementsRecent` if the following two criteria are met:
    * The last sync was performed within the last 30 days
    * Fewer than 10,000 records are being synced
  * `EngagementsAll` if either of these criteria are not met.

  Because of this, the `engagements` stream can be slow to sync if it hasn't synced within the last 30 days and/or is generating large volumes of new data. We therefore recommend scheduling frequent syncs.

## Performance considerations

1. Rate limiting

The integration is restricted by normal [HubSpot rate limitations](https://developers.hubspot.com/docs/api/usage-details).

## Troubleshooting

1. **Enabling streams:** Some streams, such as `workflows``, need to be enabled before they can be read using an integration authenticated using an API Key. If reading a stream that is not enabled, a log message returned to the output and the sync operation will only sync the other streams available.

Example of the output message when trying to read `workflows` stream with missing permissions for the API Key:
```
{
    "type": "LOG",
    "log": {
        "level": "WARN",
        "message": "Stream `workflows` cannot be proceed. This API Key (EXAMPLE_API_KEY) does not have proper permissions! (requires any of [automation-access])"
    }
}
```

2. **Unnesting top level properties:** Since version 1.5.0, in order to not make the users query their destinations for complicated json fields, we duplicate most of nested data as top level fields.

For instance:
```
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
```
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

3. **403 Forbidden Error**

  * Hubspot has **scopes** for each API call.

  * Each stream is tied to a scope and will need access to that scope to sync data.

  * Review the Hubspot OAuth scope documentation [here](https://developers.hubspot.com/docs/api/working-with-oauth#scopes).

  * Additional permissions:

      * `feedback_submissions`: Service Hub Professional account

      * `marketing_emails`: Market Hub Starter account

      * `workflows`: Sales, Service, and Marketing Hub Professional accounts

4. Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
