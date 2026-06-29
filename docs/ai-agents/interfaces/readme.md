---
plan: all
sidebar_position: 4
---

# Interfaces

Airbyte Agents supports several interfaces for working with your data and your agents. Choose the interface that best fits how you want to build and run agents.

- [**Web app**](/ai-agents/interfaces/ui): The Airbyte Agents web app at [app.airbyte.ai](https://app.airbyte.ai). Talk to an Airbyte-hosted agent in [Chats](/ai-agents/interfaces/ui/chats), or define [Automations](/ai-agents/interfaces/ui/automations) that run manually or on a schedule. Best when you want Airbyte itself to be your agent, with no code required.
- [**MCP server**](/ai-agents/interfaces/mcp): A remote, Airbyte-hosted Model Context Protocol server that connects MCP-capable agents (like ChatGPT, Claude, and Cursor) to your data. Best for conversational agents that use off-the-shelf clients.
- [**SDK**](/ai-agents/interfaces/sdk): Python SDK for building, authenticating, and executing agent connectors directly in your Python applications. Best for Python-based agents you build and host yourself.
- [**CLI**](/ai-agents/interfaces/cli): A shell-first interface for installing `airbyte-agent`, authenticating, adding connectors, and executing connector actions from scripts or agent harnesses.
- [**API**](/ai-agents/interfaces/api): HTTP API for managing connectors, tokens, and executing operations from any language or backend service. Best for non-Python backends, custom admin flows, and embedding the authentication module in your app.

import DocCardList from '@theme/DocCardList';

<DocCardList />
