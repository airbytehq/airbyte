---
plan: all
sidebar_position: 3
---

# Describe a connector

Use `connectors describe` to inspect a configured connector before executing actions against it. The response includes the connector details plus a `schema` object returned by the connector's `describe` action.

Run this command before executing. Entity names, action names, parameters, and field names vary by connector.

## Describe by name

```bash
airbyte-agent connectors describe --json '{
  "workspace": "default",
  "name": "GitHub"
}'
```

When you use `name`, include `workspace`. If you omit `workspace`, the CLI falls back to your saved default workspace, then to `default`.

## Describe by ID

```bash
airbyte-agent connectors describe --json '{
  "id": "<connector-id>"
}'
```

Use `id` when two connectors in a workspace have the same name or when you want to avoid name resolution.

## Read the schema

The response shape is connector-specific, but the `schema` object is the contract for execution. Use it to find:

- Available entities, such as `issues`, `contacts`, or `messages`.
- Supported actions for each entity, such as `context_store_search`, `list`, `get`, `create`, or `update`.
- Required and optional `params` for each action.
- Fields you can request with `select_fields` or remove with `exclude_fields`.

Use `--fields` to focus the output when you only need part of the schema:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "default",
  "name": "GitHub"
}' --fields id,name,schema
```

## Resolve errors

- `not_found`: run `airbyte-agent connectors list --json '{"workspace": "default"}'` and confirm the connector name or ID.
- `validation_error`: pass either `id` or `name` with `workspace`, not both.
- `auth_error` or `unauthorized`: run `airbyte-agent login`, then retry.
