# Zendesk Side Conversations 403 Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ticket-specific Zendesk side-conversation authorization failures non-fatal, validate the stream in isolation, and merge its cursor back into the main 30-minute connection.

**Architecture:** Extend the existing declarative requester error policy for the `side_conversations` substream only. Roll the image through an isolated Airbyte connection, require a successful historical-data canary and incremental checkpoint, then copy state and catalog configuration into the main connection.

**Tech Stack:** Airbyte declarative connector manifest, Python 3.12, pytest/http-mocker, Docker/Google Artifact Registry, Airbyte internal API, BigQuery.

## Global Constraints

- Do not change any stream other than `side_conversations`.
- Do not silently accept global permission loss: quarantine must emit/reconcile known historical records before merge.
- Keep the 40-stream main connection healthy until quarantine validation passes.
- Preserve incremental state during the merge.

---

### Task 1: Partition-Level Error Regression Tests

**Files:**
- Modify: `airbyte-integrations/connectors/source-zendesk-support/unit_tests/mock_server/test_side_conversations.py`
- Modify: `airbyte-integrations/connectors/source-zendesk-support/manifest.yaml:1009-1040`

**Interfaces:**
- Consumes: existing `read_stream`, `given_tickets`, `ErrorResponseBuilder`, and side-conversation request/response builders.
- Produces: manifest behavior where `403`, `404`, and `422` skip only the affected parent-ticket partition.

- [ ] **Step 1: Add a failing 403 continuation test**

Create two ticket partitions. Return `403` for the first ticket and a valid side-conversation response for the second. Assert that the output contains exactly the valid second record.

- [ ] **Step 2: Run the 403 test and verify RED**

Run: `poetry run pytest -q mock_server/test_side_conversations.py::TestSideConversationsErrorHandling::test_given_403_for_one_ticket_when_read_then_skip_partition_and_continue`

Expected: FAIL with an `AirbyteTracedException` because the manifest currently uses `action: FAIL` for `403`.

- [ ] **Step 3: Add a failing 404 continuation test**

Use the same two-partition shape, return `404` for the first ticket, and assert that the second ticket's record is emitted.

- [ ] **Step 4: Run the 404 test and verify RED**

Run: `poetry run pytest -q mock_server/test_side_conversations.py::TestSideConversationsErrorHandling::test_given_404_for_one_ticket_when_read_then_skip_partition_and_continue`

Expected: FAIL with an `AirbyteTracedException`.

- [ ] **Step 5: Implement the minimal manifest policy**

Replace the `403/404` FAIL filter under `side_conversations_stream` with:

```yaml
- http_codes: [403, 404]
  action: IGNORE
  error_message: "Skipping side conversations for this ticket because it is deleted or inaccessible. Other tickets will continue to sync normally."
```

- [ ] **Step 6: Run targeted and complete stream tests**

Run:

```bash
poetry run pytest -q mock_server/test_side_conversations.py
```

Expected: all tests pass.

- [ ] **Step 7: Commit the connector fix**

```bash
git add airbyte-integrations/connectors/source-zendesk-support/manifest.yaml \
  airbyte-integrations/connectors/source-zendesk-support/unit_tests/mock_server/test_side_conversations.py
git commit -m "fix(source-zendesk-support): skip inaccessible side conversation tickets"
```

### Task 2: Build and Quarantine Validation

**Files:**
- No source changes.

**Interfaces:**
- Consumes: the connector source from Task 1 and Airbyte connection `7378106a-ac76-4e22-9d81-8e15e857dd54`.
- Produces: a uniquely tagged Artifact Registry image and a successful full/incremental Airbyte state for `side_conversations`.

- [ ] **Step 1: Run the connector's complete unit-test suite**

Run: `poetry run pytest -q`

Expected: zero failed tests.

- [ ] **Step 2: Build and publish the image**

Use the repository's connector build command to build `source-zendesk-support`, tag it in `us-central1-docker.pkg.dev/dogwood-baton-345622/airbyte-connectors` with a unique `side403fix` tag, authenticate Docker through `gcloud`, and push it.

- [ ] **Step 3: Point only the quarantine connection's source definition at the custom image**

Update the Airbyte Zendesk source definition image tag, keep the main connection without `side_conversations`, activate the quarantine connection as manual, and trigger its first sync.

- [ ] **Step 4: Validate the quarantine full/catch-up sync**

Require Airbyte job success, at least the existing 1,182 distinct IDs in BigQuery after append-dedup, at least one emitted/committed record, no duplicate `id`, and a non-null stream state.

- [ ] **Step 5: Trigger and validate a second incremental sync**

Require success, stable distinct-ID count unless Zendesk has genuinely changed, no duplicate `id`, and state at or beyond the first run's cursor.

### Task 3: State-Preserving Main Merge

**Files:**
- No source changes.

**Interfaces:**
- Consumes: validated quarantine catalog/state and the main connection `4b05eec4-2430-44c8-91a6-c04c2beaad13`.
- Produces: one active 41-stream connection on a 30-minute schedule.

- [ ] **Step 1: Snapshot both connection catalogs and states**

Read and retain the main catalog/state and quarantine catalog/state before mutation for rollback.

- [ ] **Step 2: Add `side_conversations` back to the main catalog**

Copy the validated stream configuration from quarantine into the main catalog while preserving all 40 existing stream configurations and the 30-minute basic schedule.

- [ ] **Step 3: Transfer the per-stream state**

Use Airbyte's state API to copy the quarantine `side_conversations` stream descriptor/state into the main connection without replacing other stream states.

- [ ] **Step 4: Trigger and verify the combined sync**

Require Airbyte job success, emitted records equal committed records, all 41 stream statuses terminal-successful, BigQuery core freshness current, `side_conversations` distinct IDs not lower than quarantine, and zero duplicate IDs.

- [ ] **Step 5: Retire quarantine**

Set quarantine inactive and keep it for rollback until a later cleanup; do not delete its BigQuery table or state during this change.

- [ ] **Step 6: Final verification**

Re-read the main connection to prove: active status, 30-minute basic schedule, 41 selected streams including `side_conversations`, latest job succeeded, and no failure summary.
