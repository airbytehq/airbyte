---
plan: all
sidebar_position: 5
---

# Manage workspaces and organizations

Use `workspaces` commands to list workspaces and save a default workspace. Use `organizations` commands to list organizations and save a default organization.

## List workspaces

```bash
airbyte-agent workspaces list
```

Filter by name substring:

```bash
airbyte-agent workspaces list --json '{"name_contains": "prod"}'
```

Filter by status:

```bash
airbyte-agent workspaces list --json '{"status": "active"}'
```

Limit the total number of returned rows:

```bash
airbyte-agent workspaces list --json '{"limit": 5}'
```

The CLI follows cursor pagination and returns a single JSON object:

```json
{
  "data": [
    {
      "id": "...",
      "name": "default"
    }
  ]
}
```

Use `--fields` to trim the output:

```bash
airbyte-agent workspaces list --fields id,name
```

## Set the default workspace

```bash
airbyte-agent workspaces use --json '{"name": "default"}'
```

The CLI verifies the workspace exists, then writes the canonical workspace name to `$HOME/.airbyte-agent/settings.json`. Commands that take a `workspace` parameter use this value when you omit `workspace`.

If no default workspace is configured, commands that need a workspace fall back to the literal workspace name `default`.

## List organizations

```bash
airbyte-agent organizations list
```

`organizations list` is backed by an internal route, so `airbyte-agent schema organizations list` returns `not_supported`. Use command help for its parameters:

```bash
airbyte-agent organizations list --help
```

## Set the default organization

```bash
airbyte-agent organizations use --json '{"id": "<organization-id>"}'
```

The CLI verifies the organization belongs to the authenticated account, then writes it to `$HOME/.airbyte-agent/settings.json`. Subsequent API calls use that organization unless all three credential environment variables override the settings file.
