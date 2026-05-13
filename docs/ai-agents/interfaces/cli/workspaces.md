---
plan: team, custom
sidebar_position: 2
---

# List and set workspaces

A **workspace** in Airbyte Agents is a container inside your organization that holds connectors and credentials. Every organization starts with a single `default` workspace. **Additional workspaces require a Team plan or higher.** If you're on the free or individual plan, you have only the one, so you can skip the rest of this page and rely on the default.

Use additional workspaces when you need to isolate credentials across tenants, teams, or environments.

The CLI lets you list workspaces and persist a default in your settings file so you don't have to pass `workspace` on every command.

## List workspaces

```bash
airbyte-agent workspaces list
```

`workspaces list` paginates automatically; the response includes every workspace in your organization. Common filters:

```bash
# Filter by substring (case-insensitive)
airbyte-agent workspaces list --json '{"name_contains": "prod"}'

# Filter by status
airbyte-agent workspaces list --json '{"status": "active"}'

# Cap the result count
airbyte-agent workspaces list --json '{"limit": 5}'
```

To trim the response to just the fields you need, pass `--fields`:

```bash
airbyte-agent workspaces list --fields data.id,data.name,data.status
```

## Set a default workspace

`workspaces use` persists a default workspace name to `~/.airbyte-agent/settings.json`. After running it, any command that takes a `workspace` parameter and doesn't receive one falls back to this value instead of the literal `"default"`.

```bash
airbyte-agent workspaces use --json '{"name": "Production"}'
```

`name` is required and is matched case-insensitively against the workspace's actual `name` field. The CLI verifies that the workspace exists before writing, and persists the canonical-cased name from the API. For example, typing `production` saves `Production` if that's how it's stored.

This is typically the second step in onboarding, right after [`configure`](./authenticate#recommended-airbyte-agent-configure). Run it again whenever you switch projects.

:::note Prerequisite
`workspaces use` writes to `~/.airbyte-agent/settings.json` and needs that file to already exist. On a fresh machine, run `airbyte-agent configure` first so the file gets created; `workspaces use` won't bootstrap a settings file from environment variables alone. If you're using env vars exclusively and don't want a settings file, pass `--workspace <name>` (or set `AIRBYTE_WORKSPACE`) on each command instead.
:::

To clear the default and fall back to `"default"`, edit `~/.airbyte-agent/settings.json` and remove the `workspace` key.

## Workspace creation and admin operations

The CLI doesn't expose workspace creation, renaming, or deletion. For those administrative operations, use the [Agent API](../api/workspaces). Once a workspace exists, the CLI can use it.
