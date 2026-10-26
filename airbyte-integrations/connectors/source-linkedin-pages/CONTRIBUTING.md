# Contributing to source-linkedin-pages

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Pinned LinkedIn API version** -- every request names a LinkedIn API version, and LinkedIn retires each version about a year after release. Bump it at least yearly or every connection fails.
2. **Time-bound statistics windows** -- LinkedIn only serves the last 12 months up to 2 days ago, rejects day windows shorter than 24 hours and month windows that end inside the month they start in. The connector requests whole days, or complete months that arrive 2 days after they end.
3. **No API budget: LinkedIn does not publish its rate limits** -- limits are per app and per member and are not public, so the connector retries `429` with backoff instead of pacing itself.
4. **Cursorless full-refresh streams** -- the organization profile and the four lifetime totals have nothing a cursor could track, so they are always synced in full.
5. **Posts pagination follows LinkedIn's next link** -- LinkedIn can return a short page of posts before the last one, so the connector keeps paging until LinkedIn stops sending a next link.
6. **Comments and reactions send requests per post on every sync** -- each sync re-reads comments and reactions for every post modified since the Start Date, so request volume grows with the number of posts.

## Notes for reviewers

- `org_id` stays `airbyte_secret` and `credentials` stays optional in the spec: the spec backward-compatibility check treats both changes as breaking, and neither affects how syncs run.
