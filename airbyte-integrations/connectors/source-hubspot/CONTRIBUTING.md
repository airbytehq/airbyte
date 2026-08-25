# Contributing to source-hubspot

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

**Connector type:** Hybrid (manifest.yaml + Python custom components for error handling, property history extraction, state migration, and field transformation)

**Analysis status:** Complete. 36 streams analyzed. 31 use incremental sync via various cursor strategies (CRM search API, property history cursors, standard `updatedAt`). 5 are full-refresh.

### Incremental Streams (31)

The connector implements incremental sync using multiple patterns:
- **CRM Search API streams** (companies, contacts, deals, leads, tickets, etc.): Use HubSpot's search endpoint with `lastmodifieddate` filter
- **Property history streams** (companies/contacts/deals_property_history): Use `timestamp` cursor
- **Standard cursor streams** (campaigns, contact_lists, deal_pipelines, email_events, engagements, forms, goals, line_items, marketing_emails, owners, products, subscription_changes, ticket_pipelines, workflows): Use `updatedAt`, `lastUpdated`, `created`, or similar cursors

| Key Streams | Cursor Field | Pattern |
|-------------|-------------|---------|
| companies, contacts, deals, leads, tickets | `lastmodifieddate` | CRM Search API |
| engagements_calls/emails/meetings/notes/tasks | `lastUpdated` | CRM Search API |
| campaigns | `lastUpdatedTime` | Standard cursor |
| email_events | `created` | Standard cursor |
| subscription_changes | `timestamp` | Standard cursor |

### Full-Refresh Streams (Not Actionable)

| Stream | Reason | Evidence |
|--------|--------|----------|
| list_memberships | Substream of contact_lists; no independent date filter | Per-list endpoint |
| email_subscriptions | No `updatedAt` field | HubSpot Email Subscriptions API returns current state only |
| users | No date filtering support | HubSpot Users API has no `updatedAt` or `modified_after` |
| properties | Configuration metadata; no date filter | HubSpot Properties API returns all property definitions |
| account_details | Single record | Returns one account object; no date relevance |
