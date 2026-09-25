# Peec AI source connector

This is the repository for the Peec AI source connector, written in low-code CDK
(manifest-only).

[Peec AI](https://peec.ai) tracks how brands appear in answers from AI assistants
(ChatGPT, Google AI Overview, Perplexity, …) — the discipline usually called GEO
(Generative Engine Optimisation) or AI search visibility. This connector reads the
[Peec AI Customer API](https://docs.peec.ai/api/introduction).

## Streams

| Stream | Grain | Sync mode | Cursor | Primary key |
| --- | --- | --- | --- | --- |
| `brands` | one row per tracked brand | full refresh | — | `id` |
| `model_channels` | one row per model/channel (e.g. ChatGPT, Google AI Overview) | full refresh | — | `id` |
| `brands_report` | brand × model channel × month | incremental | `month` | `month`, `brand_id`, `model_channel_id` |
| `domains_report` | domain × model channel × month | incremental | `month` | `month`, `domain`, `model_channel_id` |
| `urls_report` | url × model channel × month | incremental | `month` | *none — see below* |

### Where the common metrics live

- **Visibility score** — `visibility_count / visibility_total` in `brands_report`.
  Peec reports the numerator and denominator separately rather than a ratio, so the
  percentage stays aggregatable across periods and channels.
- **Source retrievals** — the `retrievals` / `retrieval_count` fields in
  `domains_report` (per cited domain) and `urls_report` (per cited URL).
- `brands` carries `is_own`, which marks which of the tracked brands is the project's
  own rather than a tracked competitor. It is not merely a lookup table.

## Configuration

| Field | Required | Notes |
| --- | --- | --- |
| `api_key` | yes | Created at <https://app.peec.ai/api-keys>, sent as the `x-api-key` header. |
| `start_date` | yes | `YYYY-MM-DD`. The day is ignored — the sync always starts on the 1st of that month. |
| `project_id` | no | Only needed for a **company-scoped** key. A project-scoped key (the usual case) resolves its own project, and this must be left unset. |

### Key scopes

Peec issues both **project-scoped** keys (prefix `skp-`) and company-scoped keys. They
behave differently and the connector supports both:

- A project-scoped key resolves its own project. `GET /projects` answers
  `403 Not a Company API Key`, so the connector never calls it — `check` runs against
  `brands` instead.
- A company-scoped key has no implicit project, so `project_id` must be set.

`project_id` is interpolated as `config.get('project_id', '')` and omitted from the
request entirely when unset, because the API rejects an explicit `null` with a 400.

## Incrementality

The report streams slice one calendar month per request (`step: P1M`,
`cursor_granularity: P1D`) with the start date snapped to the 1st, so a slice never
straddles two month buckets.

`lookback_window: P1M` re-reads the previous month on every sync, because Peec keeps
restating a month while chats are still landing in it. **The same month therefore
arrives more than once by design.** Downstream, keep the rows from the newest extract
for a given month rather than deduplicating on a key across extracts — the latter mixes
restated and stale numbers for the same period.

## Two things worth knowing before you model this data

### `urls_report` has no unique key, deliberately

Peec can return two rows sharing the same `(month, url, model_channel_id)`. Measured on
one month of real data: 4 such pairs in 37,844 rows, carrying 16 of 203,774 retrievals.
Three of the pairs are identical on every exposed dimension and differ only in their
metrics; the fourth also differs in `classification`. No subset of the returned fields
separates all four, so there is no key to declare.

**These rows must be summed, not deduplicated.** Declaring a primary key here would
invite a dedup that silently drops the second row of each pair. `domains_report` and
`brands_report` were verified unique on the same data.

### Offset paging is safe here empirically, not by construction

`limit` maxes out at 10000 (15000 answers 400), and a month of `urls_report` can exceed
that — so offset paging is load-bearing. Peec exposes no total order: two consecutive
walks at the same page size return the same rows in a different sequence, and `order_by`
accepts only metric columns, never brand/domain/url.

That was measured rather than assumed. The same month was walked at page sizes 10000,
7000 and 5000 — which puts the page boundaries in different places — and twice more at
10000. Every walk returned exactly the same rows and the same metric totals: nothing
lost, nothing repeated.

`integration_tests/check_paging_stability.py` pins that invariant against the live API.
It compares the multiset of rows across page sizes and deliberately does **not** assert
row positions, which are known to vary. Run it after any change to the report endpoints.

## Local development

### Testing without credentials

`unit_tests/test_manifest.py` runs the manifest against a mock Peec API — no API key and
no network needed. It covers the `x-api-key` header, month-aligned slicing, offset
pagination inside the POST body, the `AddFields` transforms, primary-key uniqueness,
record/schema conformance, and incremental resume.

The mock deliberately answers `403` to `GET /projects`, mimicking a project-scoped key,
so a regression that reintroduces a dependency on that endpoint fails loudly here rather
than in production.

```bash
python3 -m venv .venv
.venv/bin/pip install airbyte-cdk==7.10.1 jsonschema pyyaml
.venv/bin/python unit_tests/test_manifest.py
```

Pin the CDK to the version in `metadata.yaml`'s `baseImage` so the test runs on the same
runtime as the shipped image.

### Testing against the live API

```bash
export PEEC_API_KEY=<your key>
python3 integration_tests/check_paging_stability.py          # last full month
python3 integration_tests/check_paging_stability.py 2026-08  # a specific month
```

## Adding a breakdown

The report endpoints accept extra `dimensions` (`country_code`, `topic_id`, `tag_id`,
`prompt_id`, `chat_id`, `date`, `week`). To add one, append it to the stream's
`dimensions` list **and** to its `primary_key`, otherwise rows collide once aggregated.

There is also an undocumented `filters` parameter taking
`{"field": …, "operator": "in"|"not_in", "values": [...]}` over `model_id`,
`model_channel_id`, `tag_id`, `topic_id`, `prompt_id`, `country_code`, `chat_id`,
`domain`, `domain_classification`, `url`, `url_classification`, `mentioned_brand_id`,
`mentioned_brand_count` and `gap`.

**Do not assume filtering partitions the result set.** It was tempting to use
`url_classification` to split a month into single-request slices and remove paging
entirely — 11 slices, largest 9,386 rows. But the union of those slices returns 39,618
rows against the plain call's 37,844, because a URL can carry several classifications:
1,764 `(url, model_channel)` pairs come back under two of them while the unfiltered call
reports each pair once. Slicing that way double-counts them.

Any partitioning scheme must be validated the same way — run the slices, union them, and
diff the multiset against the unpartitioned call — before it is relied upon.
