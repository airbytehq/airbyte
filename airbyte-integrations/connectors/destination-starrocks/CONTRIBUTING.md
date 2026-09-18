# StarRocks version compatibility — destination-starrocks (Stream Load / Primary Key / CDC)

> This document covers the StarRocks version gating of `destination-starrocks` (Kotlin, Bulk-Load
> CDK). The gating is enforced by `StarrocksVersionGate` and validated at `check`. The user-facing
> setup guide (`docs/integrations/destinations/starrocks.md`) references this matrix.
>
> **Assumption:** the target cluster runs in **shared-data mode** (FE + CN, object storage). Feature
> gating therefore follows the **shared-data support matrix**, not the general primary-key docs —
> some PK features landed later in shared-data.

## 0. Summary

- This connector's **version gating is deliberately minimal.** At `check`/startup it does exactly two
  things: (a) **reject clusters below the shared-data 3.3 floor**, and (b) **enable JSON request-body
  compression** when the cluster is `>= 3.3.2`. That is the entire runtime effect of version detection.
- The foundation it relies on (**PRIMARY KEY tables + `__op` upsert/delete**, CSV `enclose`, JSON
  Stream Load) is guaranteed by the 3.3 floor and used unconditionally — it is not separately gated.
- The matrix below is a **StarRocks capability reference, not a list of connector behaviors.** See
  **§2.1** for exactly which rows the connector acts on, and why the rest do not apply to Airbyte's
  load model (full-row upsert/delete via Stream Load).

## 1. Version detection

The connector already connects to **9030 (MySQL protocol)** for DDL. On that same connection:

```sql
SELECT current_version();   -- e.g. "3.3.11", "3.5.4", or "4.1.1"
```

It reads the version at `check` / startup and compares it against the matrix below.

- The **only** runtime gates today: reject `< 3.3.0` (hard error at `check`), and require `>= 3.3.2`
  when JSON request-body compression is requested (else `check` fails fast). Nothing else in the
  matrix is enforced or auto-disabled by the connector.

> Why: version mismatches surface at runtime as cryptic Stream Load 4xx errors that are hard to
> debug. Validating once over 9030 before loading is well worth the cost.

## 2. Version compatibility matrix (shared-data)

Legend: ✅ available · ⚠️ conditional / caution · ❌ unsupported (needs a higher version)

| Feature (StarRocks capability; see §2.1 for what the connector uses) | shared-data since | **3.3.11** | **3.5.x** | **4.1.1** |
|---|---|:---:|:---:|:---:|
| PRIMARY KEY tables | v3.1.0 | ✅ | ✅ | ✅ |
| `__op` upsert/delete | v3.1.0 (with PK) | ✅ | ✅ | ✅ |
| `merge_condition` full-upsert (order-safety) | v3.1.0 (**Greater(≥) only**) | ✅ | ✅ | ✅ |
| partial update — row mode | v3.1.0 | ✅ | ✅ | ✅ |
| partial update — column mode | v3.3.1 | ✅ | ✅ | ✅ |
| column-mode partial **+ conditional combo** | v3.3.11 | ✅ | ✅ | ✅ (most robust) |
| request-body compression (gzip/lz4_frame/zstd, etc.) | v3.3.2 | ✅ | ✅ | ✅ |
| persistent index = `CLOUD_NATIVE` (object store) | v3.3.2 / default v3.3.8 | ⚠️ ≥3.3.8 recommended | ✅ | ✅ |
| **Merge Commit** (merge concurrent small loads) | v3.4.0 | ❌ | ✅ | ✅ |
| partial-update **automatic mode detection** | v3.5.8 / 4.0.2 | ❌ (manual) | ✅ ≥3.5.8 | ✅ |
| **parallel PK load** (publish / index / conditional) | v4.1.0 | ❌ | ❌ | ✅ |

### One line per version

- **3.3.11 (baseline):** the full connector feature set *works*, but without Merge Commit / auto-mode
  / parallel load it is the least efficient for CDC loads. The lower bound when 3.3 is already
  installed.
- **3.5.x (current stable, recommended):** all of 3.3 + **Merge Commit** (eases version pressure from
  small batches) + **automatic mode detection**. The stability/efficiency sweet spot.
  ⚠️ **JDK 17+ required from 3.5.0**.
- **4.1.1 (latest):** + **parallel PK load** for the highest throughput ceiling, and the most robust
  column-mode + conditional. Bleeding edge.

## 2.1 What this connector actually uses

Airbyte's load model is **full-row upsert/delete via Stream Load `__op` into PRIMARY KEY tables** — it
always sends complete records, never partial columns. That single fact makes most of the matrix above
irrelevant here. Concretely:

