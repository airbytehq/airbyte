---
name: connector-certification-criteria
description: The certification criteria register for Airbyte manifest-only API source connectors. Defines every criterion, how to evaluate it, how to remediate it, and who owns it. Use when evaluating whether a connector meets the certified bar, or when building/running the certification evaluator.
devin-enabled: true
icon: shield-check
---

# Connector Certification Criteria (v2)

The quality bar a manifest-only API source connector must meet to be classified **certified**
(`supportLevel: certified`). Certified connectors are Airbyte-maintained, production-ready, and eligible
for support SLAs.

**Certification transfers ownership.** Once certified, the connector is enrolled in monthly automated CDK
upgrades, blocks CI on standard-test failures, and its production failures are ours to fix. The criteria
below are the entry bar; the maintenance obligation is permanent.

## Scope

**Manifest-only connectors only.** A connector with `components.py` is still manifest-only and in scope —
the distinction is `language:manifest-only` in metadata tags, not the absence of Python.

Non-manifest-only connectors (Python CDK, low-code with a `source_*` package, Java) are **rejected at the
gate**, not remediated. Migration to manifest-only is its own project and must complete before a
certification evaluation is meaningful.

## How to read this register

Every criterion carries the same fields so the evaluator can compile it mechanically:

| Field | Meaning |
|---|---|
| **Blocking** | Must pass to certify. **Recommended** items are reported but do not gate. |
| **Owner** | `agent` · `agent+external` (needs gh/Exa/ops-mcp) · `agent+creds` (needs GSM secrets) · `human` |
| **Group** | Criteria sharing a group collapse into one sub-issue |
| **Check** | How to evaluate — exact command, path, or query |
| **Pass when** | The condition, including what counts as a documented exception |
| **Fix** | What the remediation sub-issue instructs |

Groups map 1:1 to sub-issues of the certification epic. A criterion whose Owner is `human` always gets its
own sub-issue regardless of group, because it needs a different actor.

### ⚠️ Breaking-change flag

Several remediations below are **breaking changes** under the existing policy. Each carries a
**⚠️ May be breaking** line naming the mechanism. Do not re-derive the policy here — run the
`breaking-change-evaluation` skill on the actual diff, then follow
`docs/platform/connector-development/connector-breaking-changes.md`: major version bump, a
`releases.breakingChanges` entry, a migration guide, `@airbytehq/breaking-change-reviewers` approval, the
`breaking-change` label, a `!` in the PR title, and an engineer completing the internal release playbook.

**A certification epic ships at most one breaking release.** Flagged criteria are batched together
regardless of group — see *Breaking changes: one release, not one per group* in the
`certify-connector` skill. Shipping `schema` and
`incremental` as separate major versions would force two migration guides and two upgrade deadlines on
customers for a single certification.

Where a migration removes the break — a config migration for spec changes, a state migration for cursor or
partition-key changes — define it in the same PR and the change is no longer breaking. Prefer that path.

---

## 0 · Gate

### G-1 · Connector is manifest-only
**Blocking** · Owner: `agent` · Group: `gate`

- **Check:** `yq -r '.data.tags[] | select(test("^language:"))' metadata.yaml`
- **Pass when:** the tag is `language:manifest-only`. A `components.py` file is permitted.
- **Fix:** none. **Stop the evaluation and report ineligible.** Do not file a certification epic; do not
  file a migration issue as a sub-issue. Migration is prerequisite work tracked separately.

---

## 1 · Metadata & registry

### M-1 · Support level and internal tiering
**Blocking** · Owner: `agent` · Group: `metadata`

- **Check:** `metadata.yaml` → `data.supportLevel`, `data.releaseStage`, `data.ab_internal.ql`, `data.ab_internal.sl`
- **Pass when:** `supportLevel: certified`, `releaseStage: generally_available`, `ab_internal.ql: 300`,
  `ab_internal.sl: 200`.
- **Note:** these `ab_internal` values are forward-looking for new certifications. Existing certified
  connectors sit at 400/300 or 200/200 and are not expected to match.
- **Fix:** set the four fields. This is the **last** PR in the epic — it flips the connector to certified
  and must not merge until every other blocking criterion passes.

### M-2 · AllowedHosts is minimal and templated
**Blocking** · Owner: `agent` · Group: `metadata`

- **Check:** `metadata.yaml` → `data.allowedHosts.hosts`
- **Pass when:** present, enumerates only hosts the connector actually contacts, contains no bare wildcard
  (`*`, `*.com`), and templates user-supplied hosts from config —
  e.g. `{{ config['subdomain'] }}.zendesk.com`.
