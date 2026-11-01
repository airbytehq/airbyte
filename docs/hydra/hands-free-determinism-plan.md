# Hands-Free Pipeline: Determinism Plan

Plan for pivoting the hands-free pipeline's per-event stage handoff from an
LLM-driven decision loop onto a code-driven decision engine, while keeping an
LLM in the loop only where it earns its place.

The two reference artifacts this plan builds on:

- `.github/workflows/hydra-stage-handoff.yml` — the current per-event handoff.
- [`airbytehq/hydrakit`](https://github.com/airbytehq/hydrakit) — the shared
  `hydra state`/`assess` CLI and library, already shipped and preinstalled in
  Devin sessions. This plan treats hydrakit's state schema (`hydra.state/v0`)
  and `assess` function as the deterministic engine.

The per-item playbook
(`airbytehq/ai-skills:plugins/devin-playbooks/playbooks/hands_free_item.md`)
and its sweep-side counterpart (`hands_free_sweep`) are the behavioral spec
hydrakit's `assess` is a condensed reading of. The handoff workflow launches
`!hands_free_item` scoped to a single PR; the daily sweep runs
`!hands_free_sweep` and starts a `!hands_free_item` per candidate item.

## Sequencing

| Phase | Status | Depends on | Blocks |
|---|---|---|---|
| 0 — Ship router/split playbook | **Done** (2026-10-28) | — | all downstream quality work |
| 1 — Core determinism: hydra-driven handoff | Not started | 0; hydrakit stable | 2, 3 |
| 2 — Expand trigger set | Not started | 1 | — |
| 3 — Hybrid LLM for substantive + escalation body | Not started | 1 | — |
| 4 — Close upstream gaps (dispatch-time head SHA, structured escalation markers) | Not started | parallel with 1-3 | full determinism of some branches |

Do 1 before 2 and 3 because they both wire into the hydra-driven dispatcher.
4 is parallel code in other repos (airbyte workflows, resolver) and should
start now.

---

## Phase 0 — Ship router/split playbook (DONE)

Shipped 2026-10-28 via airbyte#89775 (handoff workflow now launches
`!hands_free_item`) and the matching split in ai-skills
(`plugins/devin-playbooks/playbooks/hands_free_item.md` plus the sweep-side
`hands_free_sweep`). Decoupled from hydrakit, as expected (hydra reads PR
state, not playbook internals). Expected wins: scoped per-item prompts fix the
"laziness" and poor-escalation symptoms; eliminates the dead "Single-Item
Handoff Mode" cross-reference the old handoff prompt-text had into
`daily_hands_free_triage.md`.

---

## Phase 1 — Rebuild handoff on hydra + assess

Build the dispatcher-based handoff as a **new workflow file alongside** the
existing `hydra-stage-handoff.yml`, rather than refactoring in place. The
existing workflow stays unchanged throughout and continues launching
`!hands_free_item` as it does today. The new workflow runs in parallel.

**Separate opt-in label.** The new workflow gates on `hyd-chain-v2` instead of
`hyd-chain`. The two labels are intentionally disjoint during the soak so no
PR is driven by both workflows at the same time:

- PR labeled `hyd-chain` only → old workflow drives it (current behavior).
- PR labeled `hyd-chain-v2` only → new workflow drives it (volunteer PRs).
- Both labels on one PR → both drive it; avoid in practice. The idempotency
  key `(pr, head_sha, next_action)` catches that case.

After cutover: rename `hyd-chain-v2` → `hyd-chain` across labeled PRs (or
teach the new workflow to also accept `hyd-chain`), then retire the old
workflow.

**Why parallel instead of in-place:**

- Clean rollback: if the new workflow misbehaves, disable its triggers; the
  old one is still running untouched.
- Clean diff: a new file instead of a major refactor to a heavily-reviewed one.
- Both workflows can run simultaneously during dry-run → direct side-by-side
  comparison of decisions.
- No git-blame churn on `hydra-stage-handoff.yml` while the work is in flight.

New file name TBD (e.g. `.github/workflows/hydra-stage-handoff-v2.yml` or
`hydra-dispatch.yml`).

**New handoff shape:**

1. Trigger fires (details in Phase 2).
2. Workflow calls `hydra state <pr> --assess --json` (CLI preinstalled;
   version-pinned via `hydra.mjs` download in CI).
