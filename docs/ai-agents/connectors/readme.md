import DocCardList from '@theme/DocCardList';

# Agent connectors

Airbyte's agent connectors are Python packages that equip AI agents to call third-party APIs through strongly typed, well-documented tools. Each connector is ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

## How agent connectors differ from data replication connectors

Traditional Airbyte connectors are for data replication. They move large volumes of data from a source into a destination such as a warehouse or data lake on a schedule. Agent connectors are lightweight, type-safe Python clients that let AI agents call third-party APIs directly in real time.

The key differences are:

- **Topology**: Data replication connectors are always used in a source-to-destination pairing managed by the Airbyte platform. Agent connectors are standalone library packages that you import into your app or agent and call directly, with no source/destination pairing or sync pipeline.

- **Use cases**: Data replication connectors are for batch ELT/ETL and analytics, building a full, historical dataset in a warehouse. Agent connectors are for operational AI use cases: answering a question, fetching a slice of fresh data, or performing an action in a SaaS tool while an agent is reasoning.

- **Execution model**: Data replication connectors run as jobs orchestrated by the Airbyte platform with schedules and state tracking. Agent connectors run inside your Python app or AI agent loop, returning results to that process immediately.

- **Data flow**: Data replication connectors write data into destinations and maintain state for incremental sync. Agent connectors stream typed responses back to the caller without creating a replicated copy of the data.

Agent connectors don't replace your existing source and destination connectors. They complement them by providing agentic, real-time access to the same systems. Unlike data replication connectors, you don't need to run the Airbyte platform to use Agent connectors—they are regular Python packages you add to your application or agent.

### Connector structure

Each connector is a standalone Python package in the [Airbyte Agent Connectors repository](https://github.com/airbytehq/airbyte-agent-connectors).

```text
connectors/
├── stripe/
│   ├── airbyte_agent_stripe/
│   ├── pyproject.toml
│   ├── CHANGELOG.md
│   └── README.md
│   └── REFERENCE.md
├── github/
│   └── ...
└── ...
```

Inside each connector folder, you can find the following.

- The Python client
- Connector-specific documentation with supported operations and authentication requirements
- Typed methods generated from Airbyte's connector definitions
- Validation + error handling

## When to use these connectors

Use Airbyte agent Connectors when you want:

- **Agent‑friendly data access**: Let LLM agents call real SaaS APIs, like a CRM, billing, or analytics, with guardrails and typed responses.

- **Consistent auth and schemas**: Reuse a uniform configuration and error‑handling pattern across many APIs. Use connectors inside frameworks like Pydantic AI, LangChain, or any custom agent loop.

- **Composable building blocks**: Combine multiple connectors in a single agent to orchestrate multi‑system workflows. Compared to building ad‑hoc API wrappers, these connectors give you a shared structure, generated clients, and alignment with the rest of the Airbyte ecosystem.

## How to work with agent connectors

Two options exist to work with an agent connector: Airbyte's MCP server and Python SDK.

- [Python SDK tutorial](../quickstarts/tutorial-python) (recommended)
- [MCP tutorial](../quickstarts/tutorial-mcp) (experimental)

## All agent connectors

<DocCardList />
