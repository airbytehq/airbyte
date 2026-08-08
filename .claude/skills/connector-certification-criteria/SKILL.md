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
**Blocking** · Owner: `agent` · Group: `metadata`

- **Check:** `metadata.yaml` → `data.suggestedStreams.streams`
- **Pass when:** 3–10 streams, including the connector's headline entities, **or** a documented reason in
  `CONTRIBUTING.md` for omitting them (dynamic-stream connectors legitimately omit).
- **Why the bound:** suggested streams also determine what `airbyte-cdk image test` reads by default. A
  connector with 1 suggested stream out of 21 gets almost no container-test coverage.
- **Fix:** pick the entities a new user would sync first.

### M-5 · Icon
**Blocking** · Owner: `agent` · Group: `metadata`

- **Check:** `icon.svg` exists; viewBox is square.
- **Fix:** replace with a square SVG.

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

### I-2 · Incremental is correct, not merely present
**Blocking** · Owner: `agent+creds` · Group: `incremental`

- **Check:** sync, advance state, re-sync; assert no records are lost across the cursor boundary.
- **Pass when:** no gap. Cursor-boundary bugs that silently drop records are worse than no incremental at
  all, which is why presence alone is not sufficient.
- **Fix:** correct the cursor granularity, lookback window, or inclusivity.

---

## 4 · Schema & data integrity

### S-1 · Every stream declares a primary key
**Blocking** · Owner: `agent` · Group: `schema`

- **Check:** resolve `$ref` and `$parameters` in `manifest.yaml`; every `DeclarativeStream` has a non-empty
  `primary_key`. For dynamic-stream connectors, run `discover` and check the produced catalog.
- **Pass when:** all streams have a PK, or `CONTRIBUTING.md` names each exception and why no suitable key
  exists (genuinely keyless report/aggregate streams are legitimate).
- **Fix:** add `primary_key`, composite where needed.

### S-2 · Date and datetime fields are typed correctly
**Blocking** · Owner: `agent` · Group: `schema`

- **Check:** every date-like schema property declares the correct `format` and `airbyte_type`.
- **Fix:** correct the declarations.

### S-3 · Foreign keys are embedded in child records
**Blocking** · Owner: `agent` · Group: `schema`

- **Check:** streams fetched under a parent path (e.g. `/{employee_id}/employee_details`) include the
  parent identifier in their records.
- **Pass when:** the join key is present without requiring the user to reconstruct it.
- **Fix:** add the field via the partition router's `request_option` or a transformation.

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

### D-1 · Standard structure
**Blocking** · Owner: `agent` · Group: `docs`

- **Check:** `docs/integrations/sources/<name>.md` follows the standard heading structure and order.
- **Fix:** restructure.

### D-2 · Prerequisites covers every required field
**Blocking** · Owner: `agent` · Group: `docs`

- **Check:** every property in the spec's `required` array appears in the Prerequisites section.
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

- **Check:** every link in the docs page resolves.
- **Fix:** repair or remove.

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
