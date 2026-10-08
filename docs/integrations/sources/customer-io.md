# Customer.io

## Overview

This source provides access to the Customer.io API data.

### Output schema

Several output streams are available from this source:

- [Campaigns](https://customer.io/docs/api/#operation/listCampaigns) \(Incremental\)
- [Campaign Actions](https://customer.io/docs/api/#operation/listCampaignActions) \(Incremental\)
- [Newsletters](https://customer.io/docs/api/#operation/listNewsletters) \(Incremental\)
- [Broadcasts](https://docs.customer.io/integrations/api/app/tag/broadcasts/listbroadcasts/) \(Incremental\)
- [Broadcast Actions](https://docs.customer.io/integrations/api/app/tag/broadcasts/broadcastactions/) \(Incremental\)
- [Newsletter Variants](https://docs.customer.io/integrations/api/app/tag/newsletter-variants/listnewslettervariants/) \(Full Refresh\)
- [Transactional Messages](https://docs.customer.io/integrations/api/app/tag/transactional/listtransactional/) \(Incremental\): message templates, not deliveries
- [Sender Identities](https://docs.customer.io/integrations/api/app/tag/sender-identities/listsenders/) \(Full Refresh\)
- [Segments](https://docs.customer.io/integrations/api/app/tag/segments/listsegments/) \(Incremental\): archived segments are not included; a segment archived after an incremental sync keeps its last row in the destination
- [Segment Usage](https://docs.customer.io/integrations/api/app/tag/segments/getsegmentdependencies/) \(Full Refresh\): one record per non-archived segment
- [Subscription Topics](https://docs.customer.io/integrations/api/app/tag/subscription-center/gettopics/) \(Full Refresh\)
- [Object Types](https://docs.customer.io/integrations/api/app/tag/objects/getobjecttypes/) \(Full Refresh\)
- [Workspaces](https://docs.customer.io/integrations/api/app/tag/workspaces/listworkspaces/) \(Full Refresh\)
- [Reporting Webhooks](https://docs.customer.io/integrations/api/app/tag/reporting-webhooks/listwebhooks/) \(Full Refresh\)
- [Snippets](https://docs.customer.io/integrations/api/app/tag/snippets/listsnippets/) \(Incremental\)
- [Collections](https://docs.customer.io/integrations/api/app/tag/collections/getcollections/) \(Full Refresh\)
- [Messages](https://docs.customer.io/integrations/api/app/tag/messages/listmessages/) \(Incremental\): one record per delivery
- [Activities](https://docs.customer.io/integrations/api/app/tag/activities/listactivities/) \(Incremental\): the last 30 days of activity only
- [People](https://docs.customer.io/integrations/api/app/tag/customers/getpeoplefilter/) \(Full Refresh\): every profile, fetched with [List customers, attributes, and devices](https://docs.customer.io/integrations/api/app/tag/customers/getpeoplebyid/)
- [Segment Memberships](https://docs.customer.io/integrations/api/app/tag/segments/getsegmentmembership/) \(Full Refresh\): one record per person per segment
- [ESP Suppressions](https://docs.customer.io/integrations/api/app/tag/esp-suppression/getsuppressionbytype/) \(Full Refresh\)

`reporting_webhooks` syncs each webhook's `endpoint` URL with any `username:password@` part removed; a token in the URL's path or query string is synced as Customer.io returns it ([reporting webhooks FAQ](https://docs.customer.io/integrations/data-out/connections/webhooks/#frequently-asked-questions)). New connections leave the stream unselected. Connections set to **Propagate all field and stream changes** add and sync it automatically after upgrading to 0.7.0; to stop syncing it, deselect the stream and clear its data from the destination.

`workspaces` lists every workspace in the account with message counts for the current billing period and current people and object totals, cached by Customer.io for up to two hours. The records have no update time, so use Full Refresh | Overwrite for the latest counts, or Full Refresh | Append to keep one snapshot per sync.

`collections` lists each collection's name, schema, row count and size, not its contents. It is full refresh only, so every sync has the current counts.

`messages` has one record per delivery, a message sent to one person, with the time each metric (delivered, opened, clicked, converted and more) was recorded. Syncs read deliveries in 30-day windows of creation time, one request per 1,000 deliveries, and Start Date applies to the creation time. Customer.io records opens and clicks for up to 6 months and conversions for up to 90 days, so each incremental sync reads the deliveries created in the last **Messages Lookback Window (Days)** again (default 30, up to 180): use Incremental | Append + Deduped. Raise the setting, or run a full refresh from time to time, for complete metrics; lower it to shorten syncs in high-volume workspaces. Records carry the recipient's address and identifiers, the subject line and per-person open and click times.

`activities` is the workspace activity log, one record per event: message events such as sent, opened and clicked, tracked events, page and screen views, and attribute changes, including those of deleted people. Customer.io guarantees only the last 30 days, so sync at least every 30 days and use Incremental | Append + Deduped to keep older history. Expect several records per message sent; the first sync reads every retained activity, 100 per request. Incremental syncs skip events sent to Customer.io with a timestamp more than an hour before the newest activity already synced. If a page of 100 such older events comes before newer ones in Customer.io's list, the newer ones are skipped too. Records carry email addresses, your person IDs, IP addresses and user agents of opens and clicks, event and attribute values, and page URLs.

`people` has one record per person with every profile attribute, identifier, subscription preference and device push token. Each sync reads every profile, one request per 1,000 people to find them and one per 100 to fetch them: 1,000,000 people take about 11,000 requests, at least 18 minutes at 10 requests per second. Start Date does not apply. Full Refresh | Overwrite mirrors the workspace; Append keeps deleted people.

`segment_memberships` has one record per person per segment with the person's `cio_id`, ID and email address, so it holds the sum of all segment sizes, often several times the number of people, at up to 30,000 members per request. Membership has no timestamps, so use Full Refresh | Overwrite: Append adds a full copy on every sync. Members of a segment whose `state` is `build` can be out of date while Customer.io calculates them. Archived segments are not included.

`esp_suppressions` has one record per address on each of Customer.io's email suppression lists (bounces, blocks, spam reports, invalid emails), with a reason that can repeat the address. Each sync makes one request per 1,000 addresses on each list, at least 4 (4 per configured domain). Lifted suppressions leave the list without a record, so use Full Refresh | Overwrite: Append adds a full copy on every sync. Customer.io suppresses an address on the sending domain where it bounced or was reported as spam, so if you send from more than one domain, enter them in **Sending Domains for ESP Suppressions**: each list is then read once per domain, and records carry their `domain`. A domain you do not send from returns no records. The lists can include addresses suppressed by other workspaces that send from the same domain. If you send through your own SMTP server, your email provider keeps the suppressions, so deselect the stream.

These five streams carry personal data and are not selected by default. Connections set to **Propagate all field and stream changes** add and sync them automatically after upgrading to 0.8.0; to stop syncing them, deselect the streams and clear their data from the destination. Incremental and Append syncs keep rows of people later deleted or suppressed in Customer.io, so handle erasure requests in the destination too. If these streams fail with a 403 error, check that the key can read this data and that the Airbyte IP addresses are on your allowlist, or deselect the streams.

If there are more endpoints you'd like Faros AI to support, please [create an
issue.](https://github.com/faros-ai/airbyte-connectors/issues/new)

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| SSL connection    | Yes        |
| Namespaces        | No         |

### Performance considerations

The Customer.io API is divided into three different hosts, each serving a
different component of Customer.io. This source only uses the Beta API host,
which enforces a rate limit of 10 requests per second. Please [create an
issue](https://github.com/faros-ai/airbyte-connectors/issues/new) if you see any
rate limit issues.

## Getting started

### Requirements

- Customer.io App API Key

Please follow the [their documentation for generating an App API Key](https://customer.io/docs/managing-credentials/).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                   | Subject                                     |
|:--------|:-----------| :------------------------------------------------------------- |:--------------------------------------------|
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
