---
sidebar_position: 5
---

import AgentConnectorRegistry from '@site/src/components/AgentConnectorRegistry';

# Agent connectors

Airbyte's agent connectors are Python packages that equip AI agents to call third-party APIs through strongly typed, well-documented tools. Each connector is ready to use in the Airbyte Agents platform, using any of Airbyte's [supported interfaces](../interfaces/). 

Airbyte's connectors are open source, and you can find them in the [airbyte-agent-sdk repository](https://github.com/airbytehq/airbyte-agent-sdk/tree/main/airbyte_agent_sdk/connectors).

## How agent connectors differ from data replication connectors

Agent connectors are lightweight, type-safe Python clients that let AI agents call third-party APIs directly in real time. They're not designed for [data replication](../../integrations/). If you're an experienced Airbyte user, Agent connectors don't replace existing source and destination connectors. They complement them by providing agents with real-time access to the same systems.

## All agent connectors

<AgentConnectorRegistry />
