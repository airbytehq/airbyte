> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-github

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Authentication: one shared authenticator, always

The connector is mid-migration: some streams come from `manifest.yaml`, the rest are Python
`HttpStream` classes. Both sides **must** use the same authenticator instance, because
`RateLimitedMultipleTokenAuthenticator` tracks each token's remaining REST/GraphQL quota in
local counters. Two instances over the same tokens each believe they own the full budget, so
the connector plans for twice the quota GitHub grants and overruns the rate limit.

`SourceGithub._get_authenticator()` gets that instance by asking the manifest's component
factory for `definitions.requester_base.authenticator`. This reads like it constructs a new
one but does not: `ModelToComponentFactory` caches these by resolved constructor arguments
specifically so every stream shares one set of counters. The cache key is value-based, so pass
the **transformed** config — a different `api_url`, token list or `max_waiting_time` produces a
different instance. `test_authenticator_instance_is_shared_with_manifest_streams` guards this;
do not add a second authenticator when migrating further streams.

Reactive token rotation (rotate instead of waiting out a long reset) lives in
`utils.rotate_authenticator_token`, called from `GithubStreamABCBackoffStrategy`. It uses CDK
private state as a fallback until the CDK exposes a public rotation hook.

## Incremental Stream Considerations

The GitHub REST and GraphQL APIs support `since` parameter on many list endpoints and `updated` sorting. The connector is a Python CDK connector with stream classes extending `GithubStream`.

**Connector type:** Python CDK

**Analysis status:** Pure Python CDK connector. Full stream-by-stream analysis requires Python code review.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
