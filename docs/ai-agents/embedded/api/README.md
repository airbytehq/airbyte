---

products: embedded

---

# Agent Engine API

The Agent Engine API allows you to build a fully integrated Airbyte Embedded Experience.

## Implementation Steps

Follow these steps to implement Airbyte Embedded with the API:

### 1. One-Time Setup (Your Organization)

First, configure the foundation for your embedded integration:

1. **[Create Connection Templates](./connection-templates.md)**: Define where your users' data will be stored (destination configuration)
2. **[Create Source Templates](./source-templates.md)**: Choose which data connectors your users can access

### 2. Per-User Integration (Runtime)

For each user who wants to connect their data:

1. **[Generate User Tokens & Configure Sources](./configuring-sources.md)**: Authenticate users and collect their source credentials

This approach separates one-time organizational setup from per-user operations, making your integration more scalable.

[Full Agent Engine API reference](/ai-agents/embedded/api-reference/sonar).
