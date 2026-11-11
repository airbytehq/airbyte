# Contributing to source-outreach

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Unique behaviors (summary)

Full technical detail lives in [AGENTS.md](./AGENTS.md).

1. **Authentication recovery during long syncs** — Expired access tokens are
   refreshed before retrying the interrupted page, allowing long syncs to
   continue. Persistent authentication failures and permission errors still stop
   the stream.
