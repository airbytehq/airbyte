# Sendgrid

<HideInUI>

This page contains the setup guide and reference information for the [Sendgrid](https://sendgrid.com/) source connector.

</HideInUI>

## Prerequisites

- A SendGrid account
- A [SendGrid API key](https://www.twilio.com/docs/sendgrid/ui/account-and-settings/api-keys#creating-an-api-key) with the required permissions

## Setup guide

### Step 1: Set up SendGrid

Create a SendGrid API key with the permissions required for the streams you want to sync. The connector authenticates against the [SendGrid v3 API](https://www.twilio.com/docs/sendgrid/api-reference/how-to-use-the-sendgrid-v3-api/authentication) with this key as a bearer token. Copy the key when SendGrid displays it: you can't retrieve it again later.

Give the key read-only access. The connector only reads data, so a key restricted to the scopes below limits what Airbyte can reach if the key is ever exposed.

The following API key scopes are required depending on which streams you enable:

| Streams | Required Scopes |
|---------|-----------------|
| Bounces, Blocks, Spam Reports, Invalid Emails, Global Suppressions | `suppression.read` or the specific `suppression.{type}.read` scopes |
| Suppression Groups, Suppression Group Members | `asm.groups.read` |
| Templates | `templates.read` |
| Contacts, Lists, Segments, Single Sends, Single Send Stats, Stats Automations, Campaigns | `marketing.read` |

For simplicity, you can create an API key with **Full Access** to ensure all streams work correctly. If you prefer more granular permissions, enable only the scopes listed above for the streams you need.

### Step 2: Set up the Sendgrid connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, enter the name for the Sendgrid connector and select **Sendgrid** from the Source type dropdown.
4. For **API Key**, enter the SendGrid API key you created.
5. For **Start date**, enter a UTC timestamp in the format `2017-01-25T00:00:00Z`. The connector doesn't replicate data created before this date in incremental streams. Other formats, including UTC offsets such as `+00:00` and fractional seconds, are rejected.
6. Click **Set up source**.

<HideInUI>

## Supported sync modes

The Sendgrid source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped), except for Bounces and Spam Reports

Bounces and Spam Reports have no primary key, so deduplication isn't available for them. Sync them in **Incremental - Append** mode and deduplicate downstream if you need one row per address.

## Supported Streams

| Stream | Primary key | Incremental cursor |
|--------|-------------|--------------------|
| [Blocks](https://www.twilio.com/docs/sendgrid/api-reference/blocks-api/retrieve-all-blocks) | `email` | `created` |
| [Bounces](https://www.twilio.com/docs/sendgrid/api-reference/bounces-api/retrieve-all-bounces) | None | `created` |
| Campaigns | `id` | Full refresh only |
| [Contacts](https://www.twilio.com/docs/sendgrid/api-reference/contacts/export-contacts) | `contact_id` | Full refresh only |
| [Global Suppressions](https://www.twilio.com/docs/sendgrid/api-reference/suppressions-global-suppressions/retrieve-all-global-suppressions) | `email` | `created` |
| [Invalid Emails](https://www.twilio.com/docs/sendgrid/api-reference/invalid-emails-api/retrieve-all-invalid-emails) | `email` | `created` |
| [Lists](https://www.twilio.com/docs/sendgrid/api-reference/lists/get-all-lists) | `id` | Full refresh only |
| [Segments](https://www.twilio.com/docs/sendgrid/api-reference/segmenting-contacts-v2/get-list-of-segments) | `id` | Full refresh only |
| [Single Sends](https://www.twilio.com/docs/sendgrid/api-reference/single-sends/get-all-single-sends) | `id` | Full refresh only |
| [Single Send Stats](https://www.twilio.com/docs/sendgrid/api-reference/marketing-campaign-stats/get-all-single-sends-stats) | `id` | Full refresh only |
| [Spam Reports](https://www.twilio.com/docs/sendgrid/api-reference/spam-reports-api/retrieve-all-spam-reports) | None | `created` |
| [Stats Automations](https://www.twilio.com/docs/sendgrid/api-reference/marketing-campaign-stats/get-all-automation-stats) | `id` | Full refresh only |
| [Suppression Groups](https://www.twilio.com/docs/sendgrid/api-reference/suppressions-unsubscribe-groups/retrieve-all-suppression-groups-associated-with-the-user) | `id` | Full refresh only |
| [Suppression Group Members](https://www.twilio.com/docs/sendgrid/api-reference/suppressions-suppressions/retrieve-all-suppressions) | `group_id`, `email` | `created_at` |
| [Templates](https://www.twilio.com/docs/sendgrid/api-reference/transactional-templates/retrieve-paged-transactional-templates) | `id` | Full refresh only |

A few streams need extra explanation:

- **Campaigns** reads the Marketing Campaigns endpoint `/v3/marketing/campaigns`, not the Legacy Marketing Campaigns endpoint `/v3/campaigns`. Legacy Marketing Campaigns data isn't available through this connector.
- **Contacts** uses SendGrid's asynchronous [contacts export](https://www.twilio.com/docs/sendgrid/api-reference/contacts/export-contacts): the connector requests an export, polls until SendGrid finishes it, then downloads the resulting file. A sync of this stream takes as long as SendGrid needs to build the export, which can be several minutes on large contact databases. Field names are lowercased, so a custom field named `Company_Name` in SendGrid arrives as `company_name`.
- **Segments** reads Segments 2.0 (`/v3/marketing/segments/2.0`). Segments that exist only in the older 1.0 API don't appear.

The connector checks the connection by reading the Bounces stream, so the API key needs a suppression read scope even if you only plan to sync marketing streams.

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about Sendgrid connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting

SendGrid enforces [per-endpoint rate limits](https://www.twilio.com/docs/sendgrid/api-reference/how-to-use-the-sendgrid-v3-api/rate-limits). To stay inside them, the connector caps itself at 70 requests per second across all streams, reads up to 6 streams in parallel, and runs at most 2 Contacts export jobs at a time. It reads the `X-RateLimit-Remaining` and `X-RateLimit-Reset` response headers and waits for the reset window when SendGrid returns a 429, so a rate-limited sync slows down instead of failing.

If other tools share the same API key, the combined traffic can still exceed SendGrid's limits. Use a dedicated key for Airbyte to keep them separate.

#### The start date only applies to incremental streams

The **Start date** setting filters only the streams that have a cursor in the table above. Full refresh streams always return everything the API exposes, regardless of the date you set.

### Troubleshooting

#### 403 Forbidden errors

If you encounter 403 errors, check the following:

1. **Verify API key permissions**: Ensure your API key has the required scopes for the streams you're trying to sync. See the [Setup guide](#step-1-set-up-sendgrid) for the specific scopes needed for each stream.

2. **Legacy vs. new Marketing Campaigns**: This connector uses the new Marketing Campaigns API (`/v3/marketing/*`), which requires the `marketing.read` scope. If your SendGrid account uses Legacy Marketing Campaigns, you get 403 errors when syncing marketing streams. Legacy Marketing Campaigns use different endpoints and scopes (`marketing_campaigns.read`) that this connector doesn't support.

3. **Account type limitations**: Some SendGrid account types may not have access to all API endpoints. Verify that your SendGrid plan includes access to the features you're trying to sync.

</details>

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                                                                                           |
|:--------|:-----------| :------------------------------------------------------- |:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1.3.42 | 2026-08-18 | [84757](https://github.com/airbytehq/airbyte/pull/84757) | Update dependencies |
| 1.3.41 | 2026-08-11 | [84110](https://github.com/airbytehq/airbyte/pull/84110) | Update dependencies |
| 1.3.40 | 2026-08-04 | [83615](https://github.com/airbytehq/airbyte/pull/83615) | Update dependencies |
| 1.3.39 | 2026-07-28 | [83102](https://github.com/airbytehq/airbyte/pull/83102) | Update dependencies |
| 1.3.38 | 2026-07-21 | [82574](https://github.com/airbytehq/airbyte/pull/82574) | Update dependencies |
| 1.3.37 | 2026-07-14 | [82007](https://github.com/airbytehq/airbyte/pull/82007) | Update dependencies |
| 1.3.36 | 2026-06-30 | [81252](https://github.com/airbytehq/airbyte/pull/81252) | Update dependencies |
| 1.3.35 | 2026-06-23 | [80649](https://github.com/airbytehq/airbyte/pull/80649) | Update dependencies |
| 1.3.34 | 2026-06-16 | [80013](https://github.com/airbytehq/airbyte/pull/80013) | Update dependencies |
| 1.3.33 | 2026-06-09 | [79501](https://github.com/airbytehq/airbyte/pull/79501) | Update dependencies |
| 1.3.32 | 2026-06-02 | [78949](https://github.com/airbytehq/airbyte/pull/78949) | Update dependencies |
| 1.3.31 | 2026-04-28 | [77509](https://github.com/airbytehq/airbyte/pull/77509) | Update dependencies |
| 1.3.30 | 2026-04-25 | [77009](https://github.com/airbytehq/airbyte/pull/77009) | Promoted release candidate to GA |
| 1.3.30-rc.1 | 2026-04-16 | [76407](https://github.com/airbytehq/airbyte/pull/76407) | Increase HTTPAPIBudget rate limit from 50 to 70 req/s |
| 1.3.29 | 2026-04-21 | [75796](https://github.com/airbytehq/airbyte/pull/75796) | Update dependencies |
| 1.3.28 | 2026-04-14 | [76335](https://github.com/airbytehq/airbyte/pull/76335) | Promoted release candidate to GA |
| 1.3.28-rc.5 | 2026-04-13 | [74713](https://github.com/airbytehq/airbyte/pull/74713) | Add HTTPAPIBudget rate limiting (Phase 2) with concurrency=6 |
| 1.3.28-rc.4 | 2026-04-12 | [74713](https://github.com/airbytehq/airbyte/pull/74713) | Add concurrency_level for parallel stream processing (concurrency=6) |
| 1.3.27 | 2026-03-24 | [75331](https://github.com/airbytehq/airbyte/pull/75331) | Update dependencies |
| 1.3.26 | 2026-02-24 | [73950](https://github.com/airbytehq/airbyte/pull/73950) | Update dependencies |
| 1.3.25 | 2026-02-10 | [73157](https://github.com/airbytehq/airbyte/pull/73157) | Update dependencies |
| 1.3.24 | 2026-02-03 | [72566](https://github.com/airbytehq/airbyte/pull/72566) | Update dependencies |
| 1.3.23 | 2026-01-20 | [72099](https://github.com/airbytehq/airbyte/pull/72099) | Update dependencies |
| 1.3.22 | 2026-01-14 | [71536](https://github.com/airbytehq/airbyte/pull/71536) | Update dependencies |
| 1.3.21 | 2025-12-18 | [70736](https://github.com/airbytehq/airbyte/pull/70736) | Update dependencies |
| 1.3.20 | 2025-11-25 | [69988](https://github.com/airbytehq/airbyte/pull/69988) | Update dependencies |
| 1.3.19 | 2025-11-18 | [69685](https://github.com/airbytehq/airbyte/pull/69685) | Update dependencies |
| 1.3.18 | 2025-10-29 | [68852](https://github.com/airbytehq/airbyte/pull/68852) | Update dependencies |
| 1.3.17 | 2025-10-22 | [68591](https://github.com/airbytehq/airbyte/pull/68591) | Add `suggestedStreams` |
| 1.3.16 | 2025-10-21 | [68410](https://github.com/airbytehq/airbyte/pull/68410) | Update dependencies |
| 1.3.15 | 2025-10-14 | [67931](https://github.com/airbytehq/airbyte/pull/67931) | Update dependencies |
| 1.3.14 | 2025-10-07 | [67227](https://github.com/airbytehq/airbyte/pull/67227) | Update dependencies |
| 1.3.13 | 2025-09-30 | [66871](https://github.com/airbytehq/airbyte/pull/66871) | Update dependencies |
| 1.3.12 | 2025-09-23 | [62286](https://github.com/airbytehq/airbyte/pull/62286) | Update dependencies |
| 1.3.11 | 2025-09-15 | [66078](https://github.com/airbytehq/airbyte/pull/66078) | Update to CDK v7 |
| 1.3.10 | 2025-06-21 | [61826](https://github.com/airbytehq/airbyte/pull/61826) | Update dependencies |
| 1.3.9 | 2025-06-14 | [61314](https://github.com/airbytehq/airbyte/pull/61314) | Update dependencies |
| 1.3.8 | 2025-05-25 | [60199](https://github.com/airbytehq/airbyte/pull/60199) | Update dependencies |
| 1.3.7 | 2025-05-04 | [58982](https://github.com/airbytehq/airbyte/pull/58982) | Update dependencies |
| 1.3.6 | 2025-04-19 | [58405](https://github.com/airbytehq/airbyte/pull/58405) | Update dependencies |
| 1.3.5 | 2025-04-12 | [57952](https://github.com/airbytehq/airbyte/pull/57952) | Update dependencies |
| 1.3.4 | 2025-04-05 | [57415](https://github.com/airbytehq/airbyte/pull/57415) | Update dependencies |
| 1.3.3 | 2025-03-29 | [56746](https://github.com/airbytehq/airbyte/pull/56746) | Update dependencies |
| 1.3.2 | 2025-03-22 | [55038](https://github.com/airbytehq/airbyte/pull/55038) | Update dependencies |
| 1.3.1 | 2025-03-13 | [55744](https://github.com/airbytehq/airbyte/pull/55744) | Increase max concurrent async job count to 2 |
| 1.3.0 | 2025-03-04 | [55185](https://github.com/airbytehq/airbyte/pull/55185) | Update manifest for adapting changes with AsyncRetriever |
| 1.2.9 | 2025-02-23 | [54625](https://github.com/airbytehq/airbyte/pull/54625) | Update dependencies |
| 1.2.8 | 2025-02-15 | [54013](https://github.com/airbytehq/airbyte/pull/54013) | Update dependencies |
| 1.2.7 | 2025-02-08 | [53508](https://github.com/airbytehq/airbyte/pull/53508) | Update dependencies |
| 1.2.6 | 2025-02-01 | [52995](https://github.com/airbytehq/airbyte/pull/52995) | Update dependencies |
| 1.2.5 | 2025-01-25 | [52535](https://github.com/airbytehq/airbyte/pull/52535) | Update dependencies |
| 1.2.4 | 2025-01-18 | [51892](https://github.com/airbytehq/airbyte/pull/51892) | Update dependencies |
| 1.2.3 | 2025-01-11 | [48238](https://github.com/airbytehq/airbyte/pull/48238) | Update dependencies |
| 1.2.2 | 2024-10-29 | [47836](https://github.com/airbytehq/airbyte/pull/47836) | Update dependencies |
| 1.2.1 | 2024-10-28 | [47588](https://github.com/airbytehq/airbyte/pull/47588) | Update dependencies |
| 1.2.0 | 2024-10-13 | [46870](https://github.com/airbytehq/airbyte/pull/46870) | Migrate to Manifest-only |
| 1.1.5 | 2024-10-12 | [46781](https://github.com/airbytehq/airbyte/pull/46781) | Update dependencies |
| 1.1.4 | 2024-10-05 | [46460](https://github.com/airbytehq/airbyte/pull/46460) | Update dependencies |
| 1.1.3 | 2024-09-28 | [46105](https://github.com/airbytehq/airbyte/pull/46105) | Update dependencies |
| 1.1.2 | 2024-09-21 | [45782](https://github.com/airbytehq/airbyte/pull/45782) | Update dependencies |
| 1.1.1 | 2024-09-14 | [45525](https://github.com/airbytehq/airbyte/pull/45525) | Update dependencies |
| 1.1.0 | 2024-09-11 | [45191](https://github.com/airbytehq/airbyte/pull/45191) | Move Contacts stream to declarative async job |
| 1.0.18 | 2024-09-07 | [45239](https://github.com/airbytehq/airbyte/pull/45239) | Update dependencies |
| 1.0.17 | 2024-08-31 | [44953](https://github.com/airbytehq/airbyte/pull/44953) | Update dependencies |
| 1.0.16 | 2024-08-24 | [44753](https://github.com/airbytehq/airbyte/pull/44753) | Update dependencies |
| 1.0.15 | 2024-08-17 | [44233](https://github.com/airbytehq/airbyte/pull/44233) | Update dependencies |
| 1.0.14 | 2024-08-12 | [43751](https://github.com/airbytehq/airbyte/pull/43751) | Update dependencies |
| 1.0.13 | 2024-08-10 | [43635](https://github.com/airbytehq/airbyte/pull/43635) | Update dependencies |
| 1.0.12 | 2024-08-03 | [43269](https://github.com/airbytehq/airbyte/pull/43269) | Update dependencies |
| 1.0.11 | 2024-07-27 | [42729](https://github.com/airbytehq/airbyte/pull/42729) | Update dependencies |
| 1.0.10 | 2024-07-20 | [42310](https://github.com/airbytehq/airbyte/pull/42310) | Update dependencies |
| 1.0.9 | 2024-07-13 | [41753](https://github.com/airbytehq/airbyte/pull/41753) | Update dependencies |
| 1.0.8 | 2024-07-10 | [41531](https://github.com/airbytehq/airbyte/pull/41531) | Update dependencies |
| 1.0.7 | 2024-07-09 | [41137](https://github.com/airbytehq/airbyte/pull/41137) | Update dependencies |
| 1.0.6 | 2024-07-06 | [40898](https://github.com/airbytehq/airbyte/pull/40898) | Update dependencies |
| 1.0.5 | 2024-06-25 | [40356](https://github.com/airbytehq/airbyte/pull/40356) | Update dependencies |
| 1.0.4 | 2024-06-22 | [40155](https://github.com/airbytehq/airbyte/pull/40155) | Update dependencies |
| 1.0.3 | 2024-06-06 | [39197](https://github.com/airbytehq/airbyte/pull/39197) | [autopull] Upgrade base image to v1.2.2 |
| 1.0.2 | 2024-05-21 | [38478](https://github.com/airbytehq/airbyte/pull/38478) | Update deprecated authenticator package |
| 1.0.1 | 2024-05-20 | [38264](https://github.com/airbytehq/airbyte/pull/38264) | Replace AirbyteLogger with logging.Logger |
| 1.0.0 | 2024-04-15 | [35776](https://github.com/airbytehq/airbyte/pull/35776) | Migration to low-code CDK. Breaking change that updates configuration keys, removes unsubscribe_groups stream, renames a stream to singlesend_stats, and adds the singlesends stream. |
| 0.5.0 | 2024-03-26 | [36455](https://github.com/airbytehq/airbyte/pull/36455) | Unpin CDK version, add record counts to state messages |
| 0.4.3 | 2024-02-21 | [35343](https://github.com/airbytehq/airbyte/pull/35343) | Handle uncompressed contacts downloads. |
| 0.4.2 | 2024-02-12 | [35181](https://github.com/airbytehq/airbyte/pull/35181) | Manage dependencies with Poetry. |
| 0.4.1 | 2023-10-18 | [31543](https://github.com/airbytehq/airbyte/pull/31543) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.4.0 | 2023-05-19 | [23959](https://github.com/airbytehq/airbyte/pull/23959) | Add `unsubscribe_groups`stream |
| 0.3.1 | 2023-01-27 | [21939](https://github.com/airbytehq/airbyte/pull/21939) | Fix contacts missing records; Remove Messages stream |
| 0.3.0 | 2023-01-25 | [21587](https://github.com/airbytehq/airbyte/pull/21587) | Make sure spec works as expected in UI - make start_time parameter an ISO string instead of an integer interpreted as timestamp (breaking, update your existing connections and set the start_time parameter to ISO 8601 date time string in UTC) |
| 0.2.16 | 2022-11-02 | [18847](https://github.com/airbytehq/airbyte/pull/18847) | Skip the stream on `400, 401 - authorization required` with log message |
| 0.2.15 | 2022-10-19 | [18182](https://github.com/airbytehq/airbyte/pull/18182) | Mark the sendgrid api key secret in the spec |
| 0.2.14 | 2022-09-07 | [16400](https://github.com/airbytehq/airbyte/pull/16400) | Change Start Time config parameter to datetime string |
| 0.2.13 | 2022-08-29 | [16112](https://github.com/airbytehq/airbyte/pull/16112) | Revert back to Python CDK |
| 0.2.12 | 2022-08-24 | [15911](https://github.com/airbytehq/airbyte/pull/15911) | Bugfix to allowing reading schemas at runtime |
| 0.2.11 | 2022-08-19 | [15800](https://github.com/airbytehq/airbyte/pull/15800) | Bugfix to allow reading sentry.yaml at runtime |
| 0.2.10 | 2022-08-17 | [15734](https://github.com/airbytehq/airbyte/pull/15734) | Fix yaml based on the new schema validator |
| 0.2.9 | 2022-08-11 | [15257](https://github.com/airbytehq/airbyte/pull/15257) | Migrate to config-based framework |
| 0.2.8 | 2022-06-07 | [13571](https://github.com/airbytehq/airbyte/pull/13571) | Add Message stream |
| 0.2.7 | 2021-09-08 | [5910](https://github.com/airbytehq/airbyte/pull/5910) | Add Single Sends Stats stream |
| 0.2.6 | 2021-07-19 | [4839](https://github.com/airbytehq/airbyte/pull/4839) | Gracefully handle malformed responses from the API |

</details>

</HideInUI>