3. Switch on `assessment.next_action`:

   | `next_action` | Dispatcher does |
   |---|---|
   | `prove` | dispatch `ai-prove-fix-command.yml` |
   | `review` | dispatch `ai-review-command.yml`; mark ready-for-review if `mark_ready_for_review` |
   | `ready` | dispatch `ai-ready-command.yml` |
   | `resolve_conflicts` | dispatch `ai-resolve-conflicts-command.yml` |
   | `fix` | dispatch `ai-fix-command.yml` on `assessment.target` (issue). Rework loop; hydra enforces `rework_cap` |
   | `triage` | dispatch `ai-triage-command.yml` |
   | `fix_ci` | thin-LLM call for CI relatedness; dispatch or exit per result |
   | `escalate` | template-fire escalation (see Phase 3) |
   | `wait` / `none` / `skip` | exit |

4. Dispatcher stages pivot to `wait-for-stopped-status: true` so completion =
   session completion. Each dispatcher ends by calling the handoff workflow
   (effectively `repository_dispatch`) with the PR number; handoff re-reads
   state and loops. This is the "single chain" idea folded in.

5. Idempotency key becomes `(pr_number, head_sha, next_action)` — hydra returns
   the same assessment for the same state, so retries natively collapse.

**Non-happy branches are handled by hydra's blockers:**

- `blockers: ["can't tell whether commits are substantive"]` → go to Phase 3 LLM.
- `blockers: ["comment-only escalation isn't visible here"]` → exit with
  warning; Phase 4 closes this.
- `blockers: ["GitHub hadn't computed merge state"]` → exit; next event re-fires.

**Dry-run rollout:** ship the new workflow with `DRY_RUN=true` (env var or
repo variable) that logs the decision + the dispatch it *would* have fired,
but doesn't actually fire the `curl`. The old workflow keeps dispatching for
real during this period, so no PR actually stalls. Flip to `DRY_RUN=false`
after ~48h of clean logs with representative event volume.

**Cutover:**

1. New workflow in DRY_RUN=true, parallel to old (which keeps real-dispatching).
2. Flip new to DRY_RUN=false → both workflows now dispatching for real. The
   `(pr, head_sha, next_action)` idempotency key prevents double-dispatch.
3. Soak for a week with both live.
4. Empty the old workflow's `on:` block (or restrict to `workflow_dispatch`)
   — becomes inert.
5. After another soak with the new as sole dispatcher, delete the old file.

**Acceptance:** handoff workflow no longer launches a Devin session for the
decision itself. Decision latency drops from minutes to seconds. Per-handoff
ACU → 0 for the common case. Old `hydra-stage-handoff.yml` deleted at end of
cutover.

---

## Phase 2 — Trigger set

