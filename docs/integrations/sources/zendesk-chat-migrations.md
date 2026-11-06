# Zendesk Chat Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 2.0.0

:::danger Risk of permanent data loss
The `chats` fields `deleted`, `update_timestamp` and `engagements` are no longer available after this upgrade. Chats that sync again arrive without these fields, so wherever a new row replaces the old one the stored values are lost, and a clear or a refresh removes the stored values for every chat. Export these columns before upgrading if you need them.
:::

Zendesk [stops serving its Incremental Exports API to third-party integrations](https://support.zendesk.com/hc/en-us/articles/11275429993498) such as Airbyte between December 2, 2026 and January 19, 2027. Version 2.0.0 moves the `chats` stream off that API: chats are now found with the [Search Chats](https://developer.zendesk.com/api-reference/live-chat/chat-api/chats/#search-chats) endpoint and fetched in full with the [List Chats](https://developer.zendesk.com/api-reference/live-chat/chat-api/chats/#list-chats) endpoint. Only the `chats` stream is affected.

What changed in the `chats` stream:

- The cursor field is now `timestamp` (when the chat started) instead of `update_timestamp`. Existing incremental state is migrated automatically, so the next sync continues from where the previous version stopped without skipping chats.
- The fields `deleted`, `update_timestamp` and `engagements` are no longer available from the new endpoints and are removed from the stream schema. `tags` on offline messages, always an empty list before, is now absent. The export also sent a few fields that were never part of the schema and are gone as well: `abandon_time`, `dropped`, `proactive`, `skills_fulfilled` and `skills_requested` on chats.
- Deleted chats are no longer reported. Previously a deleted chat arrived with `deleted` set to `true`; now it disappears from the source and existing rows in your destination are left as they are.
- Chats updated after they first synced are still synced again, because the search covers every chat whose last update falls in the synced window. Every sync also sends again the chats updated during the day before the stream's cursor (a one-day lookback), which the previous version did not do; these repeats carry the same primary key and are deduplicated by destinations that deduplicate.

What to do after upgrading:

- If a connection syncs `chats` incrementally, Airbyte pauses it after the upgrade because its cursor field `update_timestamp` no longer exists in the source. Open the connection, refresh the source schema, accept the new cursor field `timestamp` and resume the connection. When Airbyte then asks whether to clear or refresh the `chats` stream, skip it: no clear is required, the migrated state continues the sync without re-reading from the start date, and a clear or refresh would remove the stored values of the three dropped fields.
- If a connection syncs `chats` in full refresh mode, or does not sync `chats`, no action is required. Refreshing the source schema is optional and only removes the three dropped fields from the catalog.
- Update any downstream query, model or dashboard that reads `chats.deleted`, `chats.update_timestamp` or `chats.engagements`.

## Upgrading to 1.0.0

The Live Chat API [changed its URL structure](https://developer.zendesk.com/api-reference/live-chat/introduction/) to use the Zendesk subdomain.
The `subdomain` field of the connector configuration is now required.
You can find your Zendesk subdomain by following instructions [here](https://support.zendesk.com/hc/en-us/articles/4409381383578-Where-can-I-find-my-Zendesk-subdomain).

## Connector upgrade guide

<MigrationGuide />
