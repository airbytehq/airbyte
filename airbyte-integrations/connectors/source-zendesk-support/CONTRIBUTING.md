# Contributing to source-zendesk-support

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

**Connector type:** Hybrid (manifest.yaml + Python custom components for record extraction, state migration, and event handling)

**Analysis status:** Complete. 42 streams analyzed. 32 use incremental sync via Zendesk's incremental export API, cursor pagination, or semi-incremental client-side filtering. 10 are full-refresh.

### Incremental Streams (32)

The connector implements incremental sync using multiple patterns:
- **Incremental Export API** (tickets, users, organizations, ticket_audits, ticket_metric_events): Uses Zendesk's dedicated incremental export endpoints
- **Cursor-based incremental** (custom_roles, schedules, sla_policies, ticket_fields, ticket_forms, topics, groups, group_memberships, macros, organization_fields, organization_memberships, triggers, audit_logs, ticket_activities, ticket_skips, satisfaction_ratings): Uses `updated_at` cursor with start_time filter
- **Semi-incremental** (articles, article_attachments, article_comments, article_votes, article_comment_votes, posts, post_comments, post_votes, post_comment_votes, ticket_comments): Client-side cursor filtering

### Full-Refresh Streams (Not Actionable)

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
| ticket_metrics | No date filter | Zendesk Ticket Metrics API; per-ticket computed metrics |
