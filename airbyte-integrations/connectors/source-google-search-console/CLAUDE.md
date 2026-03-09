# source-google-search-console

Google Search Console API source connector built on the declarative framework with custom Python
components for state migration, dimension extraction, and schema generation.

## Key Behavior Documentation

See [BEHAVIOR.md](BEHAVIOR.md) for the most important non-obvious gotchas in this connector, including:
- POST-based Search Analytics with positional keys array that must be mapped to dimension names
- Configurable rate limits where most new projects default far below the connector's limit
- AggregationType override config for customers whose properties reject certain aggregation types