- **Fix:** enumerate real hosts from the manifest's `url_base` values and any auth/token endpoints.

### M-3 · Heartbeat timeout is set
**Blocking** · Owner: `agent` · Group: `metadata`

- **Check:** `metadata.yaml` → `data.maxSecondsBetweenMessages`
- **Pass when:** set to the true maximum expected gap between emitted records, taking the highest value
  across all streams.
- **Note:** this is a **heartbeat timeout** — how long the platform tolerates no record being read or
  extracted before failing the sync. It is not a rate-limit declaration. Do not gate it on a rate-limit
  threshold.
- **Fix:** derive from the slowest stream's realistic worst case (large partition, report generation
  latency, retry-with-backoff ceiling).

### M-4 · Suggested streams are a usable default
**Blocking** · Owner: `agent+external` · Group: `metadata`

- **Check:** `metadata.yaml` → `data.suggestedStreams.streams`
- **Pass when:** the key is **present** and lists 3–10 streams, including the connector's headline
  entities. Omission is not an acceptable exception — see below.
- **Absent is not empty.** `SuggestedStreams.yaml` defines the semantics explicitly: *"SuggestedStreams
  not being present for the source means that all streams are suggested. An empty list here means that no
  streams are suggested."* A connector that omits the key pre-selects **every** stream on every new
  connection. For a dynamic-stream connector — the case most often assumed to be exempt — that is the
  worst available default, not a legitimate one.
- **Why the bound:** suggested streams also determine what `airbyte-cdk image test` reads by default.
  `docker_base.py` intersects discovered streams with `suggestedStreams` only when the key is truthy, so a
  connector with 1 suggested stream out of 21 gets almost no container-test coverage, while one that omits
  the key reads everything. Low count costs test coverage; omission costs the user a sane default.
- **Fix — how to build the list.** The list is usually absent or near-empty at certification time, so
  constructing it *is* the work. Three inputs, in order:
  1. **Method — real usage.** Query which streams existing connections actually enable, via
     `query_prod_connections_by_stream` (airbyte-ops-mcp). Prior certifications picked the top streams by
     real connection usage; this is the authoritative signal and the reason this criterion is
     `agent+external` rather than a repo read.
  2. **Intent.** `SuggestedStreams.yaml`: the streams "the average user will want."
  3. **Exclusions.** No highly sensitive or highly expensive streams (see the `new-source-connector`
     skill, §Suggested Streams). New high-volume streams default *out* —
     `docs/platform/connector-development/connector-breaking-changes.md:31-35` makes this a
     breaking-change-avoidance requirement, not a preference.

### M-5 · Icon
**Blocking** · Owner: `agent` · Group: `metadata`

- **Standard:** `docs/community/contributing-to-airbyte/resources/qa-checks.md:398` — "Each connector must
  have an icon available in at the root of the connector code directory. It must be an SVG file named
  `icon.svg` and must be a square." The check that enforced this no longer runs (see D-1); the standard
  still holds.
- **Check:** `icon.svg` exists at the connector root, and its root `<svg>` element declares
  `width == height` (tolerate a `px` suffix). **Do not test `viewBox`.** The house convention is explicit
  dimensions: of the 35 certified manifest-only sources, exactly one (`source-pinterest`) declares a
  `viewBox`. Fleet-wide, roughly half the icons have none. A `viewBox` check fails the connectors that
  follow the norm.
- **Pass when:** the file exists and is square. 250×250 is the dominant convention (≈394 of 679 icons,
  plus 45 at `250px`) and is what a new icon should use — but it is guidance, not a pass condition;
  `source-amazon-seller-partner` at 258×258 is fine.
- **Authoritative source:** the `icon.svg` **file**, not `metadata.yaml` → `data.icon`. That field is
  documented as being removed once the transition to in-folder icons completes
  (`connector-metadata-file.md:95-99`), but all 35 certified manifest-only sources still set it. Keep it
  in sync; do not treat its presence as satisfying this criterion.
- **Fix — icon is the wrong shape:** replace with a square SVG, preferring 250×250.
- **Fix — icon is missing** (the likelier case for a connector entering certification; e.g.
  `source-airtable` has no `icon.svg` today): source the vendor's official mark from their brand or press
  kit, convert to SVG, and set explicit `width="250" height="250"`. Nothing in the repo documents vendor
  logo sourcing — the `airbyte-brand-assets` skill covers Airbyte's own brand, not third-party marks — so
  record the source URL and any usage terms in the sub-issue for a human to confirm before merge.

### M-6 · Certified and enabled in Cloud
**Blocking** · Owner: `agent+external` · Group: `metadata`

