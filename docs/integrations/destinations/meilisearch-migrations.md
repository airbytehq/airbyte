# Meilisearch Migration Guide

## Upgrading to 2.0.0

Version 2.0.0 is a rewrite of the connector. Indexes written by earlier versions can't be updated in
place, so plan to rebuild them.

### Index names

Indexes of streams with a namespace are now named `<namespace>_<stream>` instead of `<stream>`.
Characters other than letters, numbers, `-` and `_` are replaced by `_`. Streams without a namespace
keep the same index name.

### Document IDs

The `_ab_pk` attribute is still the primary key of every index, but its value has changed:

- For streams synced with deduplication (**Incremental | Append + Deduped**, which is now
  supported), it is derived from the record's primary key, so a record replaces the document with
  the same key. Records with `_ab_cdc_deleted_at` set delete the document.
- For other streams, it is a random ID, as before.

### Overwrites and refreshes

Documents now have an `_airbyte_generation_id` attribute. When a stream is overwritten or
refreshed, the index and its settings are kept, and the documents of earlier syncs are deleted once
the stream has been synced completely, instead of the index being deleted at the start of the sync.

### How to upgrade

1. Upgrade the destination to 2.0.0.
2. Delete the indexes written by earlier versions of the connector. Note any index settings you
   configured, such as searchable, filterable or sortable attributes, so you can apply them again.
3. Refresh or reset the connections that use the destination, so that every stream is synced again
   into its new index.
4. Apply your index settings to the new indexes.
