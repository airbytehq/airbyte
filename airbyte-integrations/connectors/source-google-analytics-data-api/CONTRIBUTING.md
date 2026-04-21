# source-google-analytics-data-api: Unique Behaviors

## Important
This is **Google Analytics 4 (GA4)** (`source-google-analytics-data-api`), NOT the deprecated Universal Analytics (`source-google-analytics-v4`). All work goes here.


## Important: Naming Convention — GA4 vs Universal Analytics

This connector is **Google Analytics 4 (GA4)** with package name `source-google-analytics-data-api`. It is very commonly confused with the legacy connector **Google Analytics (Universal Analytics)** with package name `source-google-analytics-v4`.

The "GA4" identifier in the modern Google Analytics connector and the legacy Universal Analytics API being on "v4" often causes these to be mixed up. Now that the legacy Universal Analytics API was fully deprecated on **July 1, 2024**, no development work will ever be done in the `source-google-analytics-v4` package again. All work should be done in `source-google-analytics-data-api` from now on.

## 1. Positional Key-Value Array Extraction

GA4's RunReport API returns dimension and metric headers separately from their values. Each row contains `dimensionValues` and `metricValues` as flat arrays of objects (e.g., `[{"value": "20231001"}, {"value": "organic"}]`), not as key-value pairs. The connector uses `KeyValueExtractor` to zip the header names with the flat value stream, chunking by the number of keys to reconstruct individual records.

Similarly, `CombinedExtractor` merges records from separate sub-extractors (one for dimensions, one for metrics) by zipping them together, so each final record contains both dimension and metric fields.

**Why this matters:** Unlike most APIs that return records as self-describing objects, GA4 returns positional data that only makes sense when paired with the separately-returned header definitions. Any change to the dimensions or metrics requested will shift all value positions, and the extraction logic must correctly chunk the flat value array by key count.

## 2. Two-Level Jinja Interpolation in Component Mappings

The manifest's `components_mapping` section uses two distinct levels of Jinja interpolation that execute at different times:

1. **Template-level interpolation** resolves `components_values` during stream template building (e.g., `{{ components_values["metrics"] }}` expands into the actual metric list from the config).
2. **Runtime interpolation** resolves `stream_slice`, `config`, and `response` during sync execution (e.g., `{{ stream_slice.start_time }}`).

To prevent the second level from being evaluated during template building (when `stream_slice` doesn't exist yet), the manifest wraps runtime expressions in `{% raw %}...{% endraw %}` blocks. For example:
```
value: "{% raw %}{{ stream_slice.start_time or config.get('date_ranges_start_date', day_delta(-730, '%Y-%m-%d')) }}{% endraw %}"
```

The schema filter condition goes even further, using string concatenation with `~` to inject template-level values into a runtime expression:
```
{{ '{{ record.keys() | list | first in ' ~ (components_values["metrics"] | tojson) ~ ' }}' }}
```

**Why this matters:** Editing any interpolation in the `components_mapping` section requires understanding which level of interpolation applies. Forgetting a `{% raw %}` wrapper will cause a template build failure when the runtime variable doesn't exist yet. Conversely, wrapping a `components_values` reference in `{% raw %}` will leave it unresolved, producing broken requests.

## 3. Fully Dynamic Stream Construction from Config

Every stream in this connector is generated dynamically via `ConfigComponentsResolver`. There are no statically-defined streams in the manifest — only a `google_analytics_stream_template` that serves as a blueprint. The resolver takes user-defined custom reports (dimensions, metrics, optional pivots, cohorts, dimension filters) and the list of property IDs, then uses 12+ `ComponentMappingDefinition` entries to override nearly every part of the template:

- The API path switches between `:runReport` and `:runPivotReport` based on whether pivots are configured
- Pagination is conditionally disabled (`NoPagination`) for pivot reports since the GA4 API doesn't support pagination on pivot queries
- The incremental sync cursor is auto-detected by scanning dimensions for date-like fields (`date`, `yearWeek`, `yearMonth`, `year`), with the first match becoming the cursor field
- Stream naming follows a backward-compatible convention: the first property ID uses the plain report name, while additional property IDs get a `Property<id>` suffix (e.g., `devices` vs `devicesProperty5729978930`)
- The schema is constructed at build time by fetching metadata from the GA4 API and filtering it against the requested metrics, then adding dimension fields via schema transformations

**Why this matters:** There is no single place in the manifest that shows what a given stream looks like at runtime. To understand the final shape of a stream, you must mentally execute the 12+ component mappings against the user's config. Adding a new feature (e.g., a new report parameter) requires adding a mapping entry and understanding how it interacts with all the conditional branches.

## 4. DimensionFilter Config Transformation

The connector uses a custom `DimensionFilterConfigTransformation` component to reshape dimension filter definitions from the user-facing config format into the format required by the GA4 RunReport API. This is performed as a record transformation at sync time, not as a config migration.

The transformation handles four filter types (`andGroup`, `orGroup`, `notExpression`, `filter`) and four sub-filter types (`stringFilter`, `inListFilter`, `numericFilter`, `betweenFilter`), each with different structural requirements. For example, `matchType` and `operation` fields arrive as single-element arrays from the config UI and must be unwrapped to plain strings.

**Why this matters:** The config schema for dimension filters looks nothing like the API request schema. If you need to add a new filter type or modify existing filter behavior, changes must be made in the `DimensionFilterConfigTransformation` component rather than in the manifest's request body interpolation, because the interpolation simply passes through the already-transformed result.

## 5. Cohort Reports Disable Date Ranges and Incremental Sync

When a custom report includes a `cohortSpec` with `enabled: "true"`, the manifest's interpolation conditionally:
- Replaces `dateRanges` in the request body with a `cohortSpec` block
- Omits the `startDate` and `endDate` fields from record transformations and schema transformations
- Skips adding the `DatetimeBasedCursor` incremental sync component entirely

This means cohort reports are always full-refresh with no incremental support, and their request body structure is fundamentally different from non-cohort reports.

**Why this matters:** The same stream template produces two structurally different API requests depending on whether cohorts are enabled. Testing or modifying cohort behavior requires tracing through all the `{% if cohort %}` conditionals scattered across multiple component mappings to understand the full impact.

## 6. Rate Limit Quota Cannot Be Self-Service Increased

Most Google APIs allow quota increases through the [API & Services dashboard on GCP](https://console.cloud.google.com/apis/dashboard?project=prod-ab-cloud-proj). However, the Google Analytics Data API is **not** one of them — the quota cannot be self-service increased from the GCP console.

If rate-limited requests increase and a higher quota is needed, you must reach out to the DoIT contact (via Ralph or Davin) to request a quota increase on our behalf.

**Why this matters:** Unlike most Google connectors where rate limit issues can be resolved by bumping quotas in the GCP console, GA4 rate limit issues require an external escalation through DoIT. This means rate limit problems cannot be quickly self-resolved and require coordination with external parties.
