# Zendesk Chat Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 2.0.0

Zendesk [stops serving its Incremental Exports API to third-party integrations](https://support.zendesk.com/hc/en-us/articles/11275429993498) such as Airbyte between December 2, 2026 and January 19, 2027. Version 2.0.0 moves the `chats` stream off that API: chats are now found with the [Search Chats](https://developer.zendesk.com/api-reference/live-chat/chat-api/chats/#search-chats) endpoint and fetched in full with the [List Chats](https://developer.zendesk.com/api-reference/live-chat/chat-api/chats/#list-chats) endpoint. Only the `chats` stream is affected.

What changed in the `chats` stream:

- The cursor field is now `timestamp` (when the chat started) instead of `update_timestamp`. Existing incremental state is migrated automatically, so the next sync continues from where the previous version stopped without skipping chats.
- The fields `deleted`, `update_timestamp` and `engagements` are no longer available from the new endpoints. They are removed from the stream schema and stay empty in new records. Columns already created in your destination are kept but no longer filled.
- Deleted chats are no longer reported. Previously a deleted chat arrived with `deleted` set to `true`; now it disappears from the source and existing rows in your destination are left as they are.
- Chats updated after they first synced are still synced again, because the search covers every chat whose last update falls in the synced window.

No clear is required. After upgrading, refresh the source schema in the connection if you want the removed fields to disappear from the catalog, and update any downstream query, model or dashboard that reads `chats.deleted`, `chats.update_timestamp` or `chats.engagements`.

## Upgrading to 1.0.0

The Live Chat API [changed its URL structure](https://developer.zendesk.com/api-reference/live-chat/introduction/) to use the Zendesk subdomain.
The `subdomain` field of the connector configuration is now required.
You can find your Zendesk subdomain by following instructions [here](https://support.zendesk.com/hc/en-us/articles/4409381383578-Where-can-I-find-my-Zendesk-subdomain).

## Connector upgrade guide

<MigrationGuide />
