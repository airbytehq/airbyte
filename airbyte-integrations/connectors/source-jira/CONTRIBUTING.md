# Contributing to source-jira

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

**Connector type:** Hybrid (manifest.yaml + Python custom components for record extraction, partition routing, and field transformation)

**Analysis status:** Complete. 57 streams analyzed. 6 use incremental sync via `DatetimeBasedCursor` with `updated` cursor field or semi-incremental client-side filtering. 51 are full-refresh. Most full-refresh streams are Jira configuration/metadata endpoints that lack date-based filtering.

PR airbytehq/airbyte#76840 is in flight for inert-flag cleanup and verification.

### Incremental Streams

| Stream | Cursor Field | Pattern | Notes |
|--------|-------------|---------|-------|
| issues | updated | `DatetimeBasedCursor` | JQL `updated >` filter |
| board_issues | updated | `DatetimeBasedCursor` | Per-board issues with JQL filter |
| sprint_issues | updated | `DatetimeBasedCursor` | Per-sprint issues with JQL filter |
| issue_changelogs | updated | `DatetimeBasedCursor` | Per-issue changelogs |
| issue_comments | updated | `semi_incremental` (client-side) | Per-issue comments; client-side cursor filtering |
| issue_worklogs | updated | `semi_incremental` (client-side) | Per-issue worklogs; client-side cursor filtering |

### Full-Refresh Streams (Not Actionable)

| Stream | Category | Reason |
|--------|----------|--------|
| application_roles | Config | Jira Application Roles API; no date filter; small dataset |
| avatars | Config | Jira Avatars API; no date filter |
| boards | Config | Jira Boards API; no `updatedSince` param |
| dashboards | Config | Jira Dashboards API; no date filter |
| filters | Config | Jira Filters API; no `updatedSince` param |
| filter_sharing | Substream | Per-filter sharing; no date filter |
| groups | Config | Jira Groups API; no date filter |
| issue_fields | Config | Jira Fields API; no date filter; small dataset |
| issue_field_configurations | Config | Jira Field Configurations API; no date filter |
| issue_custom_field_contexts | Config | Per-field contexts; no date filter |
| issue_custom_field_options | Config | Per-field options; no date filter |
| issue_link_types | Config | Jira Issue Link Types API; small dataset |
| issue_navigator_settings | Config | Jira Navigator Settings API; single record |
| issue_notification_schemes | Config | Jira Notification Schemes API; no date filter |
| issue_priorities | Config | Jira Priorities API; small dataset |
| issue_property_keys | Substream | Per-issue property keys; no date filter |
| issue_properties | Substream | Per-issue properties; no date filter |
| issue_remote_links | Substream | Per-issue remote links; no date filter |
| issue_resolutions | Config | Jira Resolutions API; small dataset |
| issue_security_schemes | Config | Jira Security Schemes API; no date filter |
| issue_transitions | Substream | Per-issue transitions; no date filter |
| issue_type_schemes | Config | Jira Issue Type Schemes API; no date filter |
| issue_type_screen_schemes | Config | Jira Issue Type Screen Schemes API; no date filter |
| issue_types | Config | Jira Issue Types API; small dataset |
| issue_votes | Substream | Per-issue votes; no date filter |
| issue_watchers | Substream | Per-issue watchers; no date filter |
| jira_settings | Config | Jira Settings API; single record |
| labels | Config | Jira Labels API; no date filter |
| permissions | Config | Jira Permissions API; single record |
| permission_schemes | Config | Jira Permission Schemes API; no date filter |
| projects | Config | Jira Projects API; no `updatedSince` param |
| project_avatars | Substream | Per-project avatars; no date filter |
| project_categories | Config | Jira Project Categories API; no date filter |
| project_components | Substream | Per-project components; no date filter |
| project_email | Substream | Per-project email; no date filter |
| project_permission_schemes | Substream | Per-project permissions; no date filter |
| project_roles | Substream | Per-project roles; no date filter |
| project_types | Config | Jira Project Types API; small dataset |
| project_versions | Substream | Per-project versions; no date filter |
| screens | Config | Jira Screens API; no date filter |
| screen_schemes | Config | Jira Screen Schemes API; no date filter |
| screen_tabs | Substream | Per-screen tabs; no date filter |
| screen_tab_fields | Substream | Per-tab fields; no date filter |
| sprints | Config | Jira Sprints API; no `updatedSince` param |
| time_tracking | Config | Jira Time Tracking API; single record |
| users | Config | Jira Users API; no date filter |
| users_groups_detailed | Config | Per-user group details; no date filter |
| workflow_schemes | Config | Jira Workflow Schemes API; no date filter |
| workflow_status_categories | Config | Jira Workflow Status Categories API; small dataset |
| workflow_statuses | Config | Jira Workflow Statuses API; small dataset |
| workflows | Config | Jira Workflows API; no date filter |
