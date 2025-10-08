---
products: embedded
---

# Airbyte API

The Airbyte API allows you to build a fully integrated Airbyte Embedded Experience.

## Quick Start

New to Airbyte Embedded? Start here:

1. **[Authentication](./authentication.md)** - Understand token types and how to authenticate
2. **[Create Connection Templates](./connection-templates.md)** - Set up where your users' data will be stored
3. **[Create Source Templates](./source-templates.md)** - Choose which data connectors your users can access
4. **[Configure Sources](./configuring-sources.md)** - Help your users connect their data sources
5. **[Manage Workspaces](./workspaces.md)** - Organize and manage user environments

## API Overview

The Airbyte Embedded API is organized into three main categories:

### 1. Embedded API (`/api/v1/embedded`)
End-user-facing endpoints for credential collection and source configuration.

**Key Capabilities:**
- Generate tokens for end users (scoped and widget tokens)
- List available source templates
- Create, update, and delete end-user sources
- Check source configuration validity

**Authentication:** Requires [Scoped Token](./authentication.md#scoped-token) or [Access Token](./authentication.md#access-token-operator-token)

**Documentation:**
- [Authentication Guide](./authentication.md)
- [Configuring Sources](./configuring-sources.md)

### 2. Integration Management API (`/api/v1/integrations`)
Operator-facing endpoints for managing configurations and templates.

**Key Capabilities:**
- Create and manage source templates
- Create and manage connection templates
- Organize templates with tags
- Configure destinations
- Manage end-user sources (operator view)

**Authentication:** Requires [Access Token](./authentication.md#access-token-operator-token)

**Documentation:**
- [Source Templates](./source-templates.md)
- [Connection Templates](./connection-templates.md)
- [Template Tags](../widget/template-tags.md)

### 3. Workspace Management API (`/api/v1/workspaces`)
Operator-facing endpoints for workspace lifecycle management.

**Key Capabilities:**
- List and search workspaces
- Update workspace status (active/inactive)
- Get workspace statistics
- Sync workspaces from Airbyte Cloud

**Authentication:** Requires [Access Token](./authentication.md#access-token-operator-token)

**Documentation:**
- [Managing Workspaces](./workspaces.md)

## Implementation Patterns

### Pattern 1: Widget Integration (Recommended for Quick Start)

The fastest way to integrate Airbyte Embedded. End users configure sources through the Airbyte UI embedded in your application.

**Steps:**
1. [Set up authentication](./authentication.md) and get your access token
2. [Create connection templates](./connection-templates.md) to define data destinations
3. [Create source templates](./source-templates.md) to choose available data connectors
4. [Generate widget tokens](./authentication.md#widget-token) for each end user
5. [Embed the widget](../widget/README.md) in your application

**Best for:** Rapid integration, standard UI/UX, minimal frontend development

### Pattern 2: API Integration (Full Control)

Build your own source configuration UI with complete control over the user experience.

**Steps:**
1. [Set up authentication](./authentication.md) and get your access token
2. [Create connection templates](./connection-templates.md) to define data destinations
3. [Create source templates](./source-templates.md) to choose available data connectors
4. [Generate scoped tokens](./authentication.md#scoped-token) for each end user
5. [Build your UI](./configuring-sources.md) to configure sources via API

**Best for:** Custom branding, advanced workflows, specific UX requirements

### Pattern 3: Hybrid Approach

Combine widget and API integration for flexibility.

**Example:** Use the widget for initial source setup, then use the API for advanced management features.

## Implementation Steps

### 1. One-Time Setup (Your Organization)

Configure the foundation for your embedded integration:

1. **[Authenticate](./authentication.md)**: Obtain your access token from Airbyte Cloud
2. **[Create Connection Templates](./connection-templates.md)**: Define where your users' data will be stored (destination configuration)
3. **[Create Source Templates](./source-templates.md)**: Choose which data connectors your users can access
4. **[Organize with Tags](../widget/template-tags.md)** (Optional): Use tags to group and filter templates

### 2. Per-User Integration (Runtime)

For each user who wants to connect their data:

5. **[Generate User Tokens](./authentication.md)**: Create scoped or widget tokens for your end users
6. **[Configure Sources](./configuring-sources.md)**: Help users connect their data sources
   - Via widget: Embed the Airbyte widget in your app
   - Via API: Build your own source configuration UI

### 3. Ongoing Management (Operations)

As your integration scales:

7. **[Manage Workspaces](./workspaces.md)**: Monitor, search, and manage end-user workspaces
8. **[Update Templates](./source-templates.md)**: Add new connectors or modify existing configurations
9. **Monitor Usage**: Track workspace statistics and source configurations

## API Endpoints by Use Case

### For Your Backend (Access Token Required)

| Use Case | Endpoint | Method | Documentation |
|----------|----------|--------|---------------|
| Generate widget token | `/api/v1/embedded/widget-token` | POST | [Authentication](./authentication.md#widget-token) |
| Generate scoped token | `/api/v1/embedded/scoped-token` | POST | [Authentication](./authentication.md#scoped-token) |
| Create source template | `/api/v1/integrations/templates/sources` | POST | [Source Templates](./source-templates.md) |
| Create connection template | `/api/v1/integrations/templates/connections` | POST | [Connection Templates](./connection-templates.md) |
| List workspaces | `/api/v1/workspaces` | GET | [Workspaces](./workspaces.md) |
| Update workspace status | `/api/v1/workspaces/{id}` | PUT | [Workspaces](./workspaces.md) |

### For End Users (Scoped Token Required)

| Use Case | Endpoint | Method | Documentation |
|----------|----------|--------|---------------|
| List available source templates | `/api/v1/embedded/source-templates` | GET | [Configuring Sources](./configuring-sources.md) |
| Create a source | `/api/v1/embedded/sources` | POST | [Configuring Sources](./configuring-sources.md) |
| List configured sources | `/api/v1/embedded/sources` | GET | [Configuring Sources](./configuring-sources.md) |
| Update a source | `/api/v1/embedded/sources/{id}` | PUT | [Configuring Sources](./configuring-sources.md) |
| Delete a source | `/api/v1/embedded/sources/{id}` | DELETE | [Configuring Sources](./configuring-sources.md) |
| Check source validity | `/api/v1/embedded/sources/check` | POST | [Configuring Sources](./configuring-sources.md) |

## Additional Resources

### Documentation
- **[Complete API Reference](https://api.airbyte.ai/api/v1/docs)** - Interactive OpenAPI documentation
- **[Widget Integration Guide](../widget/README.md)** - Embed the Airbyte widget
- **[Authentication Guide](./authentication.md)** - Detailed token usage and security
- **[Workspace Management](./workspaces.md)** - Manage end-user environments

### Support
- **Email:** sonar@airbyte.io
- **Slack:** [Airbyte Community](https://airbyte.com/community)
- **GitHub:** [airbytehq/airbyte](https://github.com/airbytehq/airbyte)

### Getting Access
Airbyte Embedded requires organization activation. Contact:
- **michel@airbyte.io**
- **teo@airbyte.io**

## API Versioning

The Airbyte API follows semantic versioning. The current API version is included in the base URL:

```
https://api.airbyte.ai/api/v1/...
```

### Breaking Changes
We will announce breaking changes with at least 90 days notice. Deprecated endpoints will continue to work during the deprecation period.

### Changelog
View the [API Changelog](https://api.airbyte.ai/api/v1/changelog) for recent updates and changes.

## Rate Limiting

The Airbyte API implements rate limiting to ensure fair usage:

- **Standard Tier:** 1000 requests per hour per organization
- **Enterprise Tier:** Custom limits available

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 952
X-RateLimit-Reset: 1696348800
```

If you exceed rate limits, you'll receive a `429 Too Many Requests` response.

## Best Practices

### Security
- Store access tokens securely (environment variables, secret managers)
- Never expose access tokens to client-side code
- Use scoped tokens for end-user operations
- Implement token refresh logic for expired tokens
- Use HTTPS for all API requests

### Performance
- Implement caching for template lists
- Use pagination for large datasets
- Consider webhooks for real-time updates (coming soon)
- Batch operations when possible

### Error Handling
- Always check response status codes
- Implement retry logic with exponential backoff
- Log errors for debugging
- Provide user-friendly error messages

### Workspace Management
- Use consistent naming conventions for workspaces
- Set workspaces to inactive for churned customers
- Regularly sync workspaces for consistency
- Monitor workspace statistics

## Next Steps

1. **Get Started:** Review the [Authentication Guide](./authentication.md) to understand token types
2. **Set Up Templates:** Follow [Source Templates](./source-templates.md) and [Connection Templates](./connection-templates.md) guides
3. **Choose Integration:** Decide between [Widget](../widget/README.md) or [API](./configuring-sources.md) integration
4. **Test:** Use the [interactive API docs](https://api.airbyte.ai/api/v1/docs) to test endpoints
5. **Deploy:** Integrate into your application and go live
