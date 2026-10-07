import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# AssemblyAI Migration Guide

## Upgrading to 1.0.0

:::danger Optional backfill can delete historical data

Clearing `transcripts` deletes destination data. Back up the affected tables before an optional backfill: AssemblyAI's listing API cannot recover transcripts older than 90 days.

:::

### What changed

The `lemur_response` stream and its optional `request_id` setting have been removed. The four transcript streams retain their names, schemas, primary keys, and state format. This release also fixes API-key authentication, pagination to older transcripts, and parsing of transcript timestamps without a trailing `Z`.

### Why

AssemblyAI [deprecated LeMUR on March 31, 2026](https://www.assemblyai.com/llms/models.md). Its `GET /lemur/v3/{request_id}` retrieval endpoint now returns HTTP 404. The replacement [LLM Gateway](https://assemblyai.com/docs/faq/how-do-i-switch-from-lemur-to-llm-gateway) generates new responses via a chat-completions request; it is not a documented replacement for retrieving previously generated LeMUR responses.

### Who is affected

Connections that select `lemur_response` must update their configured catalog. Connections selecting only transcript streams do not need a schema or state migration.

### Migration steps

1. Upgrade the AssemblyAI connector to version 1.0.0 or later.
2. For each affected connection, open the **Schema** tab and select **Refresh source schema**. Accept the removal of `lemur_response` and save the catalog. For API-managed connections, remove `lemur_response` from the configured catalog.
3. Remove `request_id` from manually managed source configurations. Existing configurations containing it remain accepted, but it is no longer used.
4. Run a sync of the remaining streams. No data reset is required to remove LeMUR; existing destination data is not a source for new LLM Gateway responses.

An **optional** backfill can recover transcripts missed by the previous pagination bug. Back up the destination tables first, then clear and resync the `transcripts` stream if needed. The re-sync is bounded by `start_date` and AssemblyAI's 90-day listing retention; older history cannot be recovered from this API. Skipping the backfill leaves previously missed records before the saved cursor absent from the destination.

### Downstream consumers

Update any SQL, dbt models, dashboards, or exports that expect new `lemur_response` records (`request_id`, `response`, and `usage`). Historical data does not become LLM Gateway data automatically; applications using LLM Gateway must persist its generated responses themselves.

## Connector upgrade guide

<MigrationGuide />
