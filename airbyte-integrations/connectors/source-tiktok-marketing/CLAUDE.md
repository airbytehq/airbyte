# source-tiktok-marketing

TikTok Marketing API source connector built on the declarative framework with custom Python components
for advertiser ID partitioning and metric transformation.

## Key Behavior Documentation

See [BEHAVIOR.md](BEHAVIOR.md) for the most important non-obvious gotchas in this connector, including:
- Dynamic sandbox vs production endpoint selection based on auth type
- Dual advertiser ID partition routers (single vs batched) for different stream types
- Empty metric values returned as "-" strings that must be transformed to null
- Semi-incremental sync with client-side filtering (full dataset fetched every sync)
- Report attribution window lookback for late-arriving conversion data
- Rate limit detection via response body code (not HTTP 429)
- Smart+ ads filtered out when missing modify_time values
- Header-based authentication with no token refresh mechanism
