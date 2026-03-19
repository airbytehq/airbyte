# source-harvest

Harvest time tracking API source connector built entirely on the declarative framework (no custom Python
components).

## Key Behavior Documentation

See [BEHAVIOR.md](BEHAVIOR.md) for the most important non-obvious gotchas in this connector, including:
- Graceful degradation that silently ignores 401/403/404 errors per stream
- Report streams use date-range slicing with a different cursor format than entity streams
