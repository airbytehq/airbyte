---
sidebar_position: 3
sidebar_label: Codex
---

# Codex

[Codex](https://developers.openai.com/codex) is the coding agent from OpenAI that runs locally in your terminal and loads skills from `~/.codex/skills/`. The [airbyte-agent-sdk](https://github.com/airbytehq/airbyte-agent-sdk) repository publishes a set of Codex skills that teach Codex how to build agents on top of the Airbyte typed Python SDK. Once you install the skills, Codex reads them on demand whenever you ask it to work with Airbyte connectors.

## What the skills cover

The airbyte-agent-sdk repository ships four skills under `.codex/skills/`:

| Skill | What it teaches Codex |
| ----- | --------------------- |
| `bootstrapping-agent` | Wiring a single Airbyte connector into a PydanticAI or Claude SDK agent, including `AirbyteAuthConfig`, connector initialization, and the `tool_utils` decorator pattern. |
| `building-multi-connector-agent` | Scaffolding a complete agent with multiple Airbyte connectors, composing tools, and writing the run loop. |
| `discovering-connectors` | Enumerating the available Airbyte connectors and exploring a connector's entities, actions, and schemas at runtime. |
| `airbyte-sdk-reference` | Reference material for the public SDK API, including `configure()`, `connect()`, `Workspace`, `tool_utils`, `list_entities()`, and `entity_schema()`, plus PydanticAI and Claude SDK code patterns. |

Each skill is a directory that contains a `SKILL.md` file and an `agents/openai.yaml` manifest. You don't need to paste these into context yourself. Codex loads a skill when a prompt matches its description.

## Install the skills

Pick the approach that matches how you use Codex.

### Recommended: install with skills.sh

[skills.sh](https://skills.sh) is a cross-agent installer that works for Codex, Claude Code, Cursor, OpenCode, and 40+ other agents. It's the lowest-friction way to get the Airbyte skills into Codex.

```bash
npx skills add airbytehq/airbyte-agent-sdk
```

The installer writes the skills into `~/.codex/skills/` and keeps them up to date when you re-run the command.

### Alternative: clone and symlink

If you'd rather manage the skills directly, clone the repository and symlink the skills into your Codex skills directory:

```bash
git clone https://github.com/airbytehq/airbyte-agent-sdk ~/.codex/skills/airbyte-agent-sdk-src
ln -s ~/.codex/skills/airbyte-agent-sdk-src/.codex/skills/* ~/.codex/skills/
```

To pick up new or updated skills, run `git pull` inside `~/.codex/skills/airbyte-agent-sdk-src`.

## Use the skills

Once you install the skills, prompt Codex the way you normally would. For example:

- _"Build a PydanticAI agent that reads Stripe customers."_
- _"Add a HubSpot connector to this agent."_
- _"List the entities available on the Salesforce connector."_

Codex matches the prompt against each skill's description, loads the relevant skill, and uses its instructions to generate code that matches the patterns in the Airbyte Agent SDK.

## Credentials

The skills assume you're using the hosted Airbyte platform, which handles credentials, rate limiting, and execution for you. Before Codex runs the generated agent, set these environment variables (get the client ID and secret from [app.airbyte.ai](https://app.airbyte.ai)):

```bash
AIRBYTE_CLIENT_ID=your_client_id
AIRBYTE_CLIENT_SECRET=your_client_secret
AIRBYTE_WORKSPACE_NAME=your_workspace_name
```

See [Manage your user profile](../../../admin/profile.md) for where to find these credentials in the Airbyte Agents web app.
