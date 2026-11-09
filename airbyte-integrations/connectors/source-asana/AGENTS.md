> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# Contributing to source-asana

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Asana API supports `modified_since` filtering on tasks and other endpoints. PR airbytehq/airbyte#76838 (in flight) adds incremental sync for the `tasks` stream.

**Connector type:** Manifest-only (declarative CDK), defined in the root `manifest.yaml`.

**Analysis status:** All 20 streams currently use full refresh.

### Future incremental stream candidates

- Incremental support is deferred until after the manifest-only migration.

## Request fields

Each stream sets `retriever.requester.request_parameters.opt_fields`. Preserve schema property order:
scalars and scalar arrays use the property name; objects and arrays of objects use `property.gid`.
For tasks, use bare `custom_fields`, `hearts.user.gid`, `likes.user.gid`, and
`memberships.(project|section).gid`. For users, use bare `photo`.
Requester references merge shallowly, so every stream's requester override must include its complete request parameter map.
When changing schemas, update the fields and the behavioral drift guard in `unit_tests/mock_server/`.
