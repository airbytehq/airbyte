# source-google-analytics-data-api: Unique Behaviors

## 1. Positional Key-Value Array Extraction

GA4's RunReport API returns dimension and metric headers separately from their values. Each row contains `dimensionValues` and `metricValues` as flat arrays of objects (e.g., `[{"value": "20231001"}, {"value": "organic"}]`), not as key-value pairs. The connector uses `KeyValueExtractor` to zip the header names with the flat value stream, chunking by the number of keys to reconstruct individual records.

Similarly, `CombinedExtractor` merges records from separate sub-extractors (one for dimensions, one for metrics) by zipping them together, so each final record contains both dimension and metric fields.

**Why this matters:** Unlike most APIs that return records as self-describing objects, GA4 returns positional data that only makes sense when paired with the separately-returned header definitions. Any change to the dimensions or metrics requested will shift all value positions, and the extraction logic must correctly chunk the flat value array by key count.
