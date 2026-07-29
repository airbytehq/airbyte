# Breaking-Change Criteria for API Source Connectors

This is the **canonical checklist** the breaking-change evaluation step reviews a PR
against. It aggregates Airbyte's breaking-change definitions from the policy docs, the
connector metadata reference, the semantic-versioning handbook, the CI QA checks, and the
`breaking-change-evaluation` skill into one list, scoped to **API source connectors**
(manifest-only, low-code + components, custom Python, file-based API).

An agent using this file should: read the PR diff, apply every criterion below to the
**changed hunks only**, return a **three-state determination**, and — when breaking — check
whether the PR carries the required versioning + metadata + docs so the change is *properly
versioned* rather than an unversioned breaking change (a P0 blocker).

---

## Core principle

> A change is **breaking** if it requires the user to take manual action before they can
> continue syncing, **or** if data that was previously synced will no longer be synced (or
> will change format/semantics).

Anything a user picks up transparently on their next sync — no reconfiguration, no reset,
no downstream rework — is **not** breaking. Assume every breaking change creates friction
and should be avoided when a non-breaking path (including an automated migration) exists.

---

## Three-state determination — do not assert breakage you cannot evidence

Return exactly one of:

| State | When |
|---|---|
| **`BREAKING`** | You can point to evidence that a criterion is met and not neutralised. |
| **`NON_BREAKING`** | You checked every criterion and none is met. |
| **`NEEDS_HUMAN_REVIEW`** | You cannot establish one or more criteria from the available evidence. |

Per criterion, record `met` as **`yes` / `no` / `unknown`** — use `unknown` freely and
honestly.

**Missing evidence is `NEEDS_HUMAN_REVIEW`. It is *not* "`BREAKING` to be safe."** Both
states stop a merge, so nothing unsafe ships either way — but only one of them tells the
author a major version bump is definitely required, and asserting that on a guess is how a
review loses its credibility. When you choose `NEEDS_HUMAN_REVIEW`, list the specific
artefacts a human should check and what each one would settle.

This replaces the older "fail closed: treat it as breaking" rule, which conflated *we don't
know* with *we know it breaks*.

---

## Breaking criteria — a change is breaking if ANY of these is met

Evaluate each against the diff. For every one you mark met, capture `file:line` + the
quoted `+`/`-` line as evidence, and note the affected stream(s).

### Schema / catalog
1. **Field datatype changed** — a property's type changes (e.g. `boolean`→`string`,
   `integer`→`string`, `number`→`string`). See *Data-type compatibility* below: some
   widenings are non-breaking, some are breaking, and semantic-swap changes are always breaking.
2. **JSON Schema `format` hint added, removed, or changed on an existing field** — e.g.
   plain `{"type":"string"}` → `{"type":"string","format":"date-time"}`. This is a breaking
   **type** change, not additive metadata. Typed/normalising destinations (S3 Data Lake &
   Iceberg, BigQuery, Snowflake, Redshift) map `format` to a concrete column type, so adding
   `format: date-time`/`date`/`time` flips a `string` column to `timestamp`/`date`/`time` and
   fails schema evolution on existing connections
   (`Schema evolution for column "…" between string and timestamp is not allowed`). Applies
   whether the change is in a static `schemas/*.json` **or** produced by connector code (a
   Python datatype map, a `JsonSchemaType` mapping, a JDBC `getAirbyteType()` override) —
   inspect the code paths, not just the declarative files.
3. **Field removed or renamed** — a property present in a stream's schema is deleted or
   renamed (data stops flowing / downstream columns break).
4. **Required / nullability narrowed** — a field becomes `required`, or loses its `null`
   type, such that records the connector previously emitted would now be rejected.
5. **Nested object or array-item constraints narrowed** — the same narrowing applied inside
   a nested object or to `items`, where downstream typed destinations will reject
   previously-valid records.
6. **Primary key changed** — a stream's `primary_key` is added, removed, or changed
   (breaks dedup / incremental-dedup destinations).
7. **Cursor field changed** — an incremental stream's `cursor_field` changes **and** no
   state migration is included (see *Migrations*).
