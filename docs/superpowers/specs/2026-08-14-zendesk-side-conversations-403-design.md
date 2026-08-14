# Zendesk Side Conversations 403 Recovery Design

## Context

The `zendesk-all-streams-incremental` connection failed 146 consecutive times because the Zendesk Support connector treats every `403` from `GET /api/v2/tickets/{ticket_id}/side_conversations` as a stream-level configuration error. The failing partitions are deleted or otherwise inaccessible tickets. This single optional substream prevented the 40 core Zendesk streams from completing.

The stream is temporarily isolated in the inactive manual connection `zendesk-side-conversations-quarantine`. The main connection is healthy without it.

## Goal

Restore `side_conversations`, prove that valid partitions still return data, then merge the stream and its state back into the main 30-minute connection without allowing ticket-specific failures to block core Zendesk ingestion.

## Considered Approaches

1. **Ignore every `403` in the manifest.** Smallest change, but unsafe: revoked account permissions would look like a successful zero-row sync and advance state.
2. **Exclude deleted tickets in the parent stream.** Avoids known deleted-ticket failures, but does not cover other ticket-specific access restrictions and couples child behavior to the shared tickets stream.
3. **Ignore ticket-partition `403/404` responses, with an external access/data canary before merge.** Recommended. This matches the connector's existing `422` partition-skip behavior while preventing a global permission regression from reaching production unnoticed.

## Design

- Change only the `side_conversations` requester's response filters.
- Treat `403`, `404`, and the existing `422` as an ignored ticket partition. Log an explicit message that the ticket is deleted, inaccessible, or does not support side conversations.
- Preserve all other error handling and retries.
- Add mock-server regression tests proving:
  - a `403` partition is skipped and later valid ticket partitions still emit records;
  - a `404` partition is skipped and later valid ticket partitions still emit records;
  - non-partition server errors still fail the stream.
- Build a uniquely tagged connector image and assign it only to the quarantined connection first.
- Before accepting the quarantine run, require both:
  - at least one known historical side-conversation ticket is successfully accessible/emitted;
  - the full sync completes without connector failures and reconciles against the existing BigQuery primary keys.
- Run a second incremental sync and require no duplicate primary keys and a stable cursor.
- Transfer the quarantine stream state to the main connection, re-add `side_conversations`, and run the combined connection.
- Remove the quarantine connection only after the combined run succeeds and BigQuery freshness/count checks pass.

## Failure Safety

The patch deliberately avoids changing authentication checks or source connection checks. The production rollout gate prevents a globally unauthorized credential from being merged: if known valid tickets do not return data, the quarantine remains isolated and the Zendesk permission must be corrected instead.

## Rollback

If quarantine validation or the combined run fails, remove `side_conversations` from the main catalog, restore the previous Zendesk connector image, and leave the quarantine inactive. The 40-stream main pipeline and existing `side_conversations` table remain available throughout.
