# Connector Development Guide

Welcome to Airbyte's Connector Development Guide! This documentation will help you choose the right approach for building your connector and guide you through the development process.

:::warning Important Note About Java Development
🔄 Airbyte is undergoing a major revamp of the Java destinations codebase, with plans to release a new Java/Kotlin CDK in 2025. Currently:
* We are not accepting new Java connector contributions
* Existing Java connector maintenance continues
* For new database connectors, please use the Python CDK
:::

## Quick Start Guide

### 1. Choose Your Development Path

| If you need to... | Use this approach |
|------------------|-------------------|
| Build an HTTP/REST API connector | [Connector Builder](./connector-builder-ui/overview.md) (Recommended) |
| Create a complex HTTP API integration | [Low-code CDK](./config-based/low-code-cdk-overview.md) |
| Develop a database connector | [Python CDK](./cdk-python/basic-concepts.md) |
| Maintain existing Java/Kotlin connector | [Java CDK](./tutorials/building-a-java-destination.md) |

### 2. Essential Prerequisites
Before starting, review:
* [Airbyte Protocol Specification](../understanding-airbyte/airbyte-protocol.md)
* [Best Practices Guide](./best-practices.md)
* [Compatibility Guide](./connector-builder-ui/connector-builder-compatibility.md)

Need help? Join our [Connector Development Slack channel](https://airbytehq.slack.com/archives/C027KKE4BCZ)

## Development Process

1. **Build & Test**
   * Choose your development approach from above
   * Follow the corresponding documentation
   * Use our [testing framework](./testing-connectors/README.md)

2. **Deploy & Verify**
   * Test as a custom connector in your workspace
   * Verify with real data flows

3. **Contribute (Optional)**
   * Ready to share? Follow our [contribution guide](../contributing-to-airbyte/submit-new-connector.md)
   * Submit to the Airbyte Cloud/OSS catalog

## Development Options in Detail

### Connector Builder (No-Code Solution)
✨ **Recommended for HTTP/REST APIs**
* Perfect for REST APIs with JSON/JSONL responses
* Supports REST, GraphQL with Basic Auth, API Key, OAuth 2.0
* No local development environment needed
* [Start with our Tutorial](./connector-builder-ui/tutorial.mdx)

### Low-code CDK
🔧 **For Complex HTTP APIs**
* APIs requiring custom authentication or complex request patterns
* YAML-based configuration
* Optional [custom Python components](./config-based/advanced-topics.md#custom-components)
* [View Documentation](./config-based/low-code-cdk-overview.md)

### Python CDK
💻 **For Database & Non-HTTP Sources**
* Maximum flexibility for complex integrations
* Full programmatic control
* Recommended for all database connectors
* [Read the Guide](./tutorials/custom-python-connector/0-getting-started.md)

### Java CDK (Limited Support)
⚠️ **For Existing Connectors Only**
* Currently maintaining existing connectors only
* New Java CDK planned for 2025
* Not accepting new Java/Kotlin connectors
* [Maintenance Guide](./tutorials/building-a-java-destination.md)

### Community maintained CDKs

- The [Typescript CDK](https://github.com/faros-ai/airbyte-connectors) is actively maintained by
  Faros.ai for use in their product.
- The [Airbyte Dotnet CDK](https://github.com/mrhamburg/airbyte.cdk.dotnet) in C#.
