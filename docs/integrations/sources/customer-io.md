# Customer.io

<HideInUI>

This page contains the setup guide and reference information for the [Customer.io](https://customer.io/) source connector.

</HideInUI>

The Customer.io source connector uses the [Customer.io App API](https://docs.customer.io/integrations/api/app/) to sync data from one Customer.io workspace. It syncs messaging configuration, such as automations, one-time sends, broadcasts, transactional message templates, sender identities, segments, snippets, and collections. It can also sync end-user data: message deliveries, the activity log, people profiles, segment memberships, and email suppression lists.

:::info
Version 1.0.0 changes the declared types of fields in the `campaigns`, `campaigns_actions`, and `newsletters` streams. If you sync any of them, follow the [migration guide](/integrations/sources/customer-io-migrations#upgrading-to-100) before your first sync on 1.0.0.
:::

## Prerequisites

- A Customer.io App API key for the workspace you want to sync. Track API keys don't work with this connector.
- The Account Admin role, or the account-level **Manage API credentials** permission, to create or view API keys in Customer.io.
- The data center region of your Customer.io account: US or EU.

## Setup guide

### Step 1: Create a Customer.io App API key

1. In Customer.io, go to **Account Settings** > **API Credentials**.
2. Create an App API key for the workspace you want to sync. If you restrict the key's scope, make sure it includes the data you want to sync.
3. Copy the key right away and store it securely. Customer.io shows App API keys only once.

For more information, see Customer.io's [API credentials](https://docs.customer.io/accounts/settings/managing-credentials/) documentation.

### Step 2: Find your account region

If you're an Account Admin, your account region appears in Customer.io under **Settings** > **Account Settings** > **Data and Privacy**. Customer.io doesn't redirect App API requests between regions, so a key used against the wrong region fails with a `401` error. For more information, see [Account regions](https://docs.customer.io/accounts/settings/data-centers/).

### Step 3: Set up the Customer.io source in Airbyte

<FieldAnchor field="app_api_key">

1. For **App API Key**, enter the key you created in Step 1.

</FieldAnchor>

<FieldAnchor field="region">

1. For **Region**, select **US** or **EU** to match your Customer.io account. The default is **US**.

</FieldAnchor>

<FieldAnchor field="start_date">

1. (Optional) For **Start Date**, enter a UTC date and time in the format `YYYY-MM-DDTHH:MM:SSZ`. Incremental streams only emit records at or after this date. The date is compared with the creation time for `messages`, the event time for `activities`, and the last update time for the other incremental streams. Full-refresh-only streams ignore it. Leave it blank to sync all records.

</FieldAnchor>

<FieldAnchor field="messages_lookback_days">

1. (Optional) For **Messages Lookback Window (Days)**, enter how many days of deliveries each incremental sync of the `messages` stream reads again, from 1 to 180. The default is 30. See [`messages`](#messages) for how to choose a value.

</FieldAnchor>

<FieldAnchor field="esp_suppression_domains">

1. (Optional) For **Sending Domains for ESP Suppressions**, enter each domain you send email from, in lowercase, for example `mail.example.com`. Customer.io lists your sending domains under **Settings** > **Workspace Settings** > **Email**. Only the `esp_suppressions` stream uses this field. See [`esp_suppressions`](#esp_suppressions) for details.

</FieldAnchor>

1. Select **Set up source**. Airbyte tests the connection by reading the `campaigns` stream.

## Supported sync modes

The Customer.io source connector supports the following [sync modes](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/):

- Full Refresh | Overwrite
- Full Refresh | Append
- Incremental | Append
- Incremental | Append + Deduped

Incremental sync is available only for streams that have a cursor field in the following table.

## Supported streams

| Stream | Customer.io endpoint | Primary key | Cursor field |
| :--- | :--- | :--- | :--- |
| `campaigns` | [List automations](https://docs.customer.io/integrations/api/app/tag/automations/listcampaigns/) | `id` | `updated` |
| `campaigns_actions` | [List automation actions](https://docs.customer.io/integrations/api/app/tag/automations/listcampaignactions/) | `id` | `updated` |
| `newsletters` | [List one-time sends](https://docs.customer.io/integrations/api/app/tag/newsletters/listnewsletters/) | `id` | `updated` |
| `newsletter_variants` | [List one-time send variants](https://docs.customer.io/integrations/api/app/tag/newsletter-variants/listnewslettervariants/) | `newsletter_id`, `id` | None |
| `broadcasts` | [List broadcasts](https://docs.customer.io/integrations/api/app/tag/broadcasts/listbroadcasts/) | `id` | `updated` |
| `broadcast_actions` | [List broadcast actions](https://docs.customer.io/integrations/api/app/tag/broadcasts/broadcastactions/) | `broadcast_id`, `id` | `updated` |
| `transactional_messages` | [List transactional messages](https://docs.customer.io/integrations/api/app/tag/transactional/listtransactional/) | `id` | `updated_at` |
| `sender_identities` | [List sender identities](https://docs.customer.io/integrations/api/app/tag/sender-identities/listsenders/) | `id` | None |
| `segments` | [List segments](https://docs.customer.io/integrations/api/app/tag/segments/listsegments/) | `id` | `updated_at` |
| `segment_usage` | [Get a segment's dependencies](https://docs.customer.io/integrations/api/app/tag/segments/getsegmentdependencies/) | `segment_id` | None |
| `subscription_topics` | [List subscription topics](https://docs.customer.io/integrations/api/app/tag/subscription-center/gettopics/) | `id` | None |
| `object_types` | [List object types](https://docs.customer.io/integrations/api/app/tag/objects/getobjecttypes/) | `id` | None |
| `workspaces` | [List workspaces](https://docs.customer.io/integrations/api/app/tag/workspaces/listworkspaces/) | `id` | None |
| `reporting_webhooks` | [List reporting webhooks](https://docs.customer.io/integrations/api/app/tag/reporting-webhooks/listwebhooks/) | `id` | None |
| `snippets` | [List snippets](https://docs.customer.io/integrations/api/app/tag/snippets/listsnippets/) | `name` | `updated_at` |
| `collections` | [List your collections](https://docs.customer.io/integrations/api/app/tag/collections/getcollections/) | `id` | None |
| `messages` | [List messages](https://docs.customer.io/integrations/api/app/tag/messages/listmessages/) | `id` | `created` |
| `activities` | [List activities](https://docs.customer.io/integrations/api/app/tag/activities/listactivities/) | `id` | `timestamp` |
| `people` | [Search for customers](https://docs.customer.io/integrations/api/app/tag/customers/getpeoplefilter/), then [List customers, attributes, and devices](https://docs.customer.io/integrations/api/app/tag/customers/getpeoplebyid/) | `cio_id` | None |
| `segment_memberships` | [List customers in a segment](https://docs.customer.io/integrations/api/app/tag/segments/getsegmentmembership/) | `segment_id`, `cio_id` | None |
| `esp_suppressions` | [Get ESP-suppressed emails by type](https://docs.customer.io/integrations/api/app/tag/esp-suppression/getsuppressionbytype/) | `suppression_type`, `domain`, `email` | None |

New connections select `campaigns`, `campaigns_actions`, `newsletters`, `broadcasts`, `segments`, and `transactional_messages` by default.

### Personal data streams

`messages`, `activities`, `people`, `segment_memberships`, and `esp_suppressions` contain data about the people you message, such as email addresses, identifiers, and profile attributes. New connections leave these streams unselected.

- **Upgrading:** Connections set to **Propagate all field and stream changes** add these five streams and sync them automatically after upgrading to version 0.8.0. To stop syncing them, deselect the streams and clear their data from the destination.
- **Deletion requests:** Customer.io removes or anonymizes data when you delete or suppress a person, but rows already synced to your destination keep the original values. Incremental and Append syncs also keep rows for people who no longer exist in Customer.io. Handle erasure requests in the destination too.

### Stream details

- **Naming:** The Customer.io UI calls campaigns "automations" and newsletters "one-time sends." The API and this connector use `campaigns` and `newsletters`.
- **`broadcasts`** contains only API-triggered broadcasts.
- **`transactional_messages`** contains transactional message templates. Individual transactional deliveries are in `messages`.
- **Child streams:** `campaigns_actions`, `newsletter_variants`, `broadcast_actions`, `segment_usage`, and `segment_memberships` read their parent list, then make requests for each parent record. If a parent is deleted between those requests, Customer.io returns a `404` error and the connector skips that parent instead of failing the sync.
- **`newsletter_variants` and `broadcast_actions`** contain one record per language variant of a multi-language message. `newsletter_variants` also contains one record per A/B test variant.
- **`sender_identities`** contains both visible and hidden senders.
- **ID and time fields:** `campaigns_actions.from_id` and `campaigns_actions.reply_to_id` join to `sender_identities.id`. `campaigns.trigger_segment_ids` holds `segments.id` values, and `newsletters.content_ids` holds `newsletter_variants.id` values. `newsletters.sent_at` is the Unix time, in seconds, of the one-time send's last send.
- **`segments`, `segment_usage`, and `segment_memberships`** don't include archived segments. `segment_usage` contains one record per segment, listing the automations and one-time sends that use it.
- **`subscription_topics`** is empty until you add topics to your workspace's [subscription center](https://docs.customer.io/messaging/channels/subscriptions/center/). `newsletters.subscription_topic_id` joins to `subscription_topics.id`.
- **`object_types`**: `id` is a string, while `campaigns.object_type_id` is an integer. Cast one of them to join the two streams.
- **`workspaces`** lists every workspace in your Customer.io account, not only the workspace the API key belongs to. Message counts cover the current billing period, and people and object counts are current totals. Customer.io caches these counts for up to two hours. The records have no update time, so use Full Refresh | Overwrite for the latest counts, or Full Refresh | Append to keep one snapshot per sync.
- **`reporting_webhooks`** syncs each webhook's `endpoint` URL with any `username:password@` part removed. A token in the URL's path or query string is synced as Customer.io returns it. See the [reporting webhooks FAQ](https://docs.customer.io/integrations/data-out/connections/webhooks/#frequently-asked-questions). New connections leave this stream unselected. Connections set to **Propagate all field and stream changes** add and sync it automatically after upgrading to version 0.7.0. To stop syncing it, deselect the stream and clear its data from the destination.
- **`snippets`** have no ID. Customer.io identifies snippets by their unique name, so a snippet copied to a new name arrives as a new record.
- **`collections`** contains each collection's name, schema, row count, and size, not the collection's contents.

#### `messages`

`messages` contains one record per delivery, which is one message sent to one person, across all channels. Drafts aren't included. Each record includes the recipient's address and identifiers, the subject line, and a `metrics` object with the time each metric, such as delivered, opened, clicked, or converted, was recorded.

Metrics keep changing after a delivery is created. Customer.io records opens and clicks for up to 6 months after sending, and conversions for up to 90 days. To pick up these changes, each incremental sync reads again the deliveries created in the last **Messages Lookback Window (Days)** before the newest delivery already synced. Use **Incremental | Append + Deduped** so each delivery keeps only its latest version.

- Raise the lookback window, or run a full refresh from time to time, to keep metrics complete for older deliveries.
- Lower the lookback window to shorten syncs in high-volume workspaces. Each sync makes one request per 1,000 deliveries created in the window.
- **Start Date** applies to the delivery's creation time. A delivery created before the Start Date is never synced, even if it's opened later.

#### `activities`

`activities` is the workspace activity log, with one record per event: message events such as sent, opened, and clicked, tracked events, page and screen views, and attribute changes. It includes the activity of deleted people. Records can include email addresses, your person IDs, IP addresses and user agents of opens and clicks, event and attribute values, and page URLs. Expect several records for each message sent.

Customer.io only guarantees [the last 30 days of activity](https://docs.customer.io/integrations/api/app/tag/activities/listactivities/). To keep a longer history, sync at least every 30 days with **Incremental | Append + Deduped**. A connection that goes longer than 30 days between syncs can lose the activity in that gap.

The endpoint has no time filter, so the first sync reads every retained activity, 100 per request. Customer.io lists activities newest first, so incremental syncs stop reading at the first page with no activity newer than the saved cursor minus one hour. As a result:

- Incremental syncs skip events sent to Customer.io with a timestamp more than an hour before the newest activity already synced, such as backdated events.
- If a full page of 100 such older events comes before newer events in Customer.io's list, the sync stops there and the newer events are skipped too.

#### `people`

`people` contains one record per person, with every profile attribute, identifier, subscription preference, and device push token. The stream supports full refresh only, because Customer.io profiles have no update time. Each sync reads every profile: one request per 1,000 people to find them, and one per 100 people to fetch their profiles. A workspace with 1,000,000 people takes about 11,000 requests, which is at least 18 minutes at 10 requests per second. **Start Date** doesn't apply.

Use **Full Refresh | Overwrite** to mirror the workspace. **Full Refresh | Append** keeps a copy of each profile per sync, including people deleted since.

#### `segment_memberships`

`segment_memberships` contains one record per person per segment, with the person's `cio_id`, `id`, and `email`, plus the `segment_id`. The stream holds the sum of all segment sizes, which is often several times the number of people. The connector reads up to 30,000 members per request.

Membership has no timestamps, so use **Full Refresh | Overwrite**. **Full Refresh | Append** adds a full copy of every membership on each sync. While a segment's `state` is `build`, Customer.io is still calculating its members, so its rows can be out of date until a later sync.

#### `esp_suppressions`

`esp_suppressions` contains one record per address on each of Customer.io's [email suppression lists](https://docs.customer.io/messaging/channels/email/deliverability/esp-suppression/): `bounces`, `blocks`, `spam_reports`, and `invalid_emails`. Each record includes the address, the `suppression_type`, the `domain`, and a `reason`, which can repeat the address. Each sync makes one request per 1,000 addresses on each list, with at least 4 requests per sync, or 4 per configured domain.

- **Sending domains:** Customer.io suppresses an address on the sending domain where it bounced or was reported as spam. If you send from more than one domain, enter them all in **Sending Domains for ESP Suppressions**. The connector then reads each list once per domain and sets `domain` on each record. If you leave the field empty, the connector reads each list once without a domain filter and `domain` is empty. A domain you don't send from returns no records.
- **Shared domains:** The lists can include addresses suppressed by other workspaces that send from the same domain.
- **Lifted suppressions:** An address removed from a list leaves no record, so use **Full Refresh | Overwrite**. **Full Refresh | Append** adds a full copy of each list on every sync.
- **Custom SMTP:** If you send through your own SMTP server, your email provider keeps the suppressions instead of Customer.io. Deselect this stream.

### Incremental sync behavior

- **`messages`** filters deliveries by creation time on the server, reading 30-day windows. Each incremental sync starts the **Messages Lookback Window (Days)** before the newest `created` value already synced.
- **All other incremental streams** use endpoints that can't filter by time, so they read the full list on every sync and filter records in the connector. Incremental sync reduces the number of records written to the destination, not the number of API requests. The exception is `activities`, which stops reading early, as described in [`activities`](#activities).
- These other streams emit records whose cursor value is at or after the saved cursor minus a one-hour lookback window. The lookback catches records edited while an earlier sync was running, so each incremental sync can re-emit records updated in the hour before the saved cursor. Use **Incremental | Append + Deduped** to remove these duplicates in the destination. With **Incremental | Append**, they appear as repeated rows.
- `campaigns_actions` and `broadcast_actions` keep a separate cursor for each parent campaign or broadcast.
- Incremental syncs don't detect deletions. A record deleted or archived in Customer.io after a sync keeps its last version in the destination. Use a Full Refresh | Overwrite sync to mirror the current data.
- If you set a **Start Date** in the future, the connection test still passes, but until that date arrives, syncs emit only records edited while the sync runs.

### Known limitations

- `campaigns_actions.id` is a string (for example, `"18"`), while `campaigns.actions[].id` is an integer. Cast one of them to join the two streams.
- The `campaigns` fields `audience.person_filters`, `audience.relationship_filters`, `object_attribute_triggers`, and `relationship_attribute_triggers` have no declared type in the schema. Customer.io's API reference documents them as objects but shows JSON strings in its examples, so the connector passes them through as received.
- `messages.metrics`, `activities.data`, and `people.attributes` have no declared keys, because their keys vary by channel, activity type, or workspace. Destinations that write typed files, such as Avro or Parquet, may drop their contents.

## Rate limits

Most Customer.io App API endpoints, including the ones this connector uses, allow 10 requests per second. See [Rate limits](https://docs.customer.io/integrations/api/app/#rate-limits). The connector limits itself to 10 requests per second across all streams.

Other App API traffic in your workspace counts toward the same limit, so Customer.io can still return `429` errors during a sync. The connector retries `429` responses after the delay in the `Retry-After` header, or with exponential backoff when that header is absent. It also retries `500`, `502`, `503`, and `504` errors. If the errors persist, the sync fails after up to 30 retries, which can take up to about 17 minutes.

Sync duration depends mostly on the size of your workspace:

- Child streams make at least one request per parent record, so workspaces with many automations, one-time sends, broadcasts, or segments take longer to sync.
- `people`, `segment_memberships`, and `esp_suppressions` read their full data set on every sync. For example, `people` takes at least 18 minutes per 1,000,000 people. See the [stream details](#people) for request counts.
- `messages` makes one request per 1,000 deliveries in each sync's range, and `activities` makes one request per 100 activities.

## Troubleshooting

| Error | Cause and fix |
| :--- | :--- |
| `401` Unauthorized: "Customer.io rejected the App API key" | The key is invalid or is a Track API key, the **Region** doesn't match your account, or your account restricts API access by IP address and Airbyte's IP addresses aren't allowed. Use a valid App API key, select the correct region, and check the IP allowlist. |
| `403` Forbidden: "Customer.io denied this App API key access" | The key's scope doesn't include the requested data, or an IP allowlist blocks the request. Use a key whose scope includes the data you want to sync, and check the IP allowlist. If only the personal data streams fail, you can also deselect them. |
| Log warning: "Parent state handling is not supported for CartesianProductStreamSlicer." | The `campaigns_actions` stream logs this on every sync. It's harmless and needs no action. |
| `people` or `segment_memberships` syncs fewer records than expected | `people` has one record per profile, so compare its count with the `people` count in the `workspaces` stream. `segment_memberships` excludes archived segments, and segments in the `build` state can be incomplete. |

### IP allowlist

If your Customer.io account restricts API access by IP address, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to the allowlist on the Customer.io **Manage API Credentials** page. If you self-manage Airbyte, add the outbound IP addresses of your Airbyte deployment instead. See [Restrict API access by IP address](https://docs.customer.io/accounts/settings/managing-credentials/#restrict-api-access-by-ip-address).

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