- **Check:** `registryOverrides.cloud.enabled` and `.oss.enabled` in metadata; confirm the registry entry
  via `get_connector_registry_entry`.
- **Pass when:** enabled in both. Repo certification and Cloud certification are the same thing — the
  connector must be live for customers.
- **Fix:** enable in registry overrides.

### M-7 · On the current `source-declarative-manifest`
**Blocking** · Owner: `agent` · Group: `metadata`

- **Check:** `metadata.yaml` → `data.connectorBuildOptions.baseImage` against the latest published SDM tag.
- **Pass when:** on the latest stable tag. **No `.dev` or `.post` prerelease pins.**
- **Fix:** bump the base image. Certified connectors are auto-upgraded monthly afterward, so this only
  needs doing once.

### M-8 · Named owner
**Blocking** · Owner: `agent` · Group: `metadata`

- **Check:** the connector path appears in `CODEOWNERS`.
- **Pass when:** a team owns it. Certified means Airbyte maintains it; this is who gets paged.
- **Fix:** add the CODEOWNERS entry.

---

## 2 · Reliability evidence

The evidence hierarchy is strictly two-tier. **Production telemetry does not substitute for either path.**

1. **Standard tests** prove a stream by reading real records from the service.
2. **Mock-server tests** cover every stream the standard tests cannot prove.

### R-1 · Standard tests pass
**Blocking** · Owner: `agent+creds` · Group: `reliability`

- **Check:** `airbyte-ops secrets fetch <connector>` then `poe test-integration-tests`
  (→ `airbyte-cdk connector test`).
- **Pass when:** the suite passes. Already a hard CI gate for certified connectors — CI only tolerates
  failures when `supportLevel == community` **and** the connector has zero secrets.
- **Fix:** whatever the failure is. This blocks everything downstream in the group.

### R-2 · Every stream is accounted for by name
**Blocking** · Owner: `agent+creds` · Group: `reliability`

This is the criterion that catches what the others miss. **Do not derive coverage from `empty_streams`
alone** — neither standard test asserts per-stream record production:

- `airbyte-cdk connector test` asserts `not result.records` **in aggregate**. One stream returning data
  satisfies the assertion for every stream in the run.
- `airbyte-cdk image test` defaults `read_from_streams` to `"default"`, which intersects discovery with
  `suggestedStreams` — roughly a quarter of streams fleet-wide, and nothing at all when
  `suggestedStreams` is empty.

- **Check:** run the standard tests and parse **per-stream record counts** from the output. Classify every
  discovered stream:

  | Bucket | Meaning | Action |
  |---|---|---|
  | Records returned | Proven | none |
  | Zero records, in `empty_streams` | Known-unreadable | must have a mock (R-3) |
  | **Zero records, not in `empty_streams`** | **Undeclared gap** | investigate |

- **Pass when:** the third bucket is empty.
- **Fix:** for each undeclared empty stream, determine whether it is (a) genuinely unreadable in the test
  account → add to `empty_streams` with a `bypass_reason`, then write a mock test; or (b) a real defect —
  deprecated endpoint, missing permission, filter matching nothing → fix the connector.
- **File this as its own sub-issue.** It is the only criterion that routinely surfaces live bugs rather
  than missing tests.

### R-3 · Mock-server tests cover every bypassed stream
**Blocking** · Owner: `agent` · Group: `reliability`

- **Check:** every entry in `acceptance-test-config.yml` → `empty_streams` has a corresponding
  `HttpMocker`-based test in `unit_tests/`.
- **Pass when:** 1:1 coverage. Every bypass must also carry a non-empty `bypass_reason`.
- **Fix:** write the mock tests. Group by connector, one sub-issue listing every uncovered stream.

### R-4 · Custom component test coverage
**Blocking** · Owner: `agent+creds` · Group: `reliability`

- **Check:** `poe coverage` scoped to `components.py`.
- **Pass when:** ≥90% line coverage, **and** every public class and method has a direct test. The second
  condition is the meaningful one — line coverage on a 40-line component is noise.
- **Not applicable** when the connector has no `components.py`.
- **Prerequisite:** `poe-tasks/manifest-only-connector-tasks.toml` has no `coverage` task today. It must be
  added before this criterion is measurable.

---

## 3 · Incremental sync

### I-1 · Incremental implemented where the API supports it
**Blocking** · Owner: `agent+external` · Group: `incremental`

- **Check:** for each stream without `incremental_sync`, determine from API docs whether a usable cursor
  (updated-at, sequence, or event timestamp) exists.
