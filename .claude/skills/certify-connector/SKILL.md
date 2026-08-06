---
name: certify-connector
description: Evaluate a manifest-only API source connector against the certification criteria and file a certification epic. Reports pass/fail/unevaluated per criterion with evidence, then optionally creates a GitHub epic with sub-issues sized for Devin sessions. Use when assessing whether a connector can be certified, or when starting a certification effort.
devin-enabled: true
icon: shield-check
---

# Certify Connector

Evaluates a manifest-only API source connector against [connector-certification-criteria](../connector-certification-criteria/SKILL.md)
and turns the gaps into a trackable certification epic.

**Certification transfers ownership.** A certified connector is enrolled in monthly automated CDK upgrades,
blocks CI on standard-test failures, and its production failures become ours to fix. Treat this as a
commitment, not a badge.

## Usage

```
/certify-connector source-<name>              # evaluate, report, stop
/certify-connector source-<name> --file-epic  # evaluate, then file the epic
```

Evaluation is read-only and re-runnable. **Never file issues without `--file-epic`** — the evaluation will
be run many times during remediation and must not create duplicates.

---

## Phase 0 · Gate

Read `airbyte-integrations/connectors/<name>/metadata.yaml`:

```bash
yq -r '.data.tags[] | select(test("^language:"))' metadata.yaml
```

**If the tag is not `language:manifest-only`, stop.** Report the connector ineligible and say that migration
to manifest-only is prerequisite work tracked separately.

Do not file a migration issue. Do not file an epic. Do not evaluate the remaining criteria — a partial
report against a connector that can't be certified invites someone to act on it.

A `components.py` file is fine. Custom Python components are still manifest-only.

---

## Phase 1 · Evaluate

Work through every criterion in the register. Three verdicts:

| Verdict | When |
|---|---|
| **pass** | The criterion is met, with evidence |
| **fail** | The criterion is not met, with evidence |
| **unevaluated** | The criterion could not be checked |

**Never report `pass` for something you could not check.** Criteria S-6 (field validation dashboards) and
O-2 (Datadog runbook) currently have unresolved dependencies and will normally come back `unevaluated`.
A silent no-op that reads as a pass is the worst possible outcome here.

Every verdict cites evidence: a file and line, a command and its output, or a query result.

### Order of work

Cheap static checks first, then external lookups, then the expensive credentialed test run. That way an
obviously-ineligible connector fails fast without burning a test cycle.

1. **Static, in-repo** — metadata, manifest, schemas, spec, docs, CODEOWNERS
2. **External** — competitor parity, bug backlog, production telemetry, registry state
3. **Credentialed** — standard tests, per-stream record counts, coverage

### Running the credentialed checks (R-1, R-2, R-4, I-2)

```bash
cd airbyte-integrations/connectors/<name>
airbyte-ops secrets fetch <name>
poe test-integration-tests    # → airbyte-cdk connector test
```

**R-2 is the criterion that matters most and is easiest to get wrong.**

Do not derive stream coverage from `empty_streams`. Neither standard test asserts per-stream record
production:

- `airbyte-cdk connector test` asserts records were returned **in aggregate** — one stream returning data
  satisfies the assertion for every stream in the run.
- `airbyte-cdk image test` defaults `read_from_streams` to `"default"`, which intersects discovery with
  `suggestedStreams` — a fraction of streams, and nothing at all when `suggestedStreams` is empty.

So "not in `empty_streams`" means nobody declared the stream broken, not that it works.

Parse **per-stream record counts** from the read output and classify every discovered stream:

| Bucket | Meaning | Action |
|---|---|---|
| Records returned | Proven | none |
| Zero records, in `empty_streams` | Known-unreadable | needs a mock test (R-3) |
| **Zero records, not in `empty_streams`** | **Undeclared gap** | investigate — see below |

For each undeclared empty stream, determine whether it is:

- **genuinely unreadable in the test account** (premium tier, no data, permission we lack) → add to
  `empty_streams` with a `bypass_reason`, then write a mock test; or
- **a real defect** — deprecated endpoint, broken pagination, a filter matching nothing → fix the connector.

This bucket is unmeasured across the fleet today. It is the only criterion that routinely surfaces live
bugs rather than missing tests, so give it its own sub-issue.

If secrets are unavailable, report R-1, R-2, R-4, and I-2 as `unevaluated` and say so prominently. Do not
substitute production telemetry — it is explicitly not an evidence path.

