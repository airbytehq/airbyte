# Contributing to source-mailchimp

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

**Connector type:** Hybrid (manifest.yaml + Python custom components for record extraction and config transformation)

**Analysis status:** Complete. 12 streams analyzed. 9 use incremental sync with `since_last_changed` or similar params. 3 are full-refresh.

### Incremental Streams

| Stream | Cursor Field | API Filter | Notes |
|--------|-------------|------------|-------|
| automations | parameterized | `since_last_changed` | Mailchimp Automations API |
| campaigns | parameterized | `since_last_changed` | Mailchimp Campaigns API |
| email_activity | parameterized | `since` | Per-campaign email activity |
| lists | parameterized | `since_last_changed` | Mailchimp Lists/Audiences API |
| list_members | parameterized | `since_last_changed` | Per-list member data |
| reports | parameterized | `since_last_changed` | Campaign reports |
| segments | parameterized | `since_last_changed` | List segments |
| segment_members | parameterized | `since_last_changed` | Per-segment members |
| unsubscribes | parameterized | `since_last_changed` | Unsubscribe events |

### Full-Refresh Streams (Not Actionable)

| Stream | Reason | Evidence |
|--------|--------|----------|
| tags | No date filtering | Mailchimp Tags API has no `since_last_changed` param; small dataset per list |
| interest_categories | No date filtering | Mailchimp Interest Categories API has no date filter; small dataset |
| interests | No date filtering | Mailchimp Interests API has no date filter; child of interest_categories |
