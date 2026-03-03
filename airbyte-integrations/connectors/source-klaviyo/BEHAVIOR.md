# source-klaviyo: Unique Behaviors

## 1. Hidden Per-Campaign API Calls for Detailed Campaign Data

The `CampaignsDetailedTransformation` makes two additional API calls for every campaign record during transformation: one to fetch `estimated_recipient_count` from the `/campaign-recipient-estimations/{id}` endpoint, and one to fetch `campaign_messages` by following the `relationships.campaign-messages.links.related` URL from the record itself.

**Why this matters:** Each campaign record triggers two hidden HTTP requests, so syncing 1,000 campaigns results in at least 2,000 additional API calls beyond the pagination requests. These calls have their own error handling and retry logic (including 404 ignore) that operates independently from the main stream's error handling.

## 2. JSON:API Included Relationship Resolution

Klaviyo uses the JSON:API specification where related resources are returned in a top-level `included` array rather than being nested in the record. The `KlaviyoIncludedFieldExtractor` resolves these relationships by matching `type` and `id` between the record's `relationships` and the `included` array, then merging the included resource's attributes back into the relationship data.

**Why this matters:** Records extracted from Klaviyo do not contain their related data inline. Without the included field resolution, relationship fields would only contain `type` and `id` references instead of actual attribute data. This affects streams like events where metric and profile details need to be resolved from the included array.

## 3. Endpoint-Specific Rate Limits and Concurrency

Klaviyo's API rate limiting varies by endpoint size tier, each with a burst and steady-state limit:

| Tier | Burst | Steady |
|------|-------|--------|
| XS   | 1/s   | 15/m   |
| S    | 3/s   | 60/m   |
| M    | 10/s  | 150/m  |
| L    | 75/s  | 700/m  |
| XL   | 350/s | 3500/m |

As of 2024-11-11, the streams map to endpoint tiers and concurrency settings as follows:

| Stream | Endpoint | Klaviyo Rate Limit Size | Source Concurrency Between Streams | Source Concurrency Within Stream | Source Max Number of Threads Sharing Rate Limits | Notes |
|--------|----------|------------------------|------------------------------------|----------------------------------|--------------------------------------------------|-------|
| profiles | [GET /profiles](https://developers.klaviyo.com/en/v2023-02-22/reference/get_profiles) | M | Yes, shared with global_exclusions | No (`step` not defined in `incremental_sync`) | 2 | With other streams (global_exclusions), not within stream |
| global_exclusions | [GET /profiles](https://developers.klaviyo.com/en/v2023-02-22/reference/get_profiles) | M | Yes, shared with profiles | No (`step` not defined in `incremental_sync`) | 2 | With other streams (profiles), not within stream |
| events | [GET /events](https://developers.klaviyo.com/en/reference/get_events) | XL | Yes, shared with events_detailed | Yes (sliced on `datetime`) | number of steps for events + number of steps for events_detailed | With other streams (events_detailed) and within stream |
| events_detailed | [GET /events](https://developers.klaviyo.com/en/reference/get_events) | XL | Yes, shared with events | Yes (sliced on `datetime`) | number of steps for events + number of steps for events_detailed | With other streams (events) and within stream |
| email_templates | [GET /templates](https://developers.klaviyo.com/en/reference/get_templates) | M | None | No (`step` not defined in `incremental_sync`) | 1 | None |
| metrics | [GET /metrics](https://developers.klaviyo.com/en/reference/get_metrics) | M | None | No (`step` not defined in `incremental_sync`) | 1 | None |
| lists | [GET /lists](https://developers.klaviyo.com/en/reference/get_lists) | L | Yes, shared with lists_detailed | No (`step` not defined in `incremental_sync`) | 2 | With other streams (lists_detailed), not within stream |
| lists_detailed | [GET /lists](https://developers.klaviyo.com/en/reference/get_lists) | L | Yes, shared with lists | No (`step` not defined in `incremental_sync`) | 2 | With other streams (lists), not within stream |

> **Note:** As of 2024-11-11, `metrics`, `lists`, and `lists_detailed` are not supported by the Concurrent CDK as they do client-side filtering.

The only streams that allow for slicing (and hence may perform more concurrent HTTP requests) are `events` and `events_detailed`. All other streams have no slicing, so their concurrency is limited to the number of streams querying the same endpoint. Given that the events endpoint is XL tier, the default concurrency is set to **10**.

**Why this matters:** Streams sharing the same endpoint share the same rate limit budget. Running `profiles` and `global_exclusions` simultaneously means both compete for the same M-tier limit. The `events` and `events_detailed` streams are the most impactful — both share the XL-tier endpoint AND support datetime slicing, so the total concurrent requests equals the sum of both streams' active slices.