Triggers go on the **new** workflow (per Phase 1's parallel-workflow approach).
The old `hydra-stage-handoff.yml` keeps its original trigger set unchanged
until it's retired at the end of Phase 1's cutover.

Keep what works, add what's missing, and trust the engine to debounce.

**Keep:**

- `issue_comment: [created, edited]` — only until Phase 1 lands; replace with
  the completion-driven path below.
- `workflow_dispatch` — manual.

**Add:**

- `wait-for-stopped-status: true` on prove-fix / review / resolve-conflicts
  dispatchers; each dispatcher calls the handoff via `repository_dispatch` on
  completion. Removes comment-marker regex entirely.
- `check_run: [completed]` filtered to the 7 required status checks on
  `master`. Verified from the repo ruleset: all 7 required checks arrive as
  `CheckRun` entries (6 from GH Actions, 1 — "Connector CI Checks Summary" —
  from a GitHub App via the Checks API). `check_run` is the only trigger that
  covers all of them uniformly, and `status` events buy nothing here (no
  required check uses legacy commit statuses). Filter inside the job to the
  required-check names before calling hydra so unrelated check completions
  don't wake a runner needlessly.
- `pull_request: [synchronize]` — push-driven re-eval. Fires immediately on
  push (before CI starts), so hydra sees the new HEAD and can invalidate stale
  markers right away. Complementary to `check_run: completed`, which fires
  when CI finishes.
- `pull_request: [labeled]` filtered to `hyd-chain-v2` — opt-in moment,
  one-pass kickstart. Label migrates back to `hyd-chain` after cutover.
- `schedule` — Monday 08:00 UTC (midnight PT), scoped to `label:hyd-chain-v2`
  PRs
  whose `state.runs[ready].outcome === "FROZEN"`. One hydra pass per matching
  PR; re-dispatches `/ai-ready` as the engine decides. Only mechanism to
  recover from weekend-frozen `/ai-ready`.
- `repository_dispatch` from the oncall triage/fix workflows if cross-repo
  `/ai-triage → /ai-fix` ever moves into this chain. Not required for v1 — the
  sweep still catches that transition.

**Do not carry over to the new workflow:**

- `workflow_run` on `Connector CI` success — superseded by `check_run:
  completed`. The old `workflow_run` trigger only covered the subset of
  required checks produced by that specific workflow and missed the
  App-produced "Connector CI Checks Summary" rollup entirely. `check_run`
  covers all 7 required checks uniformly. (Under the parallel-workflow
  approach, "drop" means "do not include in the new workflow's `on:` block" —
  the old workflow keeps the trigger until retirement.)
- Comment-marker trigger stays dormant as a fallback until the completion-
  driven path (`wait-for-stopped-status` + `repository_dispatch`) is proven
  for a week in prod, then retire.

**"Settle" is not a trigger problem.** Trigger broadly, let `assess` return
`wait` when CI is pending or sessions are in flight, trust the next event.
Natural debouncing.

### Keeping the required-check filter list in sync

The `check_run: completed` trigger needs a filter list of required-check names
so the handoff doesn't wake on every unrelated CheckRun. Hydrakit itself reads
the required-check list live from the branch-protection ruleset
(`collect/github.ts:requiredChecks`), but the workflow filter is a separate
copy. Two options for keeping them in sync:

**Option A — Hardcoded list in the workflow, with drift detection.**

```yaml
jobs:
  handoff:
    if: >
      contains(fromJson(vars.REQUIRED_CHECK_NAMES), github.event.check_run.name)
```

Store the list as a repo variable (`vars.REQUIRED_CHECK_NAMES`, JSON array) so
updating it doesn't require editing the workflow file. Add a small periodic CI
check that reads the ruleset via `gh api repos/{owner}/{repo}/rules/branches/master`,
extracts `required_status_checks[].context`, and asserts the result matches
`vars.REQUIRED_CHECK_NAMES`. On mismatch, the check fails and someone updates
the variable. Required-check sets change rarely, so this check can run daily or
weekly rather than per-handoff.

- Cost per handoff: zero extra API calls.
- Cost of drift: a failed daily/weekly CI check; manual update of the repo var.
- Risk: between the ruleset change and the drift-check firing, the handoff may
  wake on an outdated filter (missing a newly-required check, or waking
  needlessly on a de-required one).

**Option B — Query the ruleset at trigger time.**

```yaml
jobs:
  handoff:
    runs-on: ubuntu-latest
    steps:
      - name: Load required check names
        id: required
        env:
          GH_TOKEN: ${{ steps.get-app-token.outputs.token }}
        run: |
          REQUIRED=$(gh api repos/${{ github.repository }}/rules/branches/master \
            --jq '[.[] | select(.type=="required_status_checks") | .parameters.required_status_checks[].context] | tostring')
          echo "names=$REQUIRED" >> "$GITHUB_OUTPUT"
      - name: Early exit if check is not required
        if: >
          !contains(fromJson(steps.required.outputs.names), github.event.check_run.name)
        run: exit 0
      # ...then call hydra as usual
```

- Cost per handoff: one extra GitHub REST call. Fast (<300ms, cached by GitHub
  edge).
- Cost of drift: none — the filter is live.
- Risk: a transient 5xx from the rulesets API drops the handoff for that
  event (idempotent retry on the next event covers it).

**Recommendation: Option A for v1.** Required-check sets change on the order
of once a quarter; the per-handoff savings dominate the one-off cost of
updating a repo variable. Add Option B as a fallback if drift events start
being frequent or disruptive.

**Acceptance:** every stage transition has at least one trigger.
Weekend-frozen `/ai-ready` recovers within 24h without the daily sweep. The
required-check filter list is either kept in a repo variable with drift
detection (Option A) or sourced live from the ruleset per handoff (Option B).

---

## Phase 3 — Scoped LLM for the two agentic branches

Two surgical uses of a thin LLM call (not a Devin session) from the handoff
workflow:

### Substantive-commit classification

Invoked only when hydra returns `prove` with the blocker `"can't tell whether
the commits since the verdict are substantive"`.

- Input: diff file list + per-file patch summary from
  `compare/{old_head}...{new_head}`.
- Output schema: `{is_substantive: boolean, reason: string, files_driving_decision: string[]}`.
- Model: Haiku-tier. Sub-second, fractional ACU.
- Fallback on LLM failure: assume substantive (hydra's current conservative
  default). No regression vs today.

**Also widen hydra's deterministic exemption** at the same time to reduce how
often the LLM is called:

- `.github/workflows/*.yml`, `.github/*.md`
- Octavia-authored version-bump commits (check `commit.author` + title pattern)
- Patches that are 100% whitespace or comment lines (detectable via
  `git diff --word-diff=porcelain` for a single-file diff)

This should drop re-prove rate meaningfully without needing the LLM for the
clearly-benign cases.

### Escalation message body

Invoked only when hydra returns `escalate`. Deterministic target (lookup chain
from §2.5 Escalation Targeting; connector→team table + `@oc-hydra` default).
Thin LLM call for the message body only, with the escalation reason + PR
context as input. Approve/reject buttons set deterministically per reason type.

**Acceptance:** no full Devin session on the handoff decision path except via
`fix_ci`. Re-prove rate drops ≥50% vs today.

---

## Phase 4 — Close upstream gaps (parallel work in other repos)

Hydra's known gaps that bound determinism. Each needs a small change in a
non-hydrakit repo. Start now; land independently.

1. **Dispatch-time head SHA tag.** `/ai-ready` and `/ai-resolve-conflicts` runs
   don't record which HEAD they covered — `assess` falls back to commit-dates
   estimation (`freshness_basis: time`). Fix: each dispatcher adds a
   `hydra-sha-<12>` tag at session start. Hydrakit reads it, upgrades
   `head_match` from estimated to exact.
2. **`/ai-ready` commit status.** Have `/ai-ready` post a `Hydra / ai-ready`
   commit status on the evaluated head. Gives hydra an exact-match signal
   without parsing comments.
3. **Structured conflict-resolver escalation marker.**
   `ai_resolve_conflicts_escalated` is comment-only today, which forces hydra's
   "can't see this escalation" blocker. Fix: emit a dispatch tag
   `hydra-escalated-<sha>` or a commit status; hydrakit then dedupes repeat
   attempts without the handoff needing a side channel.
4. **`/ai-ready` eligibility detail.** NOT_ELIGIBLE records the step name but
   not which specific gate failed. Have the workflow write the failing gate
   name as a job output or commit-status description. Lets hydra say "parked
   for human: Support Bot not assigned" vs just "parked for human."

**Acceptance:** `freshness_basis: time` disappears from hydra's state for ready
and resolve_conflicts. Repeat conflict-resolver escalations stop. `/ai-ready`
outcomes carry the specific blocking gate.

---

## Operate

- **Daily sweep stays.** Reduced role but not retired. Catches: untagged runs
  (older sessions, Slack-initiated), `/ai-triage → /ai-fix` cross-repo
  transitions, duplicate PR detection, post-merge health, and anything the
  event-driven path misses. Should get noticeably quieter as Phases 1–4 land.
- **Dynamic Workflows** not for the main orchestrator (wrong primitive for an
  event-driven, weeks-long, many-items-in-flight pipeline). Hold in reserve
  for bulk sweep tasks: backfills, migrations, one-shot audits.
- **Shadow mode first.** Before any dispatch, run Phase 1's handoff in a
  logging-only mode for a week. For every event, record the engine's
  `next_action` and compare to the daily sweep's actual action on the same PR.
  Divergences → either hydra bug (fix in hydrakit) or sweep inconsistency (fix
  in playbook). Only after a clean week does the handoff start dispatching.

---

## Non-goals (explicit)

- Making escalation message bodies deterministic. Templates for 8 reasons is a
  lot of taste work for a modest win; the thin LLM call wins.
- Making CI-failure relatedness deterministic. The LLM is doing real work there
  (reading error logs), and the branch fires infrequently.
- Retiring the daily sweep. Keep it as the catch-all; the event-driven path is
  a latency improvement, not a replacement.
- Replacing the orchestrator with Dynamic Workflows. Different problem shape.

---

## Risks

1. **Hydra schema churn.** `hydra.state/v0` is explicitly marked "still changes
   freely." Pin the version in the handoff workflow (`hydra.mjs` sha-pinned per
   release) and version-gate the switch statement so a schema bump doesn't
   silently break dispatch.
2. **Rework loop runaway.** `/ai-fix` dispatched for rework may not know it's a
   rework if the fix session doesn't read prior `failing_verdicts`. Confirm the
   fix playbook reads session history before leaning on rework. If not,
   dispatcher should pass rework context in the prompt.
3. **Thin-LLM latency on substantive calls.** Haiku is fast but adds a hop. If
   the deterministic widening (Phase 3) brings the "ambiguous" rate low enough,
   this is a non-issue. Monitor.
4. **Pending third-party checks.** Hydra handles via `wait`, but if a check
   never completes, the PR sits. Add an alert if a hydra `wait` persists >24h
   on a `hyd-chain-v2` or `hyd-chain` PR.
5. **Double-dispatch during the parallel soak.** New workflow gates on
   `hyd-chain-v2`, old on `hyd-chain` — disjoint label sets mean no PR is
   driven by both at the same time. Risk reduces to "someone accidentally
   applies both labels"; the `(pr, head_sha, next_action)` idempotency key
   catches that case.