- **Pass when:** every stream with a viable cursor is incremental, or `CONTRIBUTING.md` documents why not.
- **Fix:** add `incremental_sync` with the correct cursor field and datetime format.
- **⚠️ May be breaking:** introducing a cursor changes the connector's state format for that stream.
  Changing an existing cursor is explicitly breaking unless a state migration ships with it. Define the
  state migration in the same PR where possible. Run `breaking-change-evaluation`.

### I-2 · Incremental is correct, not merely present
**Blocking** · Owner: `agent+creds` · Group: `incremental`

- **Check:** sync, advance state, re-sync; assert no records are lost across the cursor boundary.
- **Pass when:** no gap. Cursor-boundary bugs that silently drop records are worse than no incremental at
  all, which is why presence alone is not sufficient.
- **Fix:** correct the cursor granularity, lookback window, or inclusivity.
- **⚠️ May be breaking:** correcting a cursor field, or a change that alters the *value* emitted for an
  existing cursor field, breaks incremental continuity unless a state migration ships with it. Granularity
  and lookback adjustments that preserve the field and its values generally are not. Run
  `breaking-change-evaluation`.

---

## 4 · Schema & data integrity

### S-1 · Every stream declares a primary key, and the key is actually a key
**Blocking** · Owner: `agent` · Group: `schema`

- **Check:** resolve `$ref` and `$parameters` in `manifest.yaml`; every `DeclarativeStream` has a non-empty
  `primary_key`. For dynamic-stream connectors, run `discover` and check the produced catalog. Then check
  that the declared key is *valid*:
  - **Non-deterministic values fail.** A PK field populated by an `AddFields` transformation whose value is
    time- or run-dependent (`{{ now_utc() }}`, `{{ today_utc() }}`, a UUID generator) re-keys every record
    on every sync and defeats dedup entirely. `source-100ms` declares `primary_key: [uuid]` on
    `active_room_peers`, `template_settings`, and `templates_destinations`, where `uuid` is
    `{{ now_utc() }}` — a non-empty `primary_key` that is not a key. Presence alone is not the test.
  - **Substream keys must be unique across parents.** Where a child stream is fetched under a parent path
    and its records are unique only *within* that parent, the key must be composite —
    `[parent_id, id]`, not `[id]`. **Substreams are the leading case for "composite where needed"; see
    S-3, which must pass jointly with this criterion.**
- **Pass when:** all streams have a PK, the PK is deterministic, and substream PKs include the parent
  identifier where the child is not independently unique — or `CONTRIBUTING.md` names each exception and
  why no suitable key exists (genuinely keyless report/aggregate streams are legitimate).
- **Fix:** add or correct `primary_key`, composite for substreams.
- **⚠️ May be breaking:** adding or changing a stream's primary key is on the breaking-change checklist
  ("*Schema change: The primary key (PK) for a stream is changed*"). Adding one where none existed changes
  dedup behaviour and the destination table key, and widening `[id]` to `[user_id, id]` is a PK change.
  Replacing a `now_utc()` PK also re-keys every existing destination row. Run
  `breaking-change-evaluation`.

### S-2 · Date and datetime fields are typed correctly
**Blocking** · Owner: `agent` · Group: `schema`

- **Check:** every date-like schema property declares the correct `format` and `airbyte_type`.
- **Fix:** correct the declarations.
- **⚠️ May be breaking:** adding, removing, or changing a `format` hint on an existing field is a breaking
  **type** change, not additive metadata. Typed destinations (S3 Data Lake & Iceberg, BigQuery, Snowflake,
  Redshift) map `format` to a concrete column type, so adding `format: date-time` flips a `string` column
  to `timestamp` and fails schema evolution on existing connections. Run `breaking-change-evaluation`.

### S-3 · Foreign keys are embedded in child records
**Blocking** · Owner: `agent` · Group: `schema`

- **Check:** streams fetched under a parent path (e.g. `/{employee_id}/employee_details`) include the
  parent identifier in their **emitted records**.
  - **Interpolating the parent ID into the request is the failing case, not the passing one.** A stream
    whose `path` contains `{{ stream_partition['...'] }}` sends the parent key to the API; it does not put
    it in the record. `source-aha` (`/products/{{ stream_partition.id }}/idea_categories`) and
    `source-100ms` (`/v2/active-rooms/{{ stream_partition['room_id'] }}/peers`) both fail on this.
  - Verify against actual output — read the stream and inspect a record — not against the manifest alone.
