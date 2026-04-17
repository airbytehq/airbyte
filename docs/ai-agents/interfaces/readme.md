---
sidebar_position: 4
---

# Interfaces

Airbyte Agents supports three interfaces for working with your data and your agents. Choose the interface that best fits how you want to build and run agents.

- [**Web app**](ui): The Airbyte Agents web app at [app.airbyte.ai](https://app.airbyte.ai). Talk to an Airbyte-hosted agent in [Chats](ui/chats), or define [Automations](ui/automations) that run on a schedule or webhook. Best when you want Airbyte itself to be your agent, with no code required.
- [**MCP server**](mcp): A remote, Airbyte-hosted Model Context Protocol server that connects MCP-capable agents (like Claude, Cursor, and ChatGPT) to your data. Best for conversational agents that use off-the-shelf clients.
- [**SDK**](sdk): Python SDK and platform APIs for building, authenticating, and executing agent connectors in your own applications. Best for agents you build and host yourself.

import DocCardList from '@theme/DocCardList';

<DocCardList />
