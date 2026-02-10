---
sidebar_position: 1
---

# About Agent Engine

import Taxonomy from "@site/static/_taxonomy_of_data_movement.md";

Airbyte's Agent Engine is a data layer for AI agents. Use the Agent Engine as a cloud platform to manage connectors, credentials, and data replication for your agents. You can also use Airbyte's open source agent connectors as standalone Python packages, import them into your AI agents, and manage storage and credentials yourself.

<!-- - **Agents hallucinate or fail**: Stale and incomplete data erodes agent effectiveness. AI agents need real-time context from multiple business systems to be fully effective.

- **Custom API integrations are brittle and expensive**: Airbyte's library of agentic connectors are open source. Benefit from the economy of scale as third-party APIs evolve, add new endpoints, and deprecate old ones.

- **Agents need to write, not just read**: Airbyte provides the operational backbone needed to make agentic AI actually work in production. Fetch, write, and reason with live business data through a standardized, open protocol.

### The use case for agentic data

The Agent engine enables agents to fetch, search, and reason with live business data.

Even if you're not a data expert, you still need to interpret vendor data. That means cleaning, normalizing, stitching fields together, and transforming your and your customers' data into entities your agents can actually use.

The Agent engine is an ideal solution when you:

- Don't want storage
- Care a lot about freshness and latency
- Are working with a small amount of data
- Need to trigger side effects, like sending an email or closing a ticket

The agentic data platform _isn't_ ideal when you:

- Need all your data in one place
- Need to join across datasets
- Need more pipelines that can be slower
- Want storage
- Want to update content, but not trigger side effects
- Rely on APIs that aren't good

If agentic data isn't what you're looking for and you need complex data aggregation for data analysis, [data replication](/platform) is likely the right solution.

### Taxonomy of data movement

<Taxonomy /> -->

## The problem with AI agents

AI agents have almost unlimited potential to scale productivity, accelerate insights, and democratize information. However, most organizations struggle to realize this promise.

- Large language models can reason, but rely on stale public training data that limits their effectiveness. They lack real-time knowledge, are stateless, and can't act on and verify facts.

- Improving context with real business data is difficult. It forces teams to build infrastructure they don't want to own: storage layers, indexing services, pipelines, and permissions models. All of this is maintenance debt just to acquire missing context.

- Even if high-quality data is available, agents still perform poorly. They lack real-time access, can't search, can't write, miss key information, and need human intervention.

Organizations trying to build agents face a problem:

- They need massive upfront investment, or

- Their agents don't perform well, or

- Both

The result is that agentic features never scale. They remain expensive, fragile prototypes that can't support real-world operations.

## How Airbyte solves that problem

Airbyte's Agent Engine solves this problem with three components.

- Open-source, type-safe connectors designed for AI agents. These connectors allow agents to retrieve information they don't have, perform computations or transformations, interact with external systems, and trigger side-effects, like sending emails, updating databases, and starting workflows

- Storage and management of end-user credentials.

- Out of the box entity caching to power low-latency search operations.

It's helpful to think of the Agent Engine as a data layer that makes agentic tool use easy. Tools are external capabilities AI agents can invoke. They allow agents to perceive, decide, and act beyond their training data. They're one of the most critical bridges between agents that aren't effective and agents with broad capabilities.

## Who Agent Engine is for

- AI companies building agentic solutions, especially multi-tenant SaaS services.

- Engineering teams building agents for internal use cases.

- Hackers, explorers, innovators, and anyone who needs to empower an agent in minutes.

- People tired of expensive agents that aren't helpful.

## Tools and MCP servers

It's helpful to think of agent connectors as equivalent to sets of tools. Tools are external capabilities AI agents can invoke. They allow agents to perceive, decide, and act beyond their training data. Tools are one of the most critical bridges between agents that aren't effective and agents with broad capabilities.

<!-- ## Requirements -->