8. **Emitted PK / cursor VALUE changed** — the field *names* are unchanged, but a
   transformation, extractor, `record_selector`, or mapping change alters the **value** the
   existing primary-key or cursor field carries (or its type/format). This re-keys records:
   destination rows keyed on the old value no longer match the new ones, breaking
   dedup/upsert and incremental cursor continuity even though the declared field list is
   identical. Inspect record `transformations`, extractor changes, and any code that rewrites
   a PK or cursor field's contents. Easy to miss precisely because the schema diff looks clean.
9. **Stream removed or renamed** — a stream is deleted from the catalog, or its name
   changes (the destination table changes; previously-synced data stops).

### Spec / config
10. **Config field removed or renamed** — a `spec` property is deleted or renamed **and** a
    config migration cannot be applied.
11. **New required config field** — a new **required** `spec` property is added **and** a
    config migration cannot supply a default/transform.
12. **Config shape change** — a `spec` parameter changes shape in a way that invalidates
    existing configs (e.g. a single value becomes a `oneOf`) **and** no config migration applies.

### State
13. **State format changed** — the format/semantics of the connector's saved state changes
    **and** no state migration can transform the old state (forcing a full re-sync the user
    must manage). *(A state-format change that triggers only one automatic full refresh, with
    no user action, is a Patch — not breaking. See handbook.)*
14. **Partition-key shape changed (incremental streams only)** — the **shape** of a
    substream/partition key changes: batching multiple parent IDs into one slice, renaming
    `partition_field`, changing the partition values so new values no longer match old ones
    (or their format changes), or swapping the partition-router class. Incremental state is
    stored **per partition, keyed by the partition value(s)**, so a partition-key change means
    old per-partition state no longer matches the new keys — and vice versa on rollback — even
    when the cursor field and the record schema are untouched. Breaking **unless** a state
    migration is included, both old and new keys are read, or the affected streams are
    full-refresh (full-refresh streams persist no per-partition state, so this does not apply).

### Behavior / data content
15. **Data content semantics changed** — not a schema change, but values change meaning
    (e.g. a field that was lowercased now uppercased; units change; IDs re-encoded) such
    that downstream consumers break.
16. **Non-reversible upgrade** — the new version writes config/state the previous version
    cannot read, so a rollback would break the connection. Treated as a subset of breaking
    changes; must be flagged and versioned even if nothing else here is met.

---

## Migrations — the primary way an otherwise-breaking change stays NON-breaking

For low-code / declarative sources, an automated migration can neutralize criteria 7
(cursor field), 10–12 (spec), and 13–14 (state and partition keys). If the PR includes the
right migration, the criterion is **met but neutralized** (record it as neutralized, not
breaking):

- **Config migrations** — transform old configs to the new shape transparently. Neutralizes
  spec renames/removals/shape-changes and some new-required-field cases.
  (CDK: `airbyte_cdk/sources/declarative/migrations` / the manifest `config_migrations` model.
  Python connectors may instead ship a `config_migrations.py` — check for both.)
- **State migrations** — transform old state to the new format transparently, avoiding a
  full refresh. Neutralizes cursor, state-format, and partition-key changes.
  (CDK: the manifest `state_migrations` model.)

Criteria 1–6, 8, 9, 15, and 16 **cannot** be neutralized by a migration — they change what
lands in the destination, so they need a major version and a migration guide.

**Always check for a migration before concluding a spec/state/cursor change is breaking.**
If a migration is present and covers the change, it is not breaking. If it is absent and
cannot be applied, it is breaking.

---

## Data-type compatibility nuance (criterion 1)

- **Breaking widening** — `float`→`string`, `datetime`→`string`: widens the type but breaks
  downstream numeric/date consumers. **Breaking.**
- **Non-breaking widening** — `int`→`bigint`, `int`→`double`: preserves semantics. **Not breaking.**
- **Semantic swap** — `datetime`→`float`, `number`→`boolean`, etc.: changes the meaning of the
  data. **Breaking; avoid entirely.**
- When unsure, treat a type change as breaking.

---

## What is NOT a breaking change

- Adding a **new stream**, a **new (non-required) config option**, or a **new field** to a
  stream's schema.
- A **state-format change** that causes only a single automatic full refresh with no user
  action (Patch).
- Performance improvements and bug fixes that don't change schema/spec/state/semantics.

