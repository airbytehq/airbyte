---
sidebar_position: 4
---

# Interfaces

Airbyte Agents supports multiple interfaces for connecting AI agents to your data. Choose the interface that best fits how you build and run agents.

- [**MCP server**](mcp): A remote, Airbyte-hosted Model Context Protocol server that connects MCP-capable agents (like Claude, Cursor, and ChatGPT) to your data. Best for conversational agents that use off-the-shelf clients.
- [**SDK**](sdk): Python SDK and platform APIs for building, authenticating, and executing agent connectors in your own applications. Best for agents you build and host yourself.

import DocCardList from '@theme/DocCardList';

<DocCardList />
