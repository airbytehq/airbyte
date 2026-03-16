---
sidebar_position: 7
---

# Claude Code skills

Airbyte provides [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) for the [Agent Engine](../). Skills are reusable instruction sets that teach Claude Code how to set up and operate Airbyte's agent connectors. When you install a skill, Claude gains the context it needs to help you configure connectors, write integration code, and troubleshoot issues without you having to explain Airbyte's APIs from scratch.

## What skills do

A skill is a structured document that Claude Code reads when you invoke it. It contains setup instructions, code examples, authentication patterns, and API usage guidance. When you ask Claude for help with a task the skill covers, Claude follows the skill's instructions to guide you through the process.

For example, the `airbyte-agent-connectors` skill teaches Claude how to:

- Set up agent connectors in Platform Mode or OSS Mode
- Configure authentication for different services
- Use the entity-action API pattern that all connectors share
- Integrate connectors with agent frameworks like Pydantic AI and LangChain
- Configure the MCP server for Claude Desktop and Claude Code

## Available skills

Skills are maintained in the [airbyte-agent-connectors](https://github.com/airbytehq/airbyte-agent-connectors/tree/main/skills) repository. Refer to that repository for the latest list of available skills and their documentation.

## Install a skill

You can install skills from the Claude Code plugin marketplace or manually from the repository.

### Install from the plugin marketplace

In Claude Code, add the plugin repository:

```text
/plugin marketplace add airbytehq/airbyte-agent-connectors
```

Then install the skill you want. For example, to install the agent connectors skill:

```text
/plugin install airbyte-agent-connectors@airbyte-agent-connectors
```

### Install manually

Clone the skill files into your project's `.claude/skills` directory:

```bash
mkdir -p .claude/skills
git clone --depth 1 https://github.com/airbytehq/airbyte-agent-connectors.git /tmp/airbyte-skills
cp -r /tmp/airbyte-skills/skills/airbyte-agent-connectors .claude/skills/
rm -rf /tmp/airbyte-skills
```

## Use a skill

After installing, invoke the skill in Claude Code by typing its name as a slash command. For example:

```text
/airbyte-agent-connectors
```

You can also ask Claude directly and it uses the skill's knowledge automatically. Try prompts like:

- "Set up a Stripe connector in Platform Mode"
- "Connect to GitHub using OSS Mode"
- "Configure Airbyte MCP tools"

## Build your own skills

You can create custom skills that extend or complement the ones Airbyte provides. Skills are markdown files that follow the [Claude Code skill format](https://docs.anthropic.com/en/docs/claude-code/skills). Place your skill files in your project's `.claude/skills` directory.

For reference, examine the structure of the skills in the [airbyte-agent-connectors repository](https://github.com/airbytehq/airbyte-agent-connectors/tree/main/skills). Each skill contains:

- A `SKILL.md` file with instructions that Claude reads
- A `README.md` file with human-readable documentation
- A `references/` directory with detailed reference material

## Requirements

- Python 3.11 or later
- [uv](https://github.com/astral-sh/uv) for package management
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview)