| Feature (from the matrix) | Status in this connector | Why |
|---|---|---|
| 3.3 floor check | ✅ used (gated) | `StarrocksVersionGate.validate()` rejects `< 3.3.0` at `check` |
| PRIMARY KEY tables + `__op` upsert/delete | ✅ used (ungated) | floor-guaranteed; the core of dedup/CDC |
| CSV `enclose` / JSON Stream Load | ✅ used (ungated) | floor-guaranteed (`enclose` since 3.0) |
| **request-body compression** (gzip/zstd, ≥3.3.2) | ✅ **used (gated)** | the *only* version-detected capability — JSON body only (`capabilities.compression`) |
| partial update — row mode | ❌ N/A | Airbyte sends full rows; there is nothing partial to update |
| partial update — column mode / conditional / auto-mode | ❌ N/A | same reason — partial update never applies |
| **Merge Commit** (`enable_merge_commit`, 3.4) | ❌ evaluated, not used | **ignores user-specified labels** ([docs](https://docs.starrocks.io/docs/sql-reference/sql-statements/loading_unloading/STREAM_LOAD/): *"They will be ignored if specified"*) → would break the content-addressed idempotent-retry guard; and *"not recommended if the concurrency is one"* — this connector loads a stream's batches **sequentially** (concurrency 1 per table), so there is nothing to merge |
| `merge_condition` order-safety | ⚠️ not implemented (future candidate) | relies instead on within-batch load order + cross-batch **commit order**. A monotonic ordering column (e.g. CDC `_ab_cdc_log_file`/`_pos`) would make cross-batch upserts order-safe; **Stream-Load-only** (the SQL load path can't use it). Only matters under parallel/reordered commits |
| persistent index `CLOUD_NATIVE` (3.3.8 default) | ▽ automatic | cluster default on ≥3.3.8; no connector action |
| parallel PK load (4.1) | ▽ automatic | cluster-side; no connector action |

## 3. Caveats that need "logic", not just a flag (all versions)

> **Status:** of the three below, only **#3 (`__op` reserved name)** is implemented (the connector
> rejects a source column named `__op`). #1/#2 concern `merge_condition`, which the connector does
> **not** use today (see §2.1) — they apply only if order-safe conditional upserts are added later.

Constraints to honor regardless of version — adding a spec field is not enough.

1. **`merge_condition` supports only the 'Greater (≥)' operator.**
   The ordering column for a conditional upsert (`dedup_ordering_column`) must therefore be **monotonically
   increasing**. A monotonic sequence derived from the CDC binlog position
   (`_ab_cdc_log_file` + `_ab_cdc_log_pos`) is ideal. A plain `updated_at` timestamp can break on
   ties / clock skew, so it is subject to **validation / warning**.

2. **`merge_condition` does not apply to DELETE (`__op=1`)**, plus there are restrictions on mixing
   condition columns within one batch. Load **conditional upserts and deletes in separate batches**;
   otherwise an out-of-order delete can remove a row that was later re-inserted.

3. **`__op` is a reserved column name in v3.3.6+.** If a source already has an `__op` column it
   collides and must be renamed upstream.

## 4. Recommended targets

- **Stability first:** **3.5.x** — full feature set + Merge Commit + auto mode, production-stable.
- **Throughput first:** **4.1.1** — parallel PK load + the most robust column-mode + conditional.
- **Lower bound:** **3.3.11** — below this the column-mode + conditional combo is incomplete, so it is
  not supported.

## 5. Operational notes

- **JDK 17+**: required when upgrading clusters to 3.5.0+ (a cluster-side requirement).
- **persistent index default**: shared-data PK on 3.3.8+ defaults to `CLOUD_NATIVE`.
- **Merge Commit** (3.4+): enabled via headers such as `enable_merge_commit`. It reduces version
  explosion / compaction pressure under Airbyte's frequent small batches. Not available on 3.3.x, so
  substitute with batch size / frequency tuning there.

## 6. Sources

- Stream Load SQL reference — https://docs.starrocks.io/docs/sql-reference/sql-statements/loading_unloading/STREAM_LOAD/
- Load to Primary Key tables — https://docs.starrocks.io/docs/loading/Load_to_Primary_Key_tables/
- Feature Support: Shared-data Clusters — https://docs.starrocks.io/docs/deployment/shared_data/feature-support-shared-data/
- Feature Support: Loading/Unloading — https://docs.starrocks.io/docs/loading/loading_introduction/feature-support-loading-and-unloading/
- Release notes — 3.3 / 3.4 / 3.5 / 4.0 / 4.1 (docs.starrocks.io/releasenotes/)
- Related PRs: column-mode partial in shared-data (#46516), shared-data conditional partial (#56132),
  CLOUD_NATIVE default (#52209), `__op` reserved name (#52621), 4.1 Lake column-mode conditional (#71961)
