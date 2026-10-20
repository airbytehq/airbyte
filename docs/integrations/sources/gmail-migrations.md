import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Gmail Migration Guide

## Upgrading to 1.0.0

### What changes

The `profile` stream now uses `emailAddress` as its primary key. The following fields change from `number` to `integer`; their nullable values are unchanged:

- `profile`: `messagesTotal`, `threadsTotal`
- `labels_details`: `messagesTotal`, `messagesUnread`, `threadsTotal`, `threadsUnread`
- `messages_details`: `sizeEstimate`, `payload.body.size`, `payload.parts[].body.size`, `payload.parts[].parts[].body.size`, and `payload.parts[].parts[].parts[].body.size`
- `threads_details`: `messages[].sizeEstimate`, `messages[].payload.body.size`, `messages[].payload.parts[].body.size`, `messages[].payload.parts[].parts[].body.size`, and `messages[].payload.parts[].parts[].parts[].body.size`

### Why

The [Gmail API](https://gmail.googleapis.com/$discovery/rest?version=v1) documents the affected count and size values as int32 integers. The profile endpoint returns one record for the authenticated mailbox, and `emailAddress` identifies that record so destinations can deduplicate profile syncs.

### Who is affected

This affects connections syncing `profile`, `labels_details`, `messages_details`, or `threads_details`. Typed destinations and downstream queries or models that expect decimal count/size columns or the previous profile row identity may need updates. Only `messages_details` supports incremental sync; the other affected streams use full refresh. This is especially relevant to `messages_details` using **Incremental | Append + Deduped** and `profile` using **Full Refresh | Overwrite + Deduped**.

### Steps

1. Upgrade the Gmail source to version 1.0.0.
2. Refresh the source schema for each affected connection and review the detected changes before saving.
3. For affected streams using append-based modes, including incremental `messages_details`, or for destinations that cannot safely evolve the typed columns in place, rebuild the stream data using **Refresh stream** → **Refresh stream and remove records**. A normal sync rebuilds streams using **Full Refresh | Overwrite**, so those streams do not need a separate data refresh.
4. Update downstream queries, models, or exports that depend on the changed column types or profile key.

:::danger
**Refresh stream and remove records** deletes the existing destination rows before re-syncing. Gmail can only return messages that are still available and allowed by the connection's start date and spam/trash settings; deleted or excluded messages may not be recoverable from the source. Back up affected destination data before removing records if you need to preserve it.
:::

For more information about refresh options, see [Refresh data](/platform/operator-guides/refreshes).

<MigrationGuide />
