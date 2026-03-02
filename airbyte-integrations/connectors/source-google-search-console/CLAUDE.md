# source-google-search-console

Google Search Console API source connector built on the declarative framework with custom Python
components for state migration, dimension extraction, and schema generation.

## Key Behavior Documentation

See [BEHAVIOR.md](BEHAVIOR.md) for the most important non-obvious gotchas in this connector, including:
- Two-level nested substream state migration for site_url + search_type partitions
- POST-based Search Analytics with positional keys array that must be mapped to dimension names
- Custom reports with dynamic schema generation based on user-selected dimensions
- Dual authentication (OAuth vs Service Account JWT) with completely separate code paths
- Configurable rate limits where most new projects default far below the connector's limit
- AggregationType override config for customers whose properties reject certain aggregation types
- Config migration from legacy string format to array format for custom reports
- Search appearance keyword streams implemented as substreams that multiply API calls
