# source-zendesk-support: Unique Behaviors

## 1. StateDelegatingStream for Ticket Metrics

The `ticket_metrics` stream uses `StateDelegatingStream` to choose between two completely different retrieval strategies based on whether stream state exists. On initial sync (no state), it reads all ticket metrics from the bulk `/ticket_metrics` endpoint. On incremental syncs with existing state, it switches to fetching metrics per-ticket via `/tickets/{id}/metrics` using the tickets stream as a parent, which allows truly incremental reads but makes one API call per ticket.

**Why this matters:** The first sync and subsequent syncs use entirely different API endpoints and data flow patterns. The incremental path's per-ticket requests mean sync time scales linearly with the number of updated tickets, and any issues with the parent tickets stream will directly block ticket metrics from syncing.

## 2. Enterprise-Only Streams Disabled at Manifest Level

Several streams (`ticket_forms`, `account_attributes`, `attribute_definitions`) are commented out in the manifest because they require Zendesk Enterprise plans and the CDK does not yet support `ConditionalStreams` based on API endpoint availability. The `ticket_forms` stream definition exists but will FAIL with a descriptive error on 403/404 rather than being silently skipped.

**Why this matters:** These streams cannot be enabled without CDK changes to support conditional stream availability. If a user on an Enterprise plan expects these streams, they will not appear in the catalog at all despite the stream definitions existing in the manifest.