**One edge case that still needs handling — high-volume streams:** adding a new stream that
emits ≥2× the volume of existing streams isn't "breaking," but it can overwhelm destinations.
It should be defaulted *out* of `suggestedStreams` and its volume documented. Flag if a new
high-volume stream is added to `suggestedStreams` or without that treatment.

---

## If it IS breaking — required artifacts (the versioning gate)

When the determination is `BREAKING`, the PR is **properly versioned** only if ALL of items
1–5 below are present. Any missing item makes this an **unversioned breaking change → P0
blocker**. Record every missing item explicitly — "which artefact is missing" is the single
most actionable thing this evaluation can tell an author.

1. **Major version bump** — `dockerImageTag` in `metadata.yaml` goes to `N.0.0` (or a minor
   bump for a pre-1.0.0 connector, per Airbyte SemVer). A patch/minor bump on a breaking
   change is the classic red flag.
2. **`releases.breakingChanges` entry** in `metadata.yaml`, keyed by the new version, with:
   - `message` — user-facing: what changed, who's affected, what action to take.
   - `upgradeDeadline` — `YYYY-MM-DD`; **sources: ≥ 7 days out (2 weeks recommended)**. May be
     present-day/past only for an already-broken upstream (removed API endpoint) — say which
     case applies. **An invalid deadline fails this gate**; do not treat the field's mere
     presence as sufficient.
   - `scopedImpact` *(recommended when applicable)* — `scopeType: stream` + `impactedScopes`
     listing only the affected streams, so unaffected users aren't alerted.
   - `deadlineAction` *(optional)* — `auto_upgrade` (platform default) or `disable`. Use
     `disable` only when a config change genuinely can't be migrated.
3. **Migration guide** — `docs/integrations/sources/<slug>-migrations.md` with a section
   for the new version covering WHAT / WHY / WHO / STEPS. **CI fails without this.**
   (`<slug>` is the connector directory name without the `source-` prefix.)
4. **Changelog entry** — a row for the new version in `docs/integrations/sources/<slug>.md`.
5. **PR conventions** — `!` in the PR title's conventional-commit type (e.g. `fix!:`) **and**
   the `breaking-change` label. Both are mechanically checkable from
   `gh pr view --json title,labels` and both are part of the gate, not advisory.

Two further policy requirements that **cannot** be verified from the repo. Report them as
required human actions rather than silently dropping them:

6. **Breaking-change reviewer approval** — `@airbytehq/breaking-change-reviewers` must
   approve. CODEOWNERS requests them automatically on migration-guide changes, so check
   whether the review was requested; approval state itself is a human gate.
7. **Release playbook** — an Airbyte engineer must complete the Connector Breaking Change
   Release Playbook before merging. Always surface this as an outstanding action on a
   breaking PR.

If the change is so large it would break *all* downstream SQL/BI (full rewrite), the guidance
is a **`-gen2` connector** with a new connector ID rather than a breaking major bump.

---

## Sources

> Note for agents reading this file at runtime: the first four paths are **local** to the
> airbyte repo and can be opened directly. The platform-schema paths at the bottom live in a
> **different repository** (`airbyte-platform-internal`) and are cited for provenance only —
> do not try to read them.

- `docs/platform/connector-development/connector-breaking-changes.md` — the policy
  ([public](https://docs.airbyte.com/platform/connector-development/connector-breaking-changes))
- `docs/platform/connector-development/connector-metadata-file.md` — `breakingChanges` /
  `scopedImpact` schema
- `docs/community/contributing-to-airbyte/resources/pull-requests-handbook.md` — SemVer +
  change→version table
- `docs/community/contributing-to-airbyte/resources/qa-checks.md` — CI enforcement
  (migration guide required; deadline ≥ 1 week; SemVer)
- `shared-airbyte-skills:breaking-change-evaluation` — the diff-level gate, and the source
  for criteria 2 (`format` hints), 8 (emitted PK/cursor values) and 14 (partition-key shape).
  Keep this file in sync when that skill adds a criterion.
- Platform schema (source of truth): `airbyte-config/config-models/.../types/VersionBreakingChange.yaml`,
  `BreakingChangeScope.yaml`; `SupportStateUpdater.kt` (`deadlineAction` = `auto_upgrade`|`disable`)
- Live example: `airbyte-integrations/connectors/source-faker/metadata.yaml` (v7.0.0)
