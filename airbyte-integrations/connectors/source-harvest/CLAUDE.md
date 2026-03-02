# source-harvest

Harvest time tracking API source connector built entirely on the declarative framework (no custom Python
components).

## Key Behavior Documentation

See [BEHAVIOR.md](BEHAVIOR.md) for the most important non-obvious gotchas in this connector, including:
- Harvest-Account-Id header required on every request (separate from authentication)
- Link-based cursor pagination using full URLs from response body
- Graceful degradation that silently ignores 401/403/404 errors per stream
- Report streams use date-range slicing with a different cursor format than entity streams
- WaitTimeFromHeader backoff strategy that honors Harvest's Retry-After header
- Substream patterns that scale API calls linearly with parent entity count
