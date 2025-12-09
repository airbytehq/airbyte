import DocCardList from '@theme/DocCardList';

# Direct connectors

Airbyte's direct connectors are Python packages that equip AI agents to call third-party APIs through strongly typed, well-documented tools. Each connector is ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

## How direct connectors are different from data replication connectors

<!-- 

- Not source-destination relationship
- Separate connectors, AI optimized
- Intended for operational AI use cases, not data replication

 -->

### Connector structure

Each connector is a standalone Python package.

```text
connectors/
├── stripe/
│   ├── airbyte_ai_stripe/
│   ├── pyproject.toml
│   ├── CHANGELOG.md
│   └── README.md
├── github/
│   └── ...
└── ...
```

Inside each connector folder, you can find the following.

- The generated Python client
- A connector-specific README with supported operations
- Typed methods generated from Airbyte's connector definitions
- Validation + error handling

## When to use these connectors

Use Airbyte AI Connectors when you want:

- **Agent‑friendly data access**: Let LLM agents call real SaaS APIs. For example, CRM, billing, analytics) with guardrails and typed responses.

- **Consistent auth and schemas**: Reuse a uniform configuration and error‑handling pattern across many APIs. Use connectors inside frameworks like PydanticAI, LangChain, or any custom agent loop.

- **Composable building blocks**: Combine multiple connectors in a single agent to orchestrate multi‑system workflows. Compared to building ad‑hoc API wrappers, these connectors give you a shared structure, generated clients, and alignment with the rest of the Airbyte ecosystem.

## How to work with direct connectors

Two options exist to work with a direct connector: Model Context Protocol (MCP) and Python SDK.

<DocCardList />