### Competitive parity (V-1)

Score in **streams**, not endpoints. Streams map to resources; competitor tables are often denormalized or
derived and don't correspond 1:1 to API endpoints.

Fivetran is required. Try the machine-readable source first:

```bash
gh api repos/fivetran/dbt_<name>_source/contents/models/src_<name>.yml --jq '.content' | base64 -d
```

That yields exact table names, columns, and descriptions. Roughly 49 such packages exist. If there's no
package, fall back to scraping `fivetran.com/docs/connectors/applications/<name>`.

Then Stitch, Estuary, or Hevo as recommended sources, plus a vertical competitor where relevant
(Supermetrics / Funnel.io / Adverity for ads; Merge.dev for HRIS, ATS, CRM, ticketing).

Emit one row per competitor table with a verdict of `covered` (naming our stream), `covered-as-field`
(naming stream and field), `missing`, or `out-of-scope` with a reason.

### Report format

```markdown
# Certification Evaluation — source-<name>

**Eligible:** yes (manifest-only)
**Blocking criteria:** N passed · M failed · K unevaluated
**Recommended criteria:** N passed · M failed

## Blocking failures
| ID | Criterion | Evidence | Group |
|----|-----------|----------|-------|

## Unevaluated
| ID | Criterion | Why it could not be checked |
|----|-----------|------------------------------|

## Per-stream evidence (R-2 / R-3)
| Stream | Evidence path | Status |
|--------|---------------|--------|

## Competitive parity (V-1)
| Competitor table | Verdict | Our stream |
|------------------|---------|------------|

## Proposed remediation plan
Ordered work units with dependencies.
```

---

## Phase 2 · File the epic

Only with `--file-epic`, and only after showing the user the proposed issue set and getting confirmation.

**Repo:** `airbytehq/airbyte-internal-issues`
**Labels:** `team/apis` and `connectors/source/<name>` on the epic and every sub-issue.
Create any missing label rather than substituting a near match:

```bash
gh label create "<name>" --repo airbytehq/airbyte-internal-issues --description "<description>"
```

**Project board:** add the epic to the APIs Team board:

```bash
gh project item-add 137 --owner airbytehq --url <issue-url>
```

### Grouping

One sub-issue per criteria group. Criteria in the same group touch the same surface, so a single Devin
session can do them together — "add the 5 missing streams" is one issue listing all five, not five issues.

Split out of the group when:

- The owner class is `human` — it needs a different actor entirely
- The work is R-2's undeclared-empty-streams bucket — it's investigation, not implementation

### Order

Sub-issues carry an explicit dependency order. Later work assumes earlier work has landed:

1. `metadata`, `auth`, `perf` — independent, parallelizable
2. `errors`, `schema` — before reliability, since both change what the standard tests observe
3. `reliability` — R-1 must pass before R-2 and R-3 mean anything
4. `incremental` — needs correct schemas and cursors in place
5. `parity` — new streams land last so they inherit the corrected patterns
6. `docs` — documents the final state
7. `ux-review`, `auth-cloud`, `monitoring` — human work; **start in parallel, gate the final merge**
8. **M-1** — flip `supportLevel` to certified. Always the last PR.

### Sub-issue body

Each one must be actionable by a Devin session with no additional context:

- The criterion ID and its statement from the register
- What the evaluator found, with evidence
- The specific fix, naming files and streams
- How to verify — the command that turns the verdict green
- A note that the certification epic tracks it, with a link

### Human-gated sub-issues

Where the owner is `human` (X-3 engineer walkthrough, X-4 non-engineer Loom, A-3 Cloud OAuth
provisioning, O-2 Datadog monitors, the E-2 check-stream sign-off), the issue instructs the engineer what
to verify rather than describing a code change. Attach the agent's analysis so the review starts from
evidence rather than cold.

**X-4 sequencing:** batch the non-engineer walkthrough across several connectors per cycle and run it in
parallel with the code work. It gates the final certification merge; it must not gate the sub-issues, or
it becomes the bottleneck on every epic.

---

## Notes

- Re-run evaluation freely during remediation. It's read-only and idempotent.
- The final PR flips `supportLevel`, `releaseStage`, and `ab_internal`. It must not merge until every
  blocking criterion passes and no criterion is left `unevaluated`.
- Follow the repo's PR conventions: open as draft, semantic title, and the AI attribution line.