- **Pass when:** the join key is present in the record without requiring the user to reconstruct it,
  **and** the parent identifier is part of the child's `primary_key` where the child is not independently
  unique (see S-1). A stream can otherwise pass S-1 (a `primary_key` exists) and pass S-3 (the field is on
  the record) while the declared key is still not unique — `source-7shifts`' `wages` stream shows the
  shape: `partition_field: user_id`, an `AddFields` putting `user_id` on the record, and no `primary_key`
  declared at all.
- **Fix:** add the field with an `AddFields` transformation — "a transformation which adds field to an
  output record" — referencing the `partition_field` declared on the `ParentStreamConfig`:

  ```yaml
  transformations:
    - type: AddFields
      fields:
        - path: [user_id]
          value: "{{ stream_partition['user_id'] }}"
  ```

  For parent fields beyond the partition key, `ParentStreamConfig.extra_fields` pulls them into the slice
  as `stream_slice.extra_fields`; they still need an `AddFields` to land in the record. Then add the
  parent identifier to the child's `primary_key` per S-1.
- **Do not use `request_option`.** It exists on `ParentStreamConfig` and `ListPartitionRouter`, so it is
  valid YAML and passes schema validation — but `RequestOption` "specifies the key field or path and where
  in the **request** a component's value should be injected," with `inject_into` limited to
  `request_parameter` / `header` / `body_data` / `body_json`. It never reaches the emitted record. An agent
  that applies it will mark S-3 fixed and ship records that still lack the join key.
- **⚠️ May be breaking:** if the parent identifier is added to a `primary_key`, that is a PK change (see
  S-1). Separately, changing the *shape* of a substream partition key on an **incremental** stream —
  renaming `partition_field`, batching parent IDs, swapping the router class — breaks per-partition state
  unless a state migration ships with it. Full-refresh substreams are unaffected. Run
  `breaking-change-evaluation`.

### S-4 · Inline schemas are the default
**Recommended** · Owner: `agent` · Group: `schema`

- **Check:** streams use `InlineSchemaLoader`.
- **Pass when:** inline, or a documented reason. Inline schemas keep the manifest self-describing and
  auditable.

### S-5 · Deletions are replicated where the API exposes them
**Blocking** · Owner: `agent+external` · Group: `schema`

- **Check:** does the API expose deletions (an `include_deleted` parameter, a deleted-records endpoint, or
  a soft-delete flag)?
- **Pass when:** deletions are replicated, using one canonical pattern documented in `CONTRIBUTING.md` —
  either a dedicated `deleted_*` stream or a deletion flag field on the primary stream. Pick one per
  connector and state which. Webhook-based deletion is out of scope.
- **Fix:** implement the pattern.

### S-6 · No unexpected or invalid record fields
**Blocking** · Owner: `agent+external` · Group: `schema`

- **Check:** the field-validation dashboards.
- **Pass when:** no unexpected fields and no validation failures, or the schema is updated to declare them.
- **⚠️ Blocked:** the dashboards are not currently reachable. Until they are, this criterion **must be
  reported as unevaluated rather than passed** — a silent no-op here is worse than a failure.

---

## 5 · Error handling

### E-1 · Errors are classified per the Airbyte Protocol
**Blocking** · Owner: `agent` · Group: `errors`

- **Check:** `manifest.yaml` error handlers and response filters.
- **Pass when:** at minimum —
  - `401` / `403` → `config_error` with an actionable message
  - `429` → rate-limit backoff, never a hard failure
  - `5xx` → retry with exponential backoff, then `system_error`
  - a documented default action for unmatched responses

  Connector-specific mappings are documented in `CONTRIBUTING.md` / `AGENTS.md`.
- **Fix:** add `HttpResponseFilter` entries. See the `writing-good-error-messages` skill for message
  wording; do not restate its guidance here.

### E-2 · The check stream is reachable by every user
**Blocking** (automatable part) + **human sign-off** · Owner: `agent` then `human` · Group: `errors`

A bad check is the single largest source of "it says connected but every sync fails."

- **Check (agent):**
  1. The stream named in `check:` **must not appear in `empty_streams`.** If our own test account cannot
     read it, it is the wrong choice by definition.
  2. The stream must not sit behind a paid plan tier or an optional scope — infer from API docs and from
     the bypass reasons of neighbouring streams. Flag candidates.
- **Sign-off (human):** an engineer confirms the stream is representative of what a typical customer will
  actually have access to. This part is subjective and stays with a person — but the agent's analysis is
  attached so the review starts from evidence.
- **Fix:** change the check stream, or add a dedicated lightweight check.

### E-3 · Known configuration errors are surfaced proactively
**Blocking** · Owner: `agent+external` · Group: `errors`

- **Check:** the API's published error guide against the connector's response filters.
- **Pass when:** documented, user-correctable failure modes produce actionable messages rather than a raw
  HTTP error.
