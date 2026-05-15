---
plan: all
sidebar_position: 3
---

import DocCardList from '@theme/DocCardList';

# CLI

The Airbyte Agent CLI (`airbyte-agent`) is a single Go binary that exposes Airbyte Agents through a uniform `airbyte-agent <resource> <operation>` interface. Resource operations accept JSON in (`--json`), return JSON out, and support schema introspection via `airbyte-agent schema <resource> <operation>`. Every command exits with a stable code, so it's safe to script from a shell and easy for AI agents to discover and call at runtime. A few top-level commands (`login`, `version`, `schema`, `completion`) sit outside the resource model and don't take `--json`.

The CLI is the right interface when you want:

- A shell-first way to talk to Airbyte Agents (scripts, CI jobs, ad-hoc terminal use).
- A non-Python tool an AI-agent harness (Claude Code, Codex, and similar) can shell out to.
- A portable single-binary alternative to the [Python SDK](../sdk) or the [Agent API](../api).

Source code, releases, and bundled agent skills live at [`airbytehq/airbyte-agent-cli`](https://github.com/airbytehq/airbyte-agent-cli).

## Prerequisites

Before you install the CLI, make sure you have:

- An Airbyte Agents account. [Sign up at app.airbyte.ai](https://app.airbyte.ai) if you don't have one.
- A signed-in [app.airbyte.ai](https://app.airbyte.ai/) account. `airbyte-agent login` opens your browser to complete the sign-in and writes credentials for you; for headless machines, [`--manual`](./authenticate#headless-machines-manual) reads them from the **Your API Credentials** card in the web app. See [Authenticate](./authenticate) for the full walkthrough.
- For [`connectors create`](./add-connector), a browser on the machine running the CLI. The credential flow opens a browser tab so you can authenticate with the third-party service.

## Install

Choose the install method that fits your environment.

### Homebrew (macOS, Linux)

```bash
brew install airbytehq/tap/airbyte-agent
```

### Manual binary download

Download the archive for your platform from the [latest release](https://github.com/airbytehq/airbyte-agent-cli/releases/latest), extract it, and put `airbyte-agent` somewhere on your `PATH`. Builds are published for `linux`, `darwin`, and `windows` on both `amd64` and `arm64` (except Windows `arm64`).

### Build from source

```bash
git clone https://github.com/airbytehq/airbyte-agent-cli.git
cd airbyte-agent-cli
make build         # builds ./airbyte-agent
# or
make install       # installs to $GOBIN
```

### Verify the install

```bash
airbyte-agent version
```

## Your first command

After [authenticating](./authenticate), list the workspaces in your organization:

```bash
airbyte-agent workspaces list
```

The CLI prints JSON to stdout. Pass `--fields` to keep only the dotted paths you want (for example, `--fields workspaces.id,workspaces.name`); pipe through `jq` for anything more involved. See [Execute operations](./execute) for the full output-filtering rules.

## Command model

Resource commands follow the same shape:

```bash
airbyte-agent <resource> <operation> [flags]
```

A few top-level commands (`login`, `login show`, `version`, and `schema <resource> <operation>`) sit outside this pattern and don't take `--json`; see the [Command reference](./command-reference) for details.

There are three resources today:

| Resource | Operations | What it covers |
| --- | --- | --- |
| `organizations` | `list` | Read your organizations. |
| `workspaces` | `list`, `use` | List workspaces, and persist a default in `~/.airbyte-agent/settings.json`. |
| `connectors` | `list`, `list-available`, `describe`, `create`, `execute`, `delete` | Manage and run connectors in a workspace. |

For the full command surface, including params, flags, and exit codes, see the [Command reference](./command-reference).

### JSON in, JSON out

Every operation accepts parameters either as a single JSON document (`--json '{...}'`) or as individual flags (`--workspace foo --name bar`). The two modes are mutually exclusive. JSON is the recommended path for agents and for any payload with nested objects; flags are convenient at a human terminal.

```bash
# JSON
airbyte-agent connectors execute --json '{
  "workspace": "default",
  "name": "hubspot",
  "entity": "contacts",
  "action": "context_store_search",
  "select_fields": ["id", "email"]
}'

# Flags
airbyte-agent connectors execute \
  --workspace default --name hubspot \
  --entity contacts --action context_store_search \
  --select-fields id,email
```

To load a long JSON payload from a file, use `--json @path/to/file.json`.

### Discover before you execute

`airbyte-agent schema <resource> <operation>` returns the schema for an operation (parameters, types, and, when the operation maps to a public API route, the underlying OpenAPI request and response shapes) without running it. Use it whenever you're unsure what an operation accepts:

```bash
airbyte-agent schema connectors execute
```

For connector-specific entities and actions, [`connectors describe`](./describe-connector) is the authoritative source. Never guess what a connector supports; ask `describe` first.

A handful of operations are backed by internal-only API routes (currently `organizations list`) and return `{"type": "not_supported", ...}` on stderr with exit code `3` when introspected via `schema`. Use `airbyte-agent <resource> <operation> --help` for those.

### Exit codes and errors

The CLI returns structured JSON errors on stderr with stable exit codes you can branch on from a script or an agent:

| Exit code | Meaning |
| --- | --- |
| `0` | Success. |
| `1` | General error. |
| `2` | Authentication error. |
| `3` | Not found. |
| `4` | Validation error. |

See [Troubleshooting](./troubleshooting) for the common ones.

## Next steps

<DocCardList />
