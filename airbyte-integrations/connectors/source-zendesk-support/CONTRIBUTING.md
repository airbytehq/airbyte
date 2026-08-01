# Contributing to source-zendesk-support

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## 4. Ticket Events Stream — Raw Incremental Ticket Event Export

The `ticket_events` stream uses Zendesk's [Incremental Ticket Event Export](https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/#incremental-ticket-event-export) (`GET /api/v2/incremental/ticket_events.json`). Unlike the `ticket_comments` stream which also hits this endpoint but extracts only Comment child events, `ticket_events` returns the full top-level ticket event objects (including all child events). The cursor field is `timestamp` (unix epoch), filtered via `start_time`. Pagination uses `end_of_stream` to signal the last page.

**Why this matters:** This stream is distinct from `ticket_comments` — both use the same API endpoint but extract different data. `ticket_comments` uses a custom extractor (`ZendeskSupportExtractorEvents`) to drill into `child_events` and filter for Comment events. `ticket_events` uses the default `DpathExtractor` to return the raw ticket event envelope, giving users access to all event types and metadata.

## Incremental Stream Considerations

**Connector type:** Hybrid (manifest.yaml + Python custom components for record extraction, state migration, and event handling)

**Analysis status:** Complete. 42 streams analyzed. 33 use incremental sync via Zendesk's incremental export API, cursor pagination, semi-incremental client-side filtering, or state-delegating patterns. 9 are full-refresh.

### Incremental Streams (33)

The connector implements incremental sync using multiple patterns:
- **Incremental Export API** (tickets, users, organizations, ticket_audits, ticket_metric_events): Uses Zendesk's dedicated incremental export endpoints
- **Cursor-based incremental** (custom_roles, schedules, sla_policies, ticket_fields, ticket_forms, topics, groups, group_memberships, macros, organization_fields, organization_memberships, triggers, audit_logs, ticket_activities, ticket_skips, satisfaction_ratings, user_identities): Uses `updated_at` cursor with start_time filter
- **StateDelegatingStream** (ticket_metrics): Uses bulk endpoint on initial sync, per-ticket incremental fetch via `_ab_updated_at` cursor on subsequent syncs
- **Semi-incremental** (articles, article_attachments, article_comments, article_votes, article_comment_votes, posts, post_comments, post_votes, post_comment_votes, ticket_comments): Client-side cursor filtering

### Full-Refresh Streams (Not Actionable) (9)

| Stream | Reason | Evidence |
|--------|--------|----------|
| deleted_tickets | Point-in-time snapshot; no date filter | Returns currently deleted tickets list |
| account_attributes | Configuration data; no date filter | Zendesk Account Attributes API |
| attribute_definitions | Configuration data; no date filter | Zendesk Attribute Definitions API |
| brands | Small dataset; no date filter | Zendesk Brands API has no `updated_since` |
| tags | No date filter | Zendesk Tags API returns all tags; no `updated_since` |
| user_fields | Configuration data; no date filter | Zendesk User Fields API |
| automations | No date filter on list endpoint | Zendesk Automations API returns all automations |
| categories | No date filter | Zendesk Help Center Categories API |
| sections | No date filter | Zendesk Help Center Sections API |