- **Fix:** add `HttpResponseFilter` entries with specific messages.

---

## 6 · Authentication & security

### A-1 · OAuth is implemented and is the default
**Blocking** · Owner: `agent` · Group: `auth`

- **Check:** `spec.advanced_auth`; ordering of the credentials `oneOf`.
- **Pass when:** OAuth is implemented and listed **first** in the UI — **where the API supports OAuth**.
  When it does not (API-key-only services), `CONTRIBUTING.md` must state that explicitly. The
  justification is the machine-checkable artifact; a silent pass is not acceptable.
- **Fix:** implement OAuth and reorder the spec.
- **⚠️ May be breaking:** *reordering* a discriminated `oneOf` is not breaking on its own — saved configs
  resolve by their `auth_type` const, and the order only drives the UI default. The breaking mechanisms
  here are **wrapping a previously flat spec into a `oneOf`** (a config shape change) and **adding a
  required field**. Both are avoidable with a config migration defined in the same PR; without one, they
  are breaking. Run `breaking-change-evaluation`.

### A-2 · Declarative OAuth over custom OAuth
**Blocking** · Owner: `agent` · Group: `auth`

- **Check:** `oauth_connector_input_specification` present; no custom OAuth component in `components.py`.
- **Pass when:** declarative, wherever the API supports a standard flow.
- **Fix:** migrate to the declarative flow.

### A-3 · Cloud OAuth is provisioned and prompts for nothing Airbyte supplies
**Blocking** · Owner: `human` · Group: `auth-cloud`

- **Check:** in Cloud, the OAuth app is registered and the consent flow completes without asking the user
  for `client_id`, `client_secret`, developer tokens, or anything else Airbyte should provide.
- **Why human:** this can fail independently of everything in the repo, and it is the failure customers
  actually hit. No repo-side check catches it.
- **Fix:** register/provision the Cloud OAuth application.

### A-4 · Secrets are marked
**Blocking** · Owner: `agent` · Group: `auth`

- **Check:** every credential-bearing spec property, including inside `oneOf` branches, has
  `airbyte_secret: true`.
- **Fix:** add the annotation.

### A-5 · HTTPS only
**Blocking** · Owner: `agent` · Group: `auth`

- **Check:** every `url_base` and auth endpoint uses `https://`.
- **Fix:** correct the scheme.

---

## 7 · Performance

### P-1 · Concurrency is configured
**Blocking** · Owner: `agent` · Group: `perf`

- **Check:** `concurrency_level` present in `manifest.yaml`.
- **Fix:** add it, tuned to the API's documented limits.

### P-2 · ApiBudget where the API publishes rate limits
**Blocking** · Owner: `agent+external` · Group: `perf`

- **Check:** `api_budget` present when the API documents rate limits.
- **Pass when:** configured to match the published limits, or `CONTRIBUTING.md` documents why the API
  needs none.
- **Fix:** add `api_budget` with the correct policies.

### P-3 · Backoff strategy
**Blocking** · Owner: `agent` · Group: `perf`

- **Check:** a backoff strategy is attached to the error handler for retryable responses.
- **Fix:** add exponential backoff, honouring `Retry-After` where the API sends it.

---

## 8 · Configuration UX

### X-1 · Spec fields are user-facing and self-explanatory
**Blocking** · Owner: `agent` · Group: `ux-spec`

- **Check:** every property in `spec.connection_specification`.
- **Pass when:** each field is user-relevant (no implementation detail leakage), required only when truly
  required, has a self-contained tooltip that does not depend on reading external docs, and has a sensible
  default where one exists. Field `order` is set.
- **Fix:** rewrite titles, descriptions, defaults, and ordering.
- **⚠️ May be breaking:** adding a new **required** spec field, or removing or renaming an existing one, is
  breaking unless a config migration applies — which is what X-2 exists to ensure. Retitling, rewording,
  reordering, and adding optional fields are not. Run `breaking-change-evaluation`.

### X-2 · Config migrations, validations, and transformations
**Blocking** · Owner: `agent` · Group: `ux-spec`

- **Check:** where the spec has changed shape historically, a config migration exists; input validation and
  normalization are implemented where appropriate.
- **Fix:** implement what is missing.

### X-3 · Engineer UX walkthrough
**Blocking** · Owner: `human` · Group: `ux-review`

- An engineer sets the connector up end to end and makes any needed improvements.

### X-4 · Non-engineer setup validation
**Blocking** · Owner: `human` · Group: `ux-review`

- A non-engineer sets up the connector using only the published docs and records a Loom for the connector
  engineer.
