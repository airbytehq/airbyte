# source-stripe: Unique Behaviors

## 1. Events-Based Incremental Sync via StateDelegatingStream

Most entity streams (customers, subscriptions, invoices, charges, refunds, transfers, etc.) use `StateDelegatingStream` with a 30-day `api_retention_period`. On the first sync (no state), the connector reads directly from the entity's own endpoint (e.g., `/v1/customers`). On subsequent incremental syncs, it switches to reading from `/v1/events` filtered by specific event types (e.g., `customer.created`, `customer.updated`, `customer.deleted`), then uses `DpathFlattenFields` to unwrap `data.object` and reconstruct the entity record from the event payload.

Stripe's Events API only retains events for 30 days. If the connector's state falls behind by more than 30 days (e.g., after a long pause in syncing), it automatically reverts to a full refresh from the entity endpoint rather than trying to read events that no longer exist.

**Why this matters:** What looks like a simple entity read is actually two completely different data paths depending on whether state exists and how old it is. Adding a new entity stream requires defining both the direct-read retriever AND the events-based retriever with the correct event type filter strings. If the event type strings are wrong, incremental syncs will silently miss updates.

## 2. Silent 403/400/404 Error Ignoring

The base error handler is configured to IGNORE (not fail) responses with HTTP status 403 (permission denied), 400 (bad request), and 404 (not found). When the Stripe API returns any of these errors for a specific resource or subresource, the connector silently skips that record and continues syncing.

**Why this matters:** If an API key loses access to a specific Stripe resource (e.g., Issuing endpoints require special permissions), those records will silently disappear from incremental syncs without any error or warning in the sync logs. A user may not notice they are missing data until they check record counts against the Stripe dashboard.

## 3. Inaccessible Expandable Fields in Events API

As of April 2024, the Stripe API does not support retrieving [expandable fields](https://docs.stripe.com/api/expanding_objects) from the Events API. This limits how the connector can process events during incremental syncs — it cannot reconstruct the full latest state of an object solely from event payloads when expandable fields are involved.

**Why this matters:** During incremental syncs (which read from `/v1/events`), the connector only sees the non-expanded version of each object. Fields that require expansion (e.g., nested customer details on a charge) will be missing or returned as just an ID string. This is a fundamental Stripe API limitation, not a connector bug.

## 4. Populating Data for Sandbox Accounts

Using `Stripe Sandbox Account` test credentials, connect to https://dashboard.stripe.com/ and toggle "Test mode". New records can be added here, but modifying or deleting existing records may cause CAT failures. To create payments, use [Stripe's test credit cards](https://docs.stripe.com/testing#cards) in test mode.

**Why this matters:** CAT tests depend on specific record states in the sandbox. Modifying or deleting records that tests rely on will break assertions. Only add new records when populating test data.

## 5. API Version-Dependent Data Discrepancies in Events

The data returned in event payloads depends on the Stripe API version the object was created with, not the version used to read the event. For example, `charge.refunds` may appear in events even though it is an [expandable field](https://docs.stripe.com/api/expanding_objects) that should not be present — this happens because the sandbox uses API version `2020-08-27`, and the `charge.refunds` field was only [removed in the 2022-11-15 upgrade](https://docs.stripe.com/upgrades#2022-11-15). See [Stripe API versioning](https://docs.stripe.com/api/versioning) for how versions are managed.

**Why this matters:** When debugging unexpected fields appearing (or missing) in event payloads, the root cause may be the API version the data was originally created with, not the connector's behavior. This is especially confusing in sandbox environments where the API version may be much older than production.
