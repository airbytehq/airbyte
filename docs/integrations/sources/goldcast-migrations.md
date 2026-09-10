# Goldcast Migration Guide

## Upgrading to 1.0.0

:::note
This change is only breaking if you are syncing the `event_members` stream and reading fields inside `props`.
:::

`props` carries Goldcast **registration form fields**, which every workspace defines for itself. Until now the schema enumerated a fixed list of eleven of them (`city`, `solutions`, `tag_source`, `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `tag_country`, `tag_form_type`, `revenue_type`, `contact_job_title`). Any other registration field was undeclared, and on V2 destinations undeclared properties are dropped silently — they do not even appear in `_airbyte_meta.changes[]`.

`props` is now a schemaless object. V2 destinations serialise a schemaless object to a JSON string, so **every** field **every** workspace defines is preserved, and no future schema change is needed when a workspace adds one.

The trade-off is that `props` is delivered as a JSON string rather than a set of nested columns.

Users should:

- Refresh the source schema for the `event_members` stream.
- Reset the stream after upgrading to ensure uninterrupted syncs.
- Update any downstream query that reads `props.<field>` as a nested column, extracting the value from the JSON string instead. In BigQuery, for example, `props.city` becomes `JSON_VALUE(props, '$.city')`; the equivalent is `props:city::string` in Snowflake and `props->>'city'` in Postgres.

### Refresh affected schemas and reset data

1. Select **Connections** in the main nav bar.
   1. Select the connection affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.
3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Reset affected streams** option is checked.
4. Select **Save connection**.

This will reset the data in your destination and initiate a fresh sync.
