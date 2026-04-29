---
sidebar_position: 2
sidebar_label: Claude Code
---

# Claude Code

[Claude Code](https://docs.claude.com/en/docs/claude-code/overview) is the coding agent from Anthropic that runs in your terminal and integrates with editors like VS Code and Cursor. The [airbyte-agent-sdk](https://github.com/airbytehq/airbyte-agent-sdk) repository publishes a set of Claude skills that teach Claude Code how to build agents on top of the Airbyte typed Python SDK. Once you install the skills, Claude Code reads them on demand whenever you ask it to work with Airbyte connectors.

## What the skills cover

The airbyte-agent-sdk repository ships four skills under `.claude/skills/`:

| Skill | What it teaches Claude Code |
| ----- | --------------------------- |
| `bootstrapping-agent` | Wiring a single Airbyte connector into a PydanticAI or Claude SDK agent, including `AirbyteAuthConfig`, connector initialization, and the `tool_utils` decorator pattern. |
| `building-multi-connector-agent` | Scaffolding a complete agent with multiple Airbyte connectors, composing tools, and writing the run loop. |
| `discovering-connectors` | Enumerating the available Airbyte connectors and exploring a connector's entities, actions, and schemas at runtime. |
| `airbyte-sdk-reference` | Reference material for the public SDK API, including `configure()`, `connect()`, `Workspace`, `tool_utils`, `list_entities()`, and `entity_schema()`, plus PydanticAI and Claude SDK code patterns. |

Each skill is a `SKILL.md` file with YAML front matter that Claude Code uses to decide when to load it. You don't need to paste these into context yourself. Claude Code pulls them in automatically when a prompt matches the skill's description.

## Install the skills

Pick the approach that matches how you use Claude Code.

### Recommended: install as a Claude Code plugin

This is the native path for Claude Code and the option that needs the least maintenance.

1. In Claude Code, add the marketplace:

   ```text
   /plugin marketplace add airbytehq/airbyte-agent-sdk
   ```

2. Install the plugin:

   ```text
   /plugin install airbyte-agent-sdk@airbyte-agent-sdk
   ```

Claude Code pulls the skills from the repository's `.claude/skills/` directory. Re-run `/plugin update` to pick up new skills as Airbyte adds them.

### Alternative: install with skills.sh

[skills.sh](https://skills.sh) is a cross-agent installer that works for Claude Code, Codex, Cursor, OpenCode, and 40+ other agents. Use it if you want the same skills available in multiple agents without installing them separately.

```bash
npx skills add airbytehq/airbyte-agent-sdk
```

The installer detects the agents it finds on your machine and wires the skills into each one. For Claude Code specifically, it writes the skills into your user-level `~/.claude/skills/` directory.

## Use the skills

Once you install the skills, you don't need any special command to invoke them. Prompt Claude Code the way you normally would. For example:

- _"Build a PydanticAI agent that reads Stripe customers."_
- _"Add a HubSpot connector to this agent."_
- _"List the entities available on the Salesforce connector."_

Claude Code matches the prompt against each skill's front matter description, loads the relevant skill, and uses its instructions to generate code that matches the patterns in the Airbyte Agent SDK.

## Credentials

The skills assume you're using the hosted Airbyte platform, which handles credentials, rate limiting, and execution for you. Before Claude Code runs the generated agent, set these environment variables (get the client ID and secret from [app.airbyte.ai](https://app.airbyte.ai)):

```bash
AIRBYTE_CLIENT_ID=your_client_id
AIRBYTE_CLIENT_SECRET=your_client_secret
AIRBYTE_WORKSPACE_NAME=your_workspace_name
```

See [Manage your user profile](../../../admin/profile.md) for where to find these credentials in the Airbyte Agents web app.
