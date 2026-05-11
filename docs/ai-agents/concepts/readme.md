---
plan: all
sidebar_position: 3
---

# Core concepts

This section covers the building blocks of Airbyte Agents: the models, resources, and platform behaviors you work with across every interface.

- [**Connect, Ask, Act**](./connect-ask-act.md): The three-layer model at the heart of the platform. Connect agents to any system through managed connectors, ask questions across all your data in one searchable layer, and let agents act on that data in real time.
- [**Agent operations**](./agent-operations.md): The unit of work in Airbyte Agents. Learn how tool calls and token usage combine into agent operations, and how AOs relate to your plan's billing.
- [**Context Store**](./context-store.md): A managed, searchable replica of your connector data. The Context Store gives agents fast, indexed access to business data without live API crawls.
- [**System architecture**](./architecture/readme.md): How the platform is organized. Covers the four interfaces, the resource hierarchy of organizations, workspaces, and connectors, and the execution model that routes agent requests.
- [**Time zones**](./time-zones.md): How Airbyte Agents stores, displays, and schedules dates and times across the web app, API, SDK, and MCP server.

import DocCardList from '@theme/DocCardList';

<DocCardList />
