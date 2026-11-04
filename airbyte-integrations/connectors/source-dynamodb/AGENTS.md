> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-dynamodb: Contributor notes

`source-dynamodb` is a Kotlin connector on the Bulk CDK. Standard local
commands:

```bash
./gradlew :airbyte-integrations:connectors:source-dynamodb:test
./gradlew :airbyte-integrations:connectors:source-dynamodb:assemble
./gradlew :airbyte-integrations:connectors:source-dynamodb:dockerBuildx
```

## Reproducing bugs locally

Use the
[`source-dynamodb-e2e-tests`](.agents/skills/source-dynamodb-e2e-tests/SKILL.md)
skill for full-refresh and cursor-incremental local sweeps. It stands up a
DynamoDB Local backend (`source-dynamodb-db-backend`), applies JSON fixtures
with the AWS CLI, and sweeps `spec` → `check` → `discover` → `read` against
`airbyte/source-dynamodb:<tag>`. Orchestration is delegated to
[`airbyte-integrations/db-harness-lib/`](../../db-harness-lib/).

There is no CDC mode. Assume-role / IAM / STS behavior is also not covered:
DynamoDB Local has no STS, and the connector's `endpoint` only overrides the
DynamoDB client, so a published image cannot send AssumeRole to this emulator.
If the reported failure depends on one of those behaviors, say so in the
evidence plan rather than forcing the generic skill to claim coverage.

```bash
cd airbyte-integrations/connectors/source-dynamodb

# Single-version sweep
poe e2e-local --test-version=<tag>

# Prove-fix comparison (target vs. known-bad control)
poe e2e-local --test-version=<tag> --control-version=<control-tag>
```

**Never** repro against a customer connection, real AWS account, or Airbyte
Cloud instance.
