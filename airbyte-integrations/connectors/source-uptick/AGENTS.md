> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-uptick

See [CONTRIBUTING.md](./CONTRIBUTING.md) for connector details, and the [Connector Development documentation](https://docs.airbyte.com/connector-development/) for general guidance.

- This connector is manifest-only. Do not add `components.py` without justification; prefer built-in CDK declarative components.
- When changing connector behavior (`manifest.yaml`, `metadata.yaml` runtime fields), bump `dockerImageTag` in `metadata.yaml` and add a changelog row in `docs/integrations/sources/uptick.md`. Docs-, test- and instruction-only edits do not need a version bump.
- Keep `supportLevel: community` in `metadata.yaml` until the certification epic closes.