- **Sequencing:** batch this across several connectors per cycle and run it **in parallel** with the code
  work. It gates the final certification merge; it must not gate the sub-issues.

---

## 9 · Documentation

**Source of truth: `docs/community/contributing-to-airbyte/resources/qa-checks.md`.** D-1, D-2, and D-6
are checks that page already defines. Cite it rather than restating it — a restated spec drifts. The
criteria below carry only the manifest-only delta.

**These checks are not merely lapsed for manifest-only connectors; they never applied.** The QA checks
lived in `airbyte-ci/connectors/connectors_qa`, deleted in #71275 (*"chore(pipelines): delete legacy
connectors_qa module"*); no QA-check code remains in the repo and nothing in `.github/workflows` runs it.
`qa-checks.md` survives as orphaned documentation. And while the checks did run, they were scoped
`_Applies to the following connector languages: python, low-code_` — **not manifest-only**. For the
category this register governs, these are a first-time bar, not a restored one.

### D-1 · Standard structure
**Blocking** · Owner: `agent` · Group: `docs`

- **Check:** `docs/integrations/sources/<name>.md` follows the heading structure and order enumerated at
  `qa-checks.md:47-124`, which lists the expected headers in order plus the eight whose strict check is
  skipped (`Set up the CONNECTOR_NAME connector in Airbyte`, the two `For Airbyte Cloud:` /
  `For Airbyte Open Source:` subtitles, `CONNECTOR_SPECIFIC_FEATURES`, `Performance considerations`,
  `Data type map`, `Limitations & Troubleshooting`, `Tutorials`). Do not infer the structure — read it
  there.
- **Two structural rules `qa-checks.md` does not cover:**
  - `writing-connector-docs.md:9-19` requires an **exact-content** `## IP allow list` section before
    `## Changelog` on every source connector. Use the copy given there verbatim.
  - `writing-connector-docs.md:188-213`: `## Usage with PyAirbyte` is **auto-generated** above `Changelog`
    when the connector is PyAirbyte-enabled and the doc does *not* declare the heading. Declaring it
    disables generation. Do not add the heading unless you intend to own the section.
- **Fix:** restructure to the order at `qa-checks.md:47-124`; add the IP allow list section.

### D-2 · Prerequisites covers every required field
**Blocking** · Owner: `agent` · Group: `docs`

- **Check:** every property in the spec's `required` array appears in the Prerequisites section. This is
  `qa-checks.md:125` — *"Prerequisites section of the documentation describes all required fields from
  specification."*
- **Fix:** add the missing entries.

### D-3 · Setup guide fields link out or spell it out
**Blocking** · Owner: `agent` · Group: `docs`

- **Check:** each setup field links to vendor documentation explaining what it is and where to find it.
  Where no such documentation exists, the steps are written inline.
- **Fix:** add links or inline steps.

### D-4 · Non-obvious behaviour is documented, in the right place
**Blocking** · Owner: `agent` · Group: `docs`

- **Check:** user-relevant quirks and domain model in the user docs; developer-relevant behaviour in
  `CONTRIBUTING.md` and `AGENTS.md`.
- **Pass when:** both exist and are current. Keep them in sync — see the
  `connectors-update-unique-behavior` skill.
- **Fix:** write the missing sections.

### D-5 · User-relevant language
**Blocking** · Owner: `agent` · Group: `docs`

- **Check:** docs describe what the user does, not how the connector is built.
- **Fix:** rewrite.

### D-6 · Links resolve
**Blocking** · Owner: `agent` · Group: `docs`

- **Check:** every link in the docs page resolves. This is `qa-checks.md:37` — *"Links used in connector
  documentation are valid."*
- **Pass when:** all links resolve, **or** an intentional 404 is prefixed with `example: ` — the
  convention that page defines for links used as examples. Do not report a prefixed link as a failure, and
  do not remove a working example link that lacks the prefix; add it.
- **Fix:** repair, remove, or prefix with `example: `.

### D-7 · Links are anchor-precise
**Recommended** · Owner: `agent` · Group: `docs`

- Links point to the relevant page anchor rather than a top-level URL where applicable. Reported, not
  gating — third-party anchors change without notice and generate noise.

---

## 10 · Competitive parity

### V-1 · Stream coverage matches the market
**Blocking** · Owner: `agent+external` · Group: `parity`

Score in **streams**, not endpoints. Streams map to resources; competitor tables are frequently
denormalized or derived and do not correspond 1:1 to API endpoints.

