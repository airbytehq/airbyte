import Taxonomy from "@site/static/_taxonomy_of_data_movement.md";

# Agent engine

Airbyte's Agent engine is a set of tools to help you automate, understand, move, and work with your data in coordination with AI agents. Some of these tools are standalone open source solutions, and others are pay solutions built on top of Airbyte Cloud.

The platform is a solution for all types of audiences, from AI engineers who are deploying agents in large enterprises down to individual founders who need real-time context and action in their platforms.

- **MCP Servers**: Model Context Protocol (MCP) servers for different use cases. The [**PyAirbyte MCP**](#pyairbyte-mcp) is a local MCP server for managing Airbyte connectors through AI assistants. The [**Connector Builder MCP (coming soon)**](#connector-builder-mcp) is an AI-assisted connector development.

- **Airbyte Embedded**: Add hundreds of integrations into your product instantly. Your end-users can authenticate into their data sources and begin syncing data to your product. You no longer need to spend engineering cycles on data movement. Focus on what makes your product great, rather than maintaining ELT pipelines.

- **AI connectors**: AI-optimized, type-safe connectors, usable with Airbyte's Connector MCP server or your own Python agents.

:::info New and growing
The Agent engine is new and growing. Airbyte is actively seeking feedback, design partners, and community involvement. Expect this library of tools to grow and change rapidly.
:::

## Why Airbyte?

- **Agents hallucinate or fail**: Stale and incomplete data erodes agent effectiveness. AI agents need real-time context from multiple business systems to be fully effective.

- **Custom API integrations are brittle and expensive**: Airbyte's library of agentic connectors are open source. Benefit from the economy of scale as third-party APIs evolve, add new endpoints, and deprecate old ones.

- **Agents need to write, not just read**: Airbyte provides the operational backbone needed to make agentic AI actually work in production. Fetch, write, and reason with live business data through a standardized, open protocol.

### The use case for agentic data

The Agent engine is an open source solution built on the Model Context Protocol (MCP). It enables agents to fetch, search, write, and reason with live business data.

Even if you're not a data expert, you still need to interpret vendor data. That means cleaning, normalizing, stitching fields together, and transforming your and your customers' data into entities your agents can actually use.

The Agent engine is an ideal solution when you:

- Don't want storage
- Care a lot about freshness and latency
- Are working with a small amount of data
- Need to trigger side effects, like sending an email or closing a ticket

The agenda data platform _isn't_ ideal when you:

- Need all your data in one place
- Need to join across datasets
- Need more pipelines that can be slower
- Want storage
- Want to update content, but not trigger side effects
- Rely on APIs that aren't good

If agentic data isn't what you're looking for, [data replication](/platform) might be.

### Taxonomy of data movement

<Taxonomy />

## Airbyte Embedded

[Airbyte Embedded](embedded) equips product and software teams with the tools needed to move customer data and deliver context to AI applications.

Airbyte Embedded creates isolated workspaces for each of your customers, allowing them to configure their own data sources while keeping their data separate and secure. The Embedded Widget provides a pre-built UI component that handles the entire user onboarding flow from authentication to source configuration.

Once Airbyte enables your organizaton on Airbyte Embedded, you can begin onboarding customers via the Embedded Widget. You can download the Embedded demo app [from GitHub](https://github.com/airbytehq/embedded-demoapp).

## AI connectors

Airbyte's AI connectors are Python packages that equip AI agents to call third-party APIs through strongly typed, well-documented tools. Each connector is ready to use directly in your Python app, in an agent framework, or exposed through an MCP. [Learn more >](connectors)

## MCP Servers

Airbyte provides multiple MCP (Model Context Protocol) servers to enable AI-assisted data integration workflows:

### PyAirbyte MCP

[The PyAirbyte MCP server](./mcp-servers/pyairbyte-mcp.md) is a local MCP server that provides a standardized interface for managing Airbyte connectors through MCP-compatible clients. It allows you to list connectors, validate configurations, and run sync operations using the MCP protocol. This is the recommended MCP server for most use cases.

### Connector MCP

Use [AI connectors](connectors) to interact with your data using natural language.

### Connector Builder MCP

[The Connector Builder MCP server](./mcp-servers/connector-builder-mcp.md) (coming soon) will provide AI-assisted capabilities for building and testing Airbyte connectors using the Model Context Protocol.
