> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-zoom agent notes

Start with [CONTRIBUTING.md](CONTRIBUTING.md) for connector-specific authentication, error handling, rate limits, licence-gated streams, and test guidance.

`manifest.yaml` is declarative: shared authenticators, error handlers, and pagination live under `definitions`. Parent-stream partition routers list users and then route through meetings or webinars to detail, child, and report streams. Webinar and report paths double-encode webinar UUIDs that contain `/`; preserve this behavior.

Changing stream names, primary keys, or schema types is breaking. Follow the breaking-change release process by recording the change in `metadata.yaml` under `releases.breakingChanges` and adding a migration guide.

The user-facing page is `docs/integrations/sources/zoom.md`. Keep each changelog row on one line.
