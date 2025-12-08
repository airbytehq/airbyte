---
products: embedded
---

import Taxonomy from "@site/static/_taxonomy_of_data_movement.md";

# Agentic data platform

Airbyte's agentic data platform is a set of tools to help you automate, understand, move, and work with your data in coordination with AI agents. Some of these tools are standalone open source solutions, and others are pay solutions built on top of Airbyte Cloud.

The platform is a solution for all types of audiences, from AI engineers who are deploying agents in large enterprises down to individual founders who need real-time context and action in their platforms.

- **MCP Servers**: Model Context Protocol (MCP) servers for different use cases. The [**PyAirbyte MCP**](#pyairbyte-mcp) is a local MCP server for managing Airbyte connectors through AI assistants. The [**Connector Builder MCP (coming soon)**](#connector-builder-mcp) is an AI-assisted connector development.

- **Airbyte Embedded Widget**: App development teams who have signed up for Airbyte Embedded and are looking to get started onboarding customers using the Embedded Widget can follow the get started guide at the bottom of this page, which will step you through a complete sample onboarding app.

- **Authentication Proxies**: Connect safely to third party APIs using Airbyte's Authentication Proxies.

- **Direct connectors**: AI-optimized connectors, which you can use with Airbyte's MCP server or your own agents written in Python.

:::info New and growing
The agentic data platform is new and growing rapidly. Airbyte is actively seeking feedback, design partners, and community involvement. Expect this library of tools to grow and change rapidly.
:::

## Why Airbyte?

- **Agents hallucinate or fail**: Stale and incomplete data erodes agent effectiveness. AI agents need real-time context from multiple business systems to be fully effective.

- **Custom API integrations are brittle and expensive**: Airbyte's library of agentic connectors are open source. Benefit from the economy of scale as your third-party APIs evolve, add new endpoints, and deprecate old ones.

- **Agents need to write, not just read**: Airbyte provides the operational backbone needed to make agentic AI actually work in production. Fetch, write, and reason with live business data through a standardized, open protocol.

- **Agent data access needs governance and observability**: Every agent interaction is governed through row-level and user-level access controls that respect original source permissions. Complete OAuth handling and credential management means agents can only access what users are authorized to see. Every write operation is transactional and reversible with full audit trails, eliminating the governance black holes that prevent enterprises from deploying agents in production.

### The use case for agentic data

The agentic data platform is an open source solution built on the Model Context Protocol (MCP). It enables agents to fetch, search, write, and reason with live business data.

Even if you're not a data expert, you still need to interpret vendor data. That means cleaning, normalizing, stitching fields together, and transforming your and your customers' data into entities your agents can actually use.

The agentic data platform is an ideal solution when you:

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

---

## Prerequisites

Before using any Airbyte developer tools, ensure you have:

- **Airbyte Cloud account**: Sign up at [cloud.airbyte.com](https://cloud.airbyte.com)
- **Embedded access**: Contact michel@airbyte.io or teo@airbyte.io to enable Airbyte Embedded on your account
- **API credentials**: Available in your Airbyte Cloud dashboard under Settings > Applications

## Airbyte Embedded

[Airbyte Embedded](https://airbyte.com/embedded) equips product and software teams with the tools needed to move customer data and deliver context to AI applications.

### Embedded Workspaces & Widget

Airbyte Embedded creates isolated workspaces for each of your customers, allowing them to configure their own data sources while keeping their data separate and secure. The Embedded Widget provides a pre-built UI component that handles the entire user onboarding flow, from authentication to source configuration.

Once your Organization is enabled via Airbyte Embedded, you can begin onboarding customers via the Embedded Widget. You can download the code for the onboarding app [via GitHub](https://github.com/airbytehq/embedded-demoapp).

## MCP Servers

Airbyte provides multiple MCP (Model Context Protocol) servers to enable AI-assisted data integration workflows:

### PyAirbyte MCP

[The PyAirbyte MCP server](./pyairbyte-mcp.md) is a local MCP server that provides a standardized interface for managing Airbyte connectors through MCP-compatible clients. It allows you to list connectors, validate configurations, and run sync operations using the MCP protocol. This is the recommended MCP server for most use cases.

### Connector Builder MCP

[The Connector Builder MCP server](./connector-builder-mcp.md) (coming soon) will provide AI-assisted capabilities for building and testing Airbyte connectors using the Model Context Protocol.

## Proxy Requests

### API Sources

:::warning
The Airbyte Proxy feature is in alpha, which means it is still in active development and may include backward-incompatible changes. [Share feedback and requests directly with us](mailto:sonar@airbyte.io).
:::

Airbyte's Authentication Proxy enables you to submit authenticated requests to external APIs. It can be both to fetch and write data.

Here's an example of how to query an external API with the proxy:

```bash
curl -X POST -H 'Content-Type: application/json' \
-H 'Authorization: Bearer {AIRBYTE_ACCESS_TOKEN}' \
-d {"method": "GET", "url": "https://api.stripe.com/v1/balance", "headers": {"additional_header_key": "value"}}' \
'https://api.airbyte.ai/api/v1/sonar/apis/{SOURCE_ID}/request'
```

Here's an example of a POST:

```bash
curl -X POST -H 'Content-Type: application/json' \
-H 'Authorization: Bearer {AIRBYTE_ACCESS_TOKEN}' \
-d {"method": "POST", "url": "https://api.stripe.com/v1/balance", "body": {"key": "value"}}' \
'https://api.airbyte.ai/api/v1/sonar/apis/{SOURCE_ID}/request'
```

Airbyte's Authentication Proxy can be used to authenticate using a Source configured through the Widget.

The following integrations are currently supported. More will follow shortly:

- Stripe

### File Storage Sources

Airbyte's File Storage Proxy enables you to submit authenticated requests to file storage sources. It can be used to list or fetch files.

Here's an example of how to list files:

```bash
curl -X GET -H 'Content-Type: application/json' \
-H 'Authorization: Bearer {AIRBYTE_ACCESS_TOKEN}' \
'https://api.airbyte.ai/api/v1/sonar/files/{SOURCE_ID}/list/path/to/directory/or/file/prefix'
```

Here's an example of how to fetch a file:

```bash
curl -X GET -H 'Content-Type: application/octet-stream' \
-H 'Authorization: Bearer {AIRBYTE_ACCESS_TOKEN}' \
-H 'Range: bytes=0-1048575' \
'https://api.airbyte.ai/api/v1/sonar/files/{SOURCE_ID}/get/path/to/file'
```

For small files, you may omit the `Range` header.

The following integrations are currently supported. More will follow shortly:

- S3