- **Required source:** Fivetran.
  1. **First choice — machine-readable:** `github.com/fivetran/dbt_<name>_source` →
     `models/src_<name>.yml` lists exact table names, columns, and descriptions. ~49 packages exist.
  2. **Fallback:** `fivetran.com/docs/connectors/applications/<name>` for the feature matrix (capture
     deletes, history mode, priority-first sync). The full table list sits behind a JS ERD — prefer the
     dbt package.
- **Recommended sources:** Stitch (`stitchdata.com/docs/integrations/saas/<name>` — tables, replication
  keys, PKs; closest 1:1 to our stream model, but in maintenance under Qlik, so treat as a floor);
  Estuary Flow; Hevo Data.
- **Vertical sources**, only where relevant: Supermetrics / Funnel.io / Adverity for ads connectors;
  Merge.dev for HRIS / ATS / CRM / ticketing.

- **Output:** a parity table with one row per competitor table and one of four verdicts:

  | Verdict | Meaning |
  |---|---|
  | `covered` | name our stream |
  | `covered-as-field` | name our stream and the field |
  | `missing` | we don't have it |
  | `out-of-scope` | with a reason |

- **Pass when:** no `missing` rows, or each is justified.
- **Fix:** implement the missing streams. **One sub-issue listing all of them**, not one per stream.

---

## 11 · Operational readiness

### O-1 · Bug backlog is resolved or triaged
**Blocking (subset)** · Owner: `agent+external` · Group: `bugs`

Search `airbytehq/airbyte`, `airbytehq/alpha-beta-issues`, and `airbytehq/oncall`.

- **Blocking:** every open issue that is **reproducible and confirmed a connector defect** is fixed, or
  explicitly waived with a written reason.
- **Required but not blocking:** every other open issue is triaged and labelled.
- **Why split:** the three repos hold ~8,600 open issues; a typical connector draws 5–25, most of which
  are user configuration problems. Requiring a fix-or-justification for all of them would consume more
  engineering time than every other criterion combined.
- **Fix:** the agent produces the first-pass triage; a human confirms the blocking subset.

### O-2 · Datadog monitors
**Blocking** · Owner: `human` · Group: `monitoring`

- Add the connector to the certified-connector monitor list and update the dashboard.
- **⚠️ Blocked:** the runbook location is not yet published. Report as unevaluated until it is.

### O-3 · Production health
**Blocking at entry** · Owner: `agent+external` · Group: `telemetry`

- **Check:** `query_prod_connector_connection_stats` and `query_prod_recent_syncs_for_connector`.
- **Pass when:** sync success rate clears the entry threshold, **scored only where there is enough traffic
  for the number to mean anything.** Success rate is a lagging indicator and does not exist at all for a
  connector with no users — it cannot be the primary reliability gate, which is why R-1 through R-3 carry
  that weight instead.
- **Standing obligation:** after certification, production failures are ours to fix. This is not
  re-litigated at each evaluation; it is the ongoing maintenance commitment certification creates.

### O-4 · Versioning and changelog hygiene
**Blocking** · Owner: `agent` · Group: `metadata`

- **Check:** no unresolved breaking-change entries; changelog has an entry per version; version matches
  across `metadata.yaml` and the docs changelog.
- **Pass when:** every changelog Subject is a **simple one-liner** — one concise sentence naming the
  user-visible change. No multi-sentence subjects, no migration instructions crammed into the cell. Where a
  change needs more explanation, it belongs in the docs page or a migration guide that the entry links to.
- **Fix:** reconcile. See the `breaking-change-evaluation` skill rather than re-deriving the policy.

---

## Evaluation order

Some work must land before other work. The evaluator emits sub-issues in this dependency order:

1. **`gate`** — if this fails, stop.
2. **`metadata`**, **`auth`**, **`perf`** — independent, parallelizable.
3. **`errors`**, **`schema`** — schema and error handling before reliability, since both change what the
   standard tests observe.
4. **`reliability`** — R-1 must pass before R-2 and R-3 are meaningful.
5. **`incremental`** — needs correct schemas and cursors already in place.
6. **`parity`** — new streams land last, so they inherit the corrected patterns rather than replicating
   old ones.
7. **`docs`** — documents the final state.
8. **`ux-review`**, **`auth-cloud`**, **`monitoring`** — human work; start in parallel, gate the final merge.
9. **M-1** — flip `supportLevel` to certified. Always the last PR.

## Reporting rules

- A criterion that cannot be evaluated is reported **unevaluated**, never **passed**. This applies to S-6
  and O-2 until their dependencies are unblocked.
- Every verdict cites evidence: a file and line, a command and its output, or a query result.
- The report records the evidence path taken per stream for R-2 and R-3.
