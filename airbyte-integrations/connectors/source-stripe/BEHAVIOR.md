# source-stripe: Unique Behaviors

## 1. Events-Based Incremental Sync via StateDelegatingStream

Most entity streams (customers, subscriptions, invoices, charges, refunds, transfers, etc.) use `StateDelegatingStream` with a 30-day `api_retention_period`. On the first sync (no state), the connector reads directly from the entity's own endpoint (e.g., `/v1/customers`). On subsequent incremental syncs, it switches to reading from `/v1/events` filtered by specific event types (e.g., `customer.created`, `customer.updated`, `customer.deleted`), then uses `DpathFlattenFields` to unwrap `data.object` and reconstruct the entity record from the event payload.

Stripe's Events API only retains events for 30 days. If the connector's state falls behind by more than 30 days (e.g., after a long pause in syncing), it automatically reverts to a full refresh from the entity endpoint rather than trying to read events that no longer exist.

**Why this matters:** What looks like a simple entity read is actually two completely different data paths depending on whether state exists and how old it is. Adding a new entity stream requires defining both the direct-read retriever AND the events-based retriever with the correct event type filter strings. If the event type strings are wrong, incremental syncs will silently miss updates.

## 2. Silent 403/400/404 Error Ignoring

The base error handler is configured to IGNORE (not fail) responses with HTTP status 403 (permission denied), 400 (bad request), and 404 (not found). When the Stripe API returns any of these errors for a specific resource or subresource, the connector silently skips that record and continues syncing.

**Why this matters:** If an API key loses access to a specific Stripe resource (e.g., Issuing endpoints require special permissions), those records will silently disappear from incremental syncs without any error or warning in the sync logs. A user may not notice they are missing data until they check record counts against the Stripe dashboard.
