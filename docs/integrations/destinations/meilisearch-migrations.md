# MeiliSearch Migration Guide

## Upgrading to 2.0.0

Version 2.0.0 changes how documents are identified in Meilisearch.

Version 1.x assigned every record a random value in an internal `_ab_pk` field and used that
field as the index primary key. Version 2.0.0 uses the stream's real primary key as the
Meilisearch index primary key whenever the stream has a single top-level primary-key field
(enabling upserts and deduplication); the internal `_ab_pk` field is only used for streams with
no primary key or with a composite/nested key.

Meilisearch does not allow changing an index's primary key while it contains documents.
Indexes created by version 1.x therefore have a primary key of `_ab_pk`, and a 2.0.0 sync that
resolves a different primary key will refuse to run with an error like:

```
Index 'my_stream' already has primary key '_ab_pk', but this sync resolved primary key 'id'.
```

### What to do

For each affected stream, do **one** of the following:

1. **Run the stream in "Full refresh | Overwrite" mode once.** Overwrite mode deletes and
   recreates the index, which resets its primary key. You can switch back to your preferred
   sync mode afterwards.
2. **Delete the index manually** in Meilisearch (`DELETE /indexes/:index_uid`), then run a sync.
   The next sync recreates the index with the correct primary key.

Streams that sync in `append` mode (or that have no primary key) are unaffected: they continue
to use the `_ab_pk` field and existing indexes keep working.

Also note: when the stream's real primary key is used, its values must be Meilisearch-compatible
document ids — an integer, or a string containing only `a-z A-Z 0-9`, `-` and `_`. Records with
other values (for example emails) are rejected with an error naming the offending field.
