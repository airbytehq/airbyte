---
plan: all
sidebar_position: 3
---

import DocCardList from '@theme/DocCardList';

# CLI

The Airbyte Agent CLI (`airbyte-agent`) is a Go command-line interface for Airbyte Agents. Use it from a terminal, script, CI job, or agent harness to list workspaces, add connectors, inspect connector schemas, and execute connector actions.

Resource commands use this shape:

```bash
airbyte-agent <resource> <operation> [flags]
```

Most resource operations accept JSON input with `--json` and print JSON output. The CLI also exposes `airbyte-agent schema <resource> <operation>` so scripts and agents can discover operation parameters without making an API call.

## When to use the CLI

- You want a shell-first interface to Airbyte Agents.
- You're building an AI agent harness that invokes command-line tools and parses JSON output.
- You need a portable binary that works in CI pipelines, shell scripts, or headless environments.
- You prefer local execution and a non-Python alternative to the [SDK](../sdk).

If your agent already speaks the Model Context Protocol, the [MCP server](../mcp) offers the same connectors with zero install. If you're writing Python, the [SDK](../sdk) gives you typed, in-process access. For raw HTTP control or non-Python backends, see the [API](../api).

Source code and releases live in the [`airbytehq/airbyte-agent-cli`](https://github.com/airbytehq/airbyte-agent-cli) repository.

## Requirements

Before you begin, make sure you have:

- An Airbyte Agents account. Sign up at [app.airbyte.ai](https://app.airbyte.ai) if you don't have one.
- A browser on the machine running the CLI for the default [`airbyte-agent login`](./authenticate) flow and for [`connectors create`](./add-connector). Headless machines can use `airbyte-agent login --manual`, but adding connector credentials still requires the browser widget.
- Access to any third-party account you want to connect. The CLI never accepts third-party credentials directly.

## Install

Choose one install method.

If you're installing the CLI for an AI agent, use the install script so the bundled agent skill is installed with the binary. Then follow [Use the CLI with AI agents](./using-with-ai-agents) for the recommended skill setup and command sequence.

### Install script

```bash
curl -fsSL https://airbyte.ai/install.sh | bash
```

The install script installs the latest `airbyte-agent` binary and the bundled agent skill. You can change its behavior with environment variables:

- `AIRBYTE_AGENT_VERSION`: install a specific release tag.
- `AIRBYTE_AGENT_INSTALL_DIR`: choose the binary install directory.
- `AIRBYTE_AGENT_SKILLS_DIR`: choose the agent skill install directory.
- `AIRBYTE_AGENT_SKIP_SKILLS=1`: install only the binary.

### Homebrew

```bash
brew install airbytehq/tap/airbyte-agent-cli
```

### Manual binary download

Download the archive for your platform from the [latest release](https://github.com/airbytehq/airbyte-agent-cli/releases/latest), extract it, and put `airbyte-agent` somewhere on your `PATH`.

### Build from source

```bash
git clone https://github.com/airbytehq/airbyte-agent-cli.git
cd airbyte-agent-cli
make build
```

The binary is written to `./airbyte-agent`. To install to your Go binary directory instead, run `make install`.

### Verify the install

```bash
airbyte-agent version
```

If your shell can't find `airbyte-agent` after running the install script, reopen the shell or add the install directory to `PATH`. The default script install location is usually `$HOME/.local/bin` unless you set `AIRBYTE_AGENT_INSTALL_DIR`.

## Authenticate

Run:

```bash
airbyte-agent login
```

The browser flow signs you in to `airbyte.ai`, fetches the credentials the CLI needs, and writes them to `$HOME/.airbyte-agent/settings.json` with `0600` permissions. It doesn't prompt for a workspace; use `workspaces use` to change the saved default after login. If you're on a headless machine, use `airbyte-agent login --manual`.

For setup details, environment variables, and the settings file format, see [Authenticate](./authenticate).

## Run your first command

List workspaces:

```bash
airbyte-agent workspaces list
```

Print only the fields you need:

```bash
airbyte-agent workspaces list --fields id,name
```

List configured connectors in the default workspace:

```bash
airbyte-agent connectors list --json '{"workspace": "default"}' --fields id,name
```

## Command model

The CLI has three resource groups:

- `organizations`: list organizations and save a default organization.
- `workspaces`: list workspaces and save a default workspace.
- `connectors`: list available connectors, create connectors, list configured connectors, describe connector schemas, execute actions, update connector credentials, and delete connectors.

Top-level commands include `login`, `login show`, `schema`, `version`, and `completion`.

For the full command surface, see the [Command reference](./command-reference).

## JSON input and output

Resource operations accept input two ways:

- `--json '{...}'` for one JSON payload.
- Per-parameter flags, such as `--workspace default --name GitHub`.

The two modes are mutually exclusive. Use JSON for agents, scripts, nested payloads, and commands you want to replay.

```bash
airbyte-agent connectors execute --json '{
  "workspace": "default",
  "name": "GitHub",
  "entity": "issues",
  "action": "context_store_search",
  "select_fields": ["id", "title", "state"],
  "params": {
    "limit": 10
  }
}'
```

Load longer payloads from a file with `@filename`:

```bash
airbyte-agent connectors execute --json @request.json
```

## Schema discovery

Run `schema` before composing a command you haven't used before:

```bash
airbyte-agent schema connectors execute
```

The response includes CLI parameters plus the underlying OpenAPI request and response schemas when a published API schema exists. Some internal operations, such as `organizations list`, don't have a published schema. For those, the CLI returns a `not_supported` JSON error and points you to `--help`:

```json
{
  "type": "not_supported",
  "message": "Schema is not available for organizations list. Use --help for command details."
}
```

## Learn more

<DocCardList />
