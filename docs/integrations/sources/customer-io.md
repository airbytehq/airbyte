# Customer.io

This page contains the setup guide and reference information for the Customer.io source connector.

The connector reads a Customer.io workspace through the [App API](https://docs.customer.io/integrations/api/app/): automations and their actions, one-time sends and their variants, API-triggered broadcasts and their actions, transactional message templates, sender identities, segments and their usage, subscription topics, object types, workspaces, reporting webhooks, snippets and collections, plus message deliveries, the activity log, people, segment memberships and email suppression lists. Stream names follow the App API, where automations are `campaigns` and one-time sends are `newsletters`. `messages` holds deliveries, one per message sent to one person.

## Prerequisites

- A Customer.io account in which you are an Account Admin, or a Member with the account-level **Manage API credentials** permission, to create the key
- An **App API Key** for the workspace you want to sync. Track API keys do not work.
- The **Region** of your Customer.io account, US or EU
- If your account restricts API access by IP address, the IP addresses Airbyte connects from on its allowlist

## Setup guide

### Step 1: Set up Customer.io

The connector authenticates with an App API key. Each key belongs to one workspace, and Customer.io shows it only once.

1. Check that you can manage API credentials: you need to be an Account Admin, or a Member with the account-level **Manage API credentials** permission ([Manage your API credentials](https://docs.customer.io/accounts/settings/managing-credentials/)).
2. In Customer.io, go to **Account Settings** > **API Credentials** ([Where can you find them?](https://docs.customer.io/accounts/settings/managing-credentials/#where-can-you-find-them)).
3. Add an App API key: give it a name and select the workspace you want to sync ([Adding new credentials](https://docs.customer.io/accounts/settings/managing-credentials/#adding-new-credentials)). Track API keys send data into a workspace and do not work here ([Track API Keys vs App API Keys](https://docs.customer.io/accounts/settings/managing-credentials/#track-api-keys-vs-app-api-keys)). If you restrict the key's scope, make sure it includes the data you want to sync ([Authentication](https://docs.customer.io/integrations/api/app/#authentication)).
4. Copy the key right away and store it somewhere safe: Customer.io shows App API keys only once ([App API Keys](https://docs.customer.io/accounts/settings/managing-credentials/#app-api-keys)).
5. Find your account's region, US or EU. Account Admins see it under **Settings** > **Account Settings** > **Data and Privacy**; other roles do not, so ask an Account Admin ([How do I know what region my data is in?](https://docs.customer.io/accounts/settings/data-centers/#how-do-i-know-what-region-my-data-is-in)). A wrong region fails the connection test with a 401 error.
6. If your account restricts API access by IP address, allow the addresses Airbyte connects from: the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) on Airbyte Cloud, or your deployment's public IP addresses on Self-Managed Airbyte. On the **Manage API Credentials** page, click **Add IP Address**, enter an address, select the workspace and click **Add IP Address**, once per address ([Restrict API access by IP Address](https://docs.customer.io/accounts/settings/managing-credentials/#restrict-api-access-by-ip-address)). Customer.io denies addresses missing from the list, even with a valid key.

### Step 2: Set up the Customer.io connector in Airbyte

1. In the Airbyte UI, go to **Sources** and click **+ New source**.
2. Select **Customer.io** from the list.
3. Enter a name for the source.
4. Fill in the fields below, then click **Set up source**. **Region**, **Start Date** and the other optional fields are under **Optional fields**; accounts in the EU region must set **Region**.

<FieldAnchor field="app_api_key">

**App API Key**: The App API key you created in Step 1 for the workspace you want to sync ([App API Keys](https://docs.customer.io/accounts/settings/managing-credentials/#app-api-keys)). Airbyte sends it as a bearer token. Track API keys do not work.

</FieldAnchor>

<FieldAnchor field="region">

**Region** (optional, required for EU accounts): The data center region of your Customer.io account, `US` (the default) or `EU`, which Account Admins see under **Settings** > **Account Settings** > **Data and Privacy**. The connector calls `https://api.customer.io/v1` or `https://api-eu.customer.io/v1`. Customer.io does not redirect App API requests to the other region, so a region that does not match your account fails with a 401 error ([Specifying your region in the API](https://docs.customer.io/accounts/settings/data-centers/#specifying-your-region-in-the-api)).

</FieldAnchor>

<FieldAnchor field="start_date">

**Start Date** (optional): A UTC date and time in the format `YYYY-MM-DDTHH:MM:SSZ`, for example `2023-01-01T00:00:00Z`. Only records created or last updated at or after it are synced, in every stream that supports incremental sync and in Full Refresh mode too: automations, actions, one-time sends, broadcasts, transactional message templates, segments, snippets and collections by their last update, `messages` by creation time and `activities` by event time. Streams that support only full refresh, such as `newsletter_variants`, `people`, `segment_memberships` and `esp_suppressions`, sync every record. Leave it blank to sync all records. See [Incremental sync and Start Date](#incremental-sync-and-start-date).

</FieldAnchor>

<FieldAnchor field="messages_lookback_days">

**Messages Lookback Window (Days)** (optional): How many days before the last synced message each incremental sync of `messages` reads again, so that opens, clicks, conversions, bounces and unsubscribes recorded after a message was sent reach the destination. Customer.io can record a conversion up to 90 days after a message is sent, opened or clicked ([conversions](https://docs.customer.io/messaging/send/automations/conversions/#how-it-works)), and records opens and clicks for up to 6 months ([delivery metrics](https://docs.customer.io/messaging/metrics/analytics/#delivery-metrics)). A longer window keeps these metrics more complete, but every sync then requests one page per 1,000 messages sent in the window. Enter 1 to 180 days. Defaults to 30.

</FieldAnchor>

<FieldAnchor field="esp_suppression_domains">

**Sending Domains for ESP Suppressions** (optional): The domains you send email from, in lowercase, for example `mail.example.com`. Customer.io lists them under **Settings** > **Workspace Settings** > **Email**. `esp_suppressions` reads each suppression list of Customer.io's email service provider (ESP) once per domain and records the domain on every row. Customer.io suppresses an address on the domain where it bounced or was reported as spam ([suppressions across domains](https://docs.customer.io/messaging/channels/email/deliverability/esp-suppression/#sync-suppressions-across-domains)), so if you send from more than one domain, enter them all. Leave it empty to read each list once without a domain filter; the `domain` column is then empty. Not needed if you send through your own SMTP server.

</FieldAnchor>

When you click **Set up source**, Airbyte tests the connection by reading automations (`campaigns`). If the test fails with a 401 or 403 error, see [Troubleshooting](#troubleshooting).

## Supported sync modes

The Customer.io source connector supports the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes):

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Namespaces | No |

Eleven streams support incremental sync; the other ten are full refresh only. No stream marks records deleted in Customer.io: see [Limitations & Troubleshooting](#limitations--troubleshooting).

## Supported Streams

New connections select the streams marked **Yes** under **Selected by default**; select the others when you need them.

| Stream | Customer.io resource | Primary key | Cursor | Sync modes | Selected by default |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `campaigns` | [Automations](https://docs.customer.io/integrations/api/app/tag/automations/listcampaigns/) | `id` | `updated` | Full Refresh, Incremental | Yes |
| `campaigns_actions` | [Automation actions](https://docs.customer.io/integrations/api/app/tag/automations/listcampaignactions/) | `id` | `updated`, per automation | Full Refresh, Incremental | Yes |
| `newsletters` | [One-time sends](https://docs.customer.io/integrations/api/app/tag/newsletters/listnewsletters/) | `id` | `updated` | Full Refresh, Incremental | Yes |
| `broadcasts` | [API-triggered broadcasts](https://docs.customer.io/integrations/api/app/tag/broadcasts/listbroadcasts/) | `id` | `updated` | Full Refresh, Incremental | Yes |
| `broadcast_actions` | [Broadcast actions](https://docs.customer.io/integrations/api/app/tag/broadcasts/broadcastactions/) | `broadcast_id`, `id` | `updated`, per broadcast | Full Refresh, Incremental | No |
| `newsletter_variants` | [One-time send variants](https://docs.customer.io/integrations/api/app/tag/newsletter-variants/listnewslettervariants/) | `newsletter_id`, `id` | None | Full Refresh | No |
| `transactional_messages` | [Transactional messages](https://docs.customer.io/integrations/api/app/tag/transactional/listtransactional/): templates, not deliveries | `id` | `updated_at` | Full Refresh, Incremental | Yes |
| `sender_identities` | [Sender identities](https://docs.customer.io/integrations/api/app/tag/sender-identities/listsenders/) | `id` | None | Full Refresh | No |
| `segments` | [Segments](https://docs.customer.io/integrations/api/app/tag/segments/listsegments/) | `id` | `updated_at` | Full Refresh, Incremental | Yes |
| `segment_usage` | [Segment dependencies](https://docs.customer.io/integrations/api/app/tag/segments/getsegmentdependencies/) | `segment_id` | None | Full Refresh | No |
| `subscription_topics` | [Subscription topics](https://docs.customer.io/integrations/api/app/tag/subscription-center/gettopics/) | `id` | None | Full Refresh | No |
| `object_types` | [Object types](https://docs.customer.io/integrations/api/app/tag/objects/getobjecttypes/) | `id` | None | Full Refresh | No |
| `workspaces` | [Workspaces](https://docs.customer.io/integrations/api/app/tag/workspaces/listworkspaces/) | `id` | None | Full Refresh | No |
| `reporting_webhooks` | [Reporting webhooks](https://docs.customer.io/integrations/api/app/tag/reporting-webhooks/listwebhooks/) | `id` | None | Full Refresh | No |
| `snippets` | [Snippets](https://docs.customer.io/integrations/api/app/tag/snippets/listsnippets/) | `name` | `updated_at` | Full Refresh, Incremental | No |
| `collections` | [Collections](https://docs.customer.io/integrations/api/app/tag/collections/getcollections/) | `id` | `updated_at` | Full Refresh, Incremental | No |
| `messages` | [Messages](https://docs.customer.io/integrations/api/app/tag/messages/listmessages/): deliveries | `id` | `created` | Full Refresh, Incremental | No (personal data) |
| `activities` | [Activities](https://docs.customer.io/integrations/api/app/tag/activities/listactivities/) | `id` | `timestamp` | Full Refresh, Incremental | No (personal data) |
| `people` | [Customers](https://docs.customer.io/integrations/api/app/tag/customers/getpeoplefilter/) with their [attributes and devices](https://docs.customer.io/integrations/api/app/tag/customers/getpeoplebyid/) | `cio_id` | None | Full Refresh | No (personal data) |
| `segment_memberships` | [Customers in a segment](https://docs.customer.io/integrations/api/app/tag/segments/getsegmentmembership/) | `segment_id`, `cio_id` | None | Full Refresh | No (personal data) |
| `esp_suppressions` | [ESP-suppressed emails](https://docs.customer.io/integrations/api/app/tag/esp-suppression/getsuppressionbytype/) | `suppression_type`, `domain`, `email` | None | Full Refresh | No (personal data) |

`reporting_webhooks` syncs each webhook's `endpoint` URL as Customer.io returns it. Customer.io documents basic authentication in the URL (`http://username:password@example.com`) as a way to secure a reporting webhook ([webhooks FAQ](https://docs.customer.io/integrations/data-out/connections/webhooks/#frequently-asked-questions)), so the URL can contain the receiving service's credentials. New connections leave the stream unselected; select it only if the destination may store them. A connection set up before 0.7.0 with **Propagate all field and stream changes** selects it on its own and syncs it in its first sync on 0.7.0 or later. To prevent that, switch the connection to **Propagate field changes only** before the upgrade; otherwise deselect the stream and delete its data from the destination.

`workspaces` lists every workspace in the account with message counts for the current billing period and current people and object totals, cached by Customer.io for up to two hours. The records have no update time, so use Full Refresh | Overwrite for the latest counts, or Full Refresh | Append to keep one snapshot per sync.

`collections` lists each collection's name, schema, row count and size, not its contents.

`messages` has one record per delivery, a message sent to one person, with the time each metric (delivered, opened, clicked, converted and more) was recorded. Syncs read deliveries in 30-day windows of creation time, one request per 1,000 deliveries, and Start Date applies to the creation time. Customer.io records opens and clicks for up to 6 months and conversions for up to 90 days, so each incremental sync reads the deliveries created in the last **Messages Lookback Window (Days)** again (default 30, up to 180): use Incremental | Append + Deduped. Raise the setting, or run a full refresh from time to time, for complete metrics; lower it to shorten syncs in high-volume workspaces. Records carry the recipient's address and identifiers, the subject line and per-person open and click times.

`activities` is the workspace activity log, one record per event: message events such as sent, opened and clicked, tracked events, page and screen views, and attribute changes, including those of deleted people. Customer.io guarantees only the last 30 days, so sync at least every 30 days and use Incremental | Append + Deduped to keep older history. Expect several records per message sent; the first sync reads every retained activity, 100 per request. Incremental syncs skip events sent to Customer.io with a timestamp more than an hour before the newest activity already synced. If a page of 100 such older events comes before newer ones in Customer.io's list, the newer ones are skipped too. Records carry email addresses, your person IDs, IP addresses and user agents of opens and clicks, event and attribute values, and page URLs.

`people` has one record per person, keyed by `cio_id`, the ID Customer.io assigns to every person, with every profile attribute, identifier, subscription preference and device push token. Each sync reads every profile, one request per 1,000 people to find them and one per 100 to fetch them: 1,000,000 people take about 11,000 requests, at least 18 minutes at 10 requests per second. Start Date does not apply. Full Refresh | Overwrite mirrors the workspace; Append keeps deleted people.

`segment_memberships` has one record per person per segment with the person's `cio_id`, ID and email address, so it holds the sum of all segment sizes, often several times the number of people, at up to 30,000 members per request. Membership has no timestamps, so use Full Refresh | Overwrite: Append adds a full copy on every sync. Members of a segment whose `state` is `build` can be out of date while Customer.io calculates them. Archived segments are not included.

`esp_suppressions` has one record per address on each of Customer.io's email suppression lists (bounces, blocks, spam reports, invalid emails), with a reason that can repeat the address. Each sync makes one request per 1,000 addresses on each list, at least 4 (4 per configured domain). Lifted suppressions leave the list without a record, so use Full Refresh | Overwrite: Append adds a full copy on every sync. Customer.io suppresses an address on the sending domain where it bounced or was reported as spam, so if you send from more than one domain, enter them in **Sending Domains for ESP Suppressions**: each list is then read once per domain, and records carry their `domain`. A mistyped or unknown domain returns no records instead of an error. The lists can include addresses suppressed by other workspaces that send from the same domain. If you send through your own SMTP server, your email provider keeps the suppressions, so deselect the stream.

`messages`, `activities`, `people`, `segment_memberships` and `esp_suppressions` carry personal data and are not selected by default. A connection set up before 0.8.0 with **Propagate all field and stream changes** selects them on its own and syncs them in its first sync on 0.8.0 or later. To prevent that, switch the connection to **Propagate field changes only** before the upgrade; otherwise deselect the streams and delete their data from the destination. Incremental and Append syncs keep rows of people later deleted or suppressed in Customer.io, so handle erasure requests in the destination too. If these streams fail with a 403 error, check that the key can read this data and that the Airbyte IP addresses are on your allowlist, or deselect the streams.

## Incremental sync and Start Date

Of the lists the connector reads, only deliveries can be filtered by time, so `messages` is the one stream Customer.io filters on the server. The other incremental streams use client-side cursors: each sync reads the full list (`activities` stops early, see below) and emits the records whose cursor (`updated`, `updated_at` or `timestamp`, in Unix seconds) is at or after the saved cursor minus one hour. The lists are not sorted by the cursor, so a record edited during a sync can fall behind the saved cursor; the one-hour lookback picks it up on the next sync. The lookback costs no extra requests, because every sync reads the full lists anyway; `activities` reads one more hour of activities. Records updated in the hour before the saved cursor are emitted again on every sync until a newer change moves the cursor, so use Incremental | Append + Deduped: Incremental | Append stores them as repeated rows. Both modes make the same requests for these streams: Incremental | Append + Deduped writes fewer rows, and Full Refresh | Overwrite also removes records deleted in Customer.io.

`campaigns_actions` and `broadcast_actions` keep one cursor per automation or broadcast. They request the actions of every automation or broadcast, including those last updated before the Start Date, because a parent's update time does not change with its actions; the actions themselves are still filtered by the Start Date. The actions of an automation or broadcast added since the last sync start from the newest update time saved for the stream, less the previous sync's duration and the one-hour lookback, not from the Start Date. Actions that keep an older update time arrive only after they change. This can affect a duplicated automation: Customer.io does not document whether copied actions keep their update time.

`messages` reads 30-day windows of creation time, and each incremental sync starts **Messages Lookback Window (Days)** before the newest `created` already synced, so metrics recorded after sending reach the destination. `activities` reads newest first and stops at the first page with no activity inside the cursor window, and Customer.io guarantees only the last 30 days of activity. The notes on both streams under [Supported Streams](#supported-streams) describe the trade-offs.

Start Date applies to the streams that support incremental sync, in Full Refresh mode too: they skip records created or last updated before it, by creation time for `messages` and event time for `activities`. The ten full refresh streams ignore it and sync every record. A future Start Date passes the connection check, but until that date a sync emits only records changed while it runs. Leave it blank to sync all records.

### Performance considerations

Customer.io limits most App API endpoints to 10 requests per second per workspace ([Rate Limits](https://docs.customer.io/integrations/api/app/#rate-limits)), from one bucket that every App API call in the workspace without a separate limit draws from, writes included ([OpenAPI spec](https://docs.customer.io/files/journeys-app.json), `components.responses.InboxPreviewReadRateLimited`). The connector shares that bucket with your other App API traffic. It caps itself at 10 requests per rolling second across all streams and reads with three workers. When other traffic fills the bucket, Customer.io answers with 429 errors and the connector waits; see [Troubleshooting](#troubleshooting).

Request costs of the expensive streams:

- `campaigns_actions`, `broadcast_actions`, `newsletter_variants` and `segment_usage`: one request per automation, broadcast, one-time send or segment, plus one per extra page of actions. 1,000 one-time sends add about 100 seconds of `newsletter_variants` requests.
- `messages`: one request per 1,000 deliveries, plus one per 30-day window. 10 million deliveries take about 10,000 requests on the first sync, and every incremental sync reads the lookback window again. With a blank Start Date, about 690 empty windows since 1970 add about 70 seconds to the first sync, and to every sync while the workspace has no deliveries.
- `activities`: one request per 100 activities, one page after another: about 10,000 requests per million activities on the first sync. Incremental syncs read the new activities plus one page.
- `people`: one request per 1,000 people plus one per 100: 1,000,000 people take about 11,000 requests, at least 18 minutes.
- `segment_memberships`: one request per segment and per 30,000 members: 10 million memberships in 200 segments take at most about 735 requests.
- `esp_suppressions`: one request per 1,000 addresses on each of the four suppression lists, at least 4, times the number of configured domains.

Leave the streams you do not need unselected.

## Limitations & Troubleshooting

### Connector limitations

How the connector treats Customer.io HTTP errors:

| HTTP status | Behavior |
| :--- | :--- |
| 401 | The sync fails with a configuration error: Customer.io rejected the key. See [Troubleshooting](#troubleshooting). |
| 403 | The sync fails with a configuration error: Customer.io denied the key access to the data. See [Troubleshooting](#troubleshooting). |
| 404 | On `campaigns_actions`, `broadcast_actions`, `newsletter_variants`, `segment_usage` and `segment_memberships`, the records of an automation, broadcast, one-time send or segment deleted during the sync are skipped. On other streams, the sync fails. |
| 429 | Retried up to 30 times after the wait in the `Retry-After` header; with `Retry-After: 1`, that rides out about a minute of rate limiting. Customer.io leaves the header out when a daily quota is reached; the connector then backs off exponentially and fails the sync after about 17 minutes. |
| 500, 502, 503, 504 | Retried with exponential backoff; the sync fails after about 17 minutes of errors. |

- **Deletions**: Customer.io's lists leave deleted records out, so no stream marks a deletion. In Incremental and Append modes, a record deleted in Customer.io keeps its last version in the destination; Full Refresh | Overwrite mirrors the current state when Start Date is blank; with a Start Date it keeps only records last updated since then. `snippets` are keyed by `name`, and a snippet cannot be renamed, so a snippet copied to a new name arrives as a new record, and deleting the old one leaves its last version like any deleted record.
- **Archived segments**: Customer.io leaves [archived segments](https://docs.customer.io/messaging/segmentation/segments/#archive-unarchive-a-segment) out of its segment list, so `segments`, `segment_usage` and `segment_memberships` skip them. A segment archived after an incremental sync keeps its last row in the destination. A segment can be archived while archived automations or sent one-time sends still use it, and that usage never reaches `segment_usage`.
- **Deprecated fields**: Customer.io's [OpenAPI spec](https://docs.customer.io/files/journeys-app.json) marks `campaigns.type`, the trigger type ("Sunsetting on March 30, 2025"), and `campaigns.msg_templates` as deprecated, so they may arrive null or stop arriving. Do not build new reports on them.
- **Field types that differ from the API reference**: `campaigns_actions.id` is a string, as Customer.io sends it, although the reference documents an integer, and `campaigns.actions[].id` is an integer, so cast one side to join them. `broadcast_actions.id` is cast to the documented integer. The `campaigns` fields `audience.person_filters`, `audience.relationship_filters`, `object_attribute_triggers` and `relationship_attribute_triggers` have no declared type: the reference types them as objects, but its examples show JSON strings. `messages` also carries `transactional_message_id` and `msg_template_id`, which the reference's response schema does not declare. Version 1.0.0 changed the declared types of `campaigns_actions.from_id` and `reply_to_id`, `newsletters.sent_at` and four ID and tag arrays; see the [migration guide](./customer-io-migrations.md).
- **Joins**: `object_types.id` is a string, because Customer.io passes object type IDs as strings, while `campaigns.object_type_id` is an integer, so that join needs a cast.
- **Variants**: `broadcast_actions` has one record per language variant of a message, all with the same `multi_language_branch_action_id`, and `newsletter_variants` one per language or A/B test of a one-time send, each with its own `id`.
- **Hidden senders**: `sender_identities` includes hidden senders; use `hidden` to tell them apart.
- **Collection counts**: Customer.io does not document whether replacing a collection's contents changes its `updated_at`. If it does not, incremental syncs keep the old `rows`, `bytes` and `schema`; Full Refresh | Overwrite always has the current values of the collections it syncs.
- **Empty streams**: `subscription_topics` is empty until the workspace has subscription topics, and a non-empty stream does not mean the subscription center is enabled. `broadcasts` and `broadcast_actions` are empty without API-triggered broadcasts, and `activities` can be empty after 30 days without activity.
- **Deliveries without content**: a `messages` record with `forgotten: true` is one whose content Customer.io did not keep, for example a transactional message sent with message retention disabled.
- **Log warning**: `campaigns_actions` logs "Parent state handling is not supported for CartesianProductStreamSlicer." on every sync. It is harmless and needs no action.

### Troubleshooting

- **401 errors**: Customer.io rejected the key. Check that it is an App API key, not a Track API key, and that you copied all of it; Customer.io shows a key only once, so create a new one if you lost it. Check that **Region** matches your account (see [Step 1](#step-1-set-up-customerio)). If your account restricts API access by IP address, add the addresses Airbyte connects from to the allowlist ([Step 1](#step-1-set-up-customerio)): Customer.io does not document which error a blocked address gets, so both the 401 and the 403 messages mention it.
- **403 errors**: Customer.io denied the key access to the data the stream reads, or the addresses Airbyte connects from are not on the allowlist. Use a key that can read the data, or deselect the stream.
- **429 errors or slow syncs**: your other App API traffic shares the 10 requests per second. Schedule syncs when that traffic is low, sync less often, or deselect the expensive streams listed in [Performance considerations](#performance-considerations).
- **5xx errors**: temporary Customer.io errors. If the sync fails after the retries, check [Customer.io Status](https://status.customerio.com/) and sync again later.
- **Records missing from incremental streams**: streams that support incremental sync skip records last updated before the Start Date, `activities` skips events dated more than an hour before the newest activity already synced, and the actions of a new automation or broadcast start from the newest update time saved for the stream (see [Incremental sync and Start Date](#incremental-sync-and-start-date)). To read them, move the Start Date earlier or leave it blank, then clear the stream; the clear also removes the rows of records deleted in Customer.io and, in Append modes, earlier versions of each record. Do not clear `activities`: Customer.io guarantees only the last 30 days, so the clear permanently removes older activity from the destination.
- **Repeated rows**: in Incremental | Append mode, records updated in the hour before the saved cursor arrive again on every sync, and `messages` repeats its lookback window. Use Incremental | Append + Deduped.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                   | Subject                                     |
|:--------|:-----------| :------------------------------------------------------------- |:--------------------------------------------|
| 1.0.0 | 2026-10-09 | [88159](https://github.com/airbytehq/airbyte/pull/88159) | Declare `from_id`, `reply_to_id` and `sent_at` as integers and the item types of four ID and tag arrays |
| 0.8.0 | 2026-10-08 | [88158](https://github.com/airbytehq/airbyte/pull/88158) | Add message, activity, people, segment membership and ESP suppression streams |
| 0.7.0 | 2026-10-08 | [88135](https://github.com/airbytehq/airbyte/pull/88135) | Add subscription topic, object type, workspace, reporting webhook, snippet and collection streams |
| 0.6.0 | 2026-10-07 | [88130](https://github.com/airbytehq/airbyte/pull/88130) | Add broadcast, newsletter variant, transactional message, sender identity and segment streams |
| 0.5.0 | 2026-10-07 | [88129](https://github.com/airbytehq/airbyte/pull/88129) | Add rate limiting, Retry-After retries, clearer authentication errors, a one-hour lookback, and missing fields |
| 0.4.17 | 2026-10-06 | [87812](https://github.com/airbytehq/airbyte/pull/87812) | Update dependencies |
| 0.4.16 | 2026-09-29 | [87129](https://github.com/airbytehq/airbyte/pull/87129) | Update dependencies |
| 0.4.15 | 2026-09-22 | [86584](https://github.com/airbytehq/airbyte/pull/86584) | Update dependencies |
| 0.4.14 | 2026-09-15 | [85996](https://github.com/airbytehq/airbyte/pull/85996) | Update dependencies |
| 0.4.13 | 2026-09-08 | [85433](https://github.com/airbytehq/airbyte/pull/85433) | Update dependencies |
| 0.4.12 | 2026-08-18 | [84549](https://github.com/airbytehq/airbyte/pull/84549) | Update dependencies |
| 0.4.11 | 2026-08-11 | [83899](https://github.com/airbytehq/airbyte/pull/83899) | Update dependencies |
| 0.4.10 | 2026-08-04 | [83394](https://github.com/airbytehq/airbyte/pull/83394) | Update dependencies |
| 0.4.9 | 2026-07-28 | [82865](https://github.com/airbytehq/airbyte/pull/82865) | Update dependencies |
| 0.4.8 | 2026-07-21 | [82368](https://github.com/airbytehq/airbyte/pull/82368) | Update dependencies |
| 0.4.7 | 2026-07-14 | [81795](https://github.com/airbytehq/airbyte/pull/81795) | Update dependencies |
| 0.4.6 | 2026-06-30 | [81036](https://github.com/airbytehq/airbyte/pull/81036) | Update dependencies |
| 0.4.5 | 2026-06-23 | [80394](https://github.com/airbytehq/airbyte/pull/80394) | Update dependencies |
| 0.4.4 | 2026-06-16 | [79829](https://github.com/airbytehq/airbyte/pull/79829) | Update dependencies |
| 0.4.3 | 2026-06-09 | [79257](https://github.com/airbytehq/airbyte/pull/79257) | Update dependencies |
| 0.4.2 | 2026-06-02 | [78639](https://github.com/airbytehq/airbyte/pull/78639) | Update dependencies |
| 0.4.1 | 2026-05-08 | [77895](https://github.com/airbytehq/airbyte/pull/77895) | Upgrade the base image to source-declarative-manifest 7.18.1 |
| 0.4.0 | 2026-05-08 | [77819](https://github.com/airbytehq/airbyte/pull/77819) | Add pagination, incremental sync, and EU region support |
| 0.3.19  | 2025-08-20 | [65113](https://github.com/airbytehq/airbyte/pull/65113) | Update logo                                 |
| 0.3.18  | 2025-05-10 | [60049](https://github.com/airbytehq/airbyte/pull/60049) | Update dependencies                         |
| 0.3.17  | 2025-05-03 | [58875](https://github.com/airbytehq/airbyte/pull/58875) | Update dependencies                         |
| 0.3.16  | 2025-04-19 | [57766](https://github.com/airbytehq/airbyte/pull/57766) | Update dependencies                         |
| 0.3.15  | 2025-04-05 | [57225](https://github.com/airbytehq/airbyte/pull/57225) | Update dependencies                         |
| 0.3.14  | 2025-03-29 | [56546](https://github.com/airbytehq/airbyte/pull/56546) | Update dependencies                         |
| 0.3.13  | 2025-03-22 | [55918](https://github.com/airbytehq/airbyte/pull/55918) | Update dependencies                         |
| 0.3.12  | 2025-03-08 | [55311](https://github.com/airbytehq/airbyte/pull/55311) | Update dependencies                         |
| 0.3.11  | 2025-03-01 | [54942](https://github.com/airbytehq/airbyte/pull/54942) | Update dependencies                         |
| 0.3.10  | 2025-02-22 | [54374](https://github.com/airbytehq/airbyte/pull/54374) | Update dependencies                         |
| 0.3.9   | 2025-02-15 | [51670](https://github.com/airbytehq/airbyte/pull/51670) | Update dependencies                         |
| 0.3.8   | 2025-01-11 | [51062](https://github.com/airbytehq/airbyte/pull/51062) | Update dependencies                         |
| 0.3.7   | 2025-01-04 | [50582](https://github.com/airbytehq/airbyte/pull/50582) | Update dependencies                         |
| 0.3.6   | 2024-12-21 | [49999](https://github.com/airbytehq/airbyte/pull/49999) | Update dependencies                         |
| 0.3.5   | 2024-12-14 | [49490](https://github.com/airbytehq/airbyte/pull/49490) | Update dependencies                         |
| 0.3.4   | 2024-12-12 | [48923](https://github.com/airbytehq/airbyte/pull/48923) | Update dependencies                         |
| 0.3.3   | 2024-11-04 | [48225](https://github.com/airbytehq/airbyte/pull/48225) | Update dependencies                         |
| 0.3.2   | 2024-10-28 | [47464](https://github.com/airbytehq/airbyte/pull/47464) | Update dependencies                         |
| 0.3.1   | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version    |
| 0.3.0   | 2024-08-15 | [44158](https://github.com/airbytehq/airbyte/pull/44158) | Refactor connector to manifest-only format  |
| 0.2.15  | 2024-08-12 | [43889](https://github.com/airbytehq/airbyte/pull/43889) | Update dependencies                         |
| 0.2.14  | 2024-08-10 | [43513](https://github.com/airbytehq/airbyte/pull/43513) | Update dependencies                         |
| 0.2.13  | 2024-08-03 | [43185](https://github.com/airbytehq/airbyte/pull/43185) | Update dependencies                         |
| 0.2.12  | 2024-07-27 | [42631](https://github.com/airbytehq/airbyte/pull/42631) | Update dependencies                         |
| 0.2.11  | 2024-07-20 | [42219](https://github.com/airbytehq/airbyte/pull/42219) | Update dependencies                         |
| 0.2.10  | 2024-07-13 | [41808](https://github.com/airbytehq/airbyte/pull/41808) | Update dependencies                         |
| 0.2.9   | 2024-07-10 | [41389](https://github.com/airbytehq/airbyte/pull/41389) | Update dependencies                         |
| 0.2.8   | 2024-07-09 | [41225](https://github.com/airbytehq/airbyte/pull/41225) | Update dependencies                         |
| 0.2.7   | 2024-07-06 | [40883](https://github.com/airbytehq/airbyte/pull/40883) | Update dependencies                         |
| 0.2.6   | 2024-06-29 | [40624](https://github.com/airbytehq/airbyte/pull/40624) | Update dependencies                         |
| 0.2.5 | 2024-06-27 | [38318](https://github.com/airbytehq/airbyte/pull/38318) | Make the connector compatible with Connector Builder |
| 0.2.4   | 2024-06-25 | [40369](https://github.com/airbytehq/airbyte/pull/40369) | Update dependencies                         |
| 0.2.3   | 2024-06-22 | [39953](https://github.com/airbytehq/airbyte/pull/39953) | Update dependencies                         |
| 0.2.2   | 2024-06-04 | [38980](https://github.com/airbytehq/airbyte/pull/38980) | [autopull] Upgrade base image to v1.2.1     |
| 0.2.1   | 2024-05-31 | [38812](https://github.com/airbytehq/airbyte/pull/38812) | [autopull] Migrate to base image and poetry |
| 0.2.0 | 2023-08-29 | [29385](https://github.com/airbytehq/airbyte/pull/29385) | Migrate TS CDK to Low code |
| 0.1.23 | 2021-11-09 | 126 | Add Customer.io source |

</details>
