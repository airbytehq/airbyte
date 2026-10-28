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

Replace `hydra-stage-handoff.yml`'s eligibility bash and the launched session's
§2.5 traversal with a code path.

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

**Acceptance:** handoff workflow no longer launches a Devin session for the
decision itself. Decision latency drops from minutes to seconds. Per-handoff
ACU → 0 for the common case.

---

## Phase 2 — Trigger set

Keep what works, add what's missing, and trust the engine to debounce.

**Keep:**

- `issue_comment: [created, edited]` — only until Phase 1 lands; replace with
  the completion-driven path below.
- `workflow_run` on `Connector CI` success — covers first-green on `/ai-fix`
  PRs and post-push re-eval.
- `workflow_dispatch` — manual.

**Add:**

- `wait-for-stopped-status: true` on prove-fix / review / resolve-conflicts
  dispatchers; each dispatcher calls the handoff via `repository_dispatch` on
  completion. Removes comment-marker regex entirely.
- `pull_request: [synchronize]` — push-driven re-eval. Fires on every PR push;
  hydra returns `wait` while CI pending, action when settled.
- `pull_request: [labeled]` filtered to `hyd-chain` — opt-in moment, one-pass
  kickstart.
- `schedule` — Monday 08:00 UTC (midnight PT), scoped to `label:hyd-chain` PRs
  whose `state.runs[ready].outcome === "FROZEN"`. One hydra pass per matching
  PR; re-dispatches `/ai-ready` as the engine decides. Only mechanism to
  recover from weekend-frozen `/ai-ready`.
- `repository_dispatch` from the oncall triage/fix workflows if cross-repo
  `/ai-triage → /ai-fix` ever moves into this chain. Not required for v1 — the
  sweep still catches that transition.

**Drop:**

- Nothing yet. Comment-marker trigger stays dormant as a fallback until the
  completion-driven path is proven for a week in prod.

**"Settle" is not a trigger problem.** Trigger broadly, let `assess` return
`wait` when CI is pending or sessions are in flight, trust the next event.
Natural debouncing.

**Acceptance:** every stage transition has at least one trigger.
Weekend-frozen `/ai-ready` recovers within 24h without the daily sweep.

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
   on a `hyd-chain` PR.
