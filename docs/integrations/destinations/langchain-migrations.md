# Vector Database (powered by LangChain) Migration Guide

## Upgrading to 0.1.0

This version changes the way record ids are tracked internally. If you are using a stream in **append-dedup** mode, you need to reset the connection after doing the upgrade to avoid duplicates.

Prior to this version, deduplication only considered the primary key per record, without disambiugating between streams. This could lead to data loss if records from two different streams had the same primary key.

The problem is fixed by appending the namespace and stream name to the `_ab_record_id` field to disambiguate between records originating from different streams. If a connection using **append-dedup** mode is not reset after the upgrade, it will consider all records as new and will not deduplicate them, leading to stale vectors in the destination.
