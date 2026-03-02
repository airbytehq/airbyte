# source-klaviyo: Unique Behaviors

## 1. Hidden Per-Campaign API Calls for Detailed Campaign Data

The `CampaignsDetailedTransformation` makes two additional API calls for every campaign record during transformation: one to fetch `estimated_recipient_count` from the `/campaign-recipient-estimations/{id}` endpoint, and one to fetch `campaign_messages` by following the `relationships.campaign-messages.links.related` URL from the record itself.

**Why this matters:** Each campaign record triggers two hidden HTTP requests, so syncing 1,000 campaigns results in at least 2,000 additional API calls beyond the pagination requests. These calls have their own error handling and retry logic (including 404 ignore) that operates independently from the main stream's error handling.

## 2. JSON:API Included Relationship Resolution

Klaviyo uses the JSON:API specification where related resources are returned in a top-level `included` array rather than being nested in the record. The `KlaviyoIncludedFieldExtractor` resolves these relationships by matching `type` and `id` between the record's `relationships` and the `included` array, then merging the included resource's attributes back into the relationship data.

**Why this matters:** Records extracted from Klaviyo do not contain their related data inline. Without the included field resolution, relationship fields would only contain `type` and `id` references instead of actual attribute data. This affects streams like events where metric and profile details need to be resolved from the included array.
