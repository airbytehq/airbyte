---
products: embedded
---

# Airbyte API

The Airbyte API allows you to build a fully integrated Airbyte Embedded Experience.

## Quick Start

Follow these steps to implement Airbyte Embedded with the API:

### 1. One-Time Setup (Your Organization)
First, configure the foundation for your embedded integration:

1. **[Create Connection Templates](./connection-templates.md)**: Define where your users' data will be stored (destination configuration)
2. **[Create Source Templates](./source-templates.md)**: Choose which data connectors your users can access

### 2. Per-User Integration (Runtime)
For each user who wants to connect their data:

3. **[Generate User Tokens & Configure Sources](./configuring-sources.md)**: Authenticate users and collect their source credentials

This approach separates one-time organizational setup from per-user operations, making your integration more scalable.

## Core Concepts

### [Authentication](./authentication.md)
Understand the different token types and how to securely authenticate your API calls:
- **Access Tokens**: Organization-level administrative access
- **Scoped Tokens**: User-level limited access for individual workspaces
- **Widget Tokens**: Specialized tokens for the Embedded Widget
- Security best practices and implementation examples

### [Workspace Management](./workspace-management.md)
Learn how Airbyte Embedded creates isolated environments for each customer:
- Multi-tenant architecture and data isolation
- Automatic workspace creation
- External ID best practices
- Template tag filtering for workspace-specific configurations

### [Schema Discovery](./schema-discovery.md)
Programmatically explore your customers' data structures:
- Discover available streams (tables/collections)
- Query field schemas and data types
- Understand primary keys and relationships
- Build dynamic UIs based on available data

## API Guides

### Setup & Configuration
- [Connection Templates](./connection-templates.md) - Configure destinations for your users
- [Source Templates](./source-templates.md) - Define available data connectors
- [Configuring Sources](./configuring-sources.md) - Collect user credentials and create sources

### Advanced Topics
- [Schema Discovery](./schema-discovery.md) - Explore data structures programmatically
- [Workspace Management](./workspace-management.md) - Manage customer isolation
- [Authentication](./authentication.md) - Secure token management

## API Reference

The complete API reference with all endpoints, request/response schemas, and interactive testing is available at [api.airbyte.ai/api/v1/docs](https://api.airbyte.ai/api/v1/docs).

## Need Help?

- **Documentation**: Browse the guides above for detailed implementation instructions
- **API Reference**: [api.airbyte.ai/api/v1/docs](https://api.airbyte.ai/api/v1/docs)
- **Support**: Contact [sonar@airbyte.io](mailto:sonar@airbyte.io) for assistance
- **Sample App**: See a complete implementation in our [embedded demo app](https://github.com/airbytehq/embedded-demoapp)
