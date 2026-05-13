---
plan: all
sidebar_position: 6
---

# Using the CLI with AI agents

The CLI was designed to be driven by AI agent harnesses (Claude Code, Codex, Cursor, and similar) as much as by humans. Compared to writing a custom MCP server or wiring a Python SDK call, shelling out to `airbyte-agent` gives an agent:

- A uniform `<resource> <operation>` surface that doesn't change between connectors.
- Self-describing schemas via `--describe` so the agent can plan without round-tripping documentation.
- Stable JSON-in, JSON-out payloads suitable for tool calls.
- Stable exit codes (`0`, `1`, `2`, `3`, `4`) that map cleanly onto retry policies.
- A credential model that keeps third-party secrets out of agent transcripts entirely.

## Install the bundled skills

The CLI ships with per-command [skill](https://github.com/vercel-labs/skills) documents: small markdown files with YAML frontmatter that tell an agent how and when to call each command. They live in the `skills/` directory of [`airbytehq/airbyte-agent-cli`](https://github.com/airbytehq/airbyte-agent-cli) and are designed to be consumed by skill-aware agent harnesses.

Install them with `npx skills add`:

```bash
# Install every skill into the current project
npx skills add airbytehq/airbyte-agent-cli

# Install a single skill
npx skills add airbytehq/airbyte-agent-cli --skill connectors-execute

# Preview without installing
npx skills add airbytehq/airbyte-agent-cli --list

# Install globally instead of per-project
npx skills add airbytehq/airbyte-agent-cli -g
```

Target a specific agent with `--agent claude-code` (or another supported agent). See the [`skills` CLI docs](https://github.com/vercel-labs/skills) for the full flag set.

If your harness doesn't support `npx skills`, copy or symlink the `skills/<command>/` directories into the agent's skill directory directly (for example, `~/.claude/skills/` for Claude Code).

## Three rules for agents

Every skill document repeats some version of these three rules. They're worth restating because they materially affect whether an agent's calls succeed.

### 1. Always run `connectors describe` before the first execute

Entity names, action names, and parameter shapes vary per connector. Guessing them costs round trips and produces validation errors. Run [`connectors describe`](./describe-connector) once per connector you intend to use, cache the result for the duration of the session, and read entities and actions from it.

```bash
airbyte-agent connectors describe --json '{"workspace": "default", "name": "hubspot"}'
```

### 2. Always pass parameters as `--json '{...}'`

Per-parameter flags (`--workspace`, `--name`, and so on) exist for human convenience, but agents should send a single JSON payload. JSON is:

- **Self-describing.** A reviewer reading a transcript sees the full input without inferring flag semantics.
- **Replayable.** The same payload can be saved to a file and re-run with `--json @file.json`.
- **Less prone to shell quoting bugs.** Nested objects (like `params` on [`connectors execute`](./execute)) can only be passed via JSON anyway.

The two modes are mutually exclusive; mixing them is an error.

### 3. Never ask the user for connector credentials

If your agent decides a new connector is needed, it must run [`connectors create`](./add-connector), which opens a browser tab for the user to sign in directly. The CLI does not accept third-party credentials inline, on stdin, or in any other channel. An agent that asks a user to paste an API key into chat is doing the wrong thing. That key would end up in transcripts, logs, and possibly training data.

If a user volunteers credentials anyway, decline politely and run `connectors create` instead.

## Output discipline

Two practical tips that meaningfully reduce context-window pressure:

- **Always filter responses.** Pass `select_fields` (API-side) and `--fields` (client-side) on every [`execute`](./execute#filter-the-response) call. The default response shape often includes nested objects and metadata you don't need; trimming it saves both bandwidth and prompt budget.
- **Prefer `context_store_search` over `list`.** For reads, the indexed store supports filtering, sorting, and pagination natively. Fall back to `list` only when you need real-time data or when search returns empty.

## Telemetry and execution context

The CLI emits anonymous usage telemetry by default. Agents can self-identify so internal usage can be filtered out of customer analytics:

```bash
AIRBYTE_EXECUTION_CONTEXT=agent airbyte-agent connectors execute --json '{...}'
```

Common values: `mcp`, `agent`, `direct`. Set `AIRBYTE_TELEMETRY_MODE=disabled` to turn telemetry off entirely.
