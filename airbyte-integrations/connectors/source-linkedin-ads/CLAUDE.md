# source-linkedin-ads

LinkedIn Ads API source connector built on the declarative framework with custom Python components.

## Key Behavior Documentation

See [BEHAVIOR.md](BEHAVIOR.md) for the most important non-obvious gotchas in this connector, including:
- Safe URL encoding that preserves LinkedIn's proprietary query parameter syntax
- Analytics property chunking with an 18-field limit per request (~5 HTTP calls per record page)
- DNS resolution errors treated as transient/retryable
- Millisecond timestamp handling and multiple datetime formats across endpoints
- Reserved keyword renaming (`pivot` -> `_pivot`) for destination compatibility
- Unpublished per-endpoint rate limits with daily caps
