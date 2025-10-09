---
products: embedded
---

# Workspace Management

Airbyte Embedded creates isolated workspaces for each of your customers, providing secure multi-tenant data pipelines. This guide explains how workspaces work and how to manage them effectively.

## What is a Workspace?

A workspace is an isolated environment within Airbyte Embedded where a single customer's:
- Data sources are configured
- Data destinations are defined
- Data pipelines execute
- Connection settings are stored

Each workspace is completely isolated from others through Row Level Security (RLS) in the database, ensuring that customer data never crosses boundaries.

## Workspace Architecture

### Multi-Tenant Isolation

Airbyte Embedded uses a multi-tenant architecture where:

1. **Your Organization**: The top-level entity that represents your company
2. **Customer Workspaces**: Individual workspaces created for each of your end-users
3. **Row Level Security**: Database-level security that enforces data isolation

```
Your Organization
├── Customer Workspace A (email: customer-a@example.com)
│   ├── Source: Stripe
│   ├── Destination: Your S3 Bucket
│   └── Connection: Stripe → S3
├── Customer Workspace B (email: customer-b@example.com)
│   ├── Source: Salesforce
│   ├── Destination: Your S3 Bucket
│   └── Connection: Salesforce → S3
└── Customer Workspace C (email: customer-c@example.com)
    ├── Source: PostgreSQL
    ├── Destination: Your S3 Bucket
    └── Connection: PostgreSQL → S3
```

## Creating Workspaces

Workspaces are automatically created when you generate a scoped token for a new customer. You don't need to explicitly create workspaces - they're created on-demand.

### Automatic Workspace Creation

When you call the scoped token endpoint with a new `external_id`:

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/embedded/scoped-token' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "external_id": "customer-unique-id-123",
    "selected_source_template_tags": ["production"],
    "selected_connection_template_tags": ["production"]
  }'
```

This will:
1. Create a new workspace if one doesn't exist for `external_id: customer-unique-id-123`
2. Return a scoped token that only has access to that workspace
3. Associate the specified template tags with that workspace

### External IDs

The `external_id` is your customer's unique identifier in your system. Choose an identifier that:

- Is unique per customer
- Is stable (doesn't change)
- Is not personally identifiable (for security)

**Good examples:**
- UUID: `"550e8400-e29b-41d4-a716-446655440000"`
- Internal customer ID: `"cust_abc123xyz"`
- Hashed identifier: `"hash_of_customer_email"`

**Bad examples:**
- Email addresses (not stable if customer changes email)
- Names (not unique, can change)
- Temporary session IDs (not stable)

## Managing Workspace Access

### Scoped Tokens

Scoped tokens provide temporary, restricted access to a specific workspace. This follows the principle of least privilege.

**Token Characteristics:**
- Expires after a configurable time period
- Only grants access to one workspace
- Can only perform specific operations (create/update sources, connections)
- Cannot access other workspaces or organization settings

### Organization-Level Access

Your organization's access token has full access to:
- All workspaces in your organization
- Template management
- Organization settings

**Security Note:** Never expose your organization access token to end-users. Always generate scoped tokens for customer interactions.

## Viewing Workspaces

As the organization owner, you can view all customer workspaces in your Airbyte Cloud dashboard:

1. Log in to [cloud.airbyte.com](https://cloud.airbyte.com)
2. Navigate to the workspace selector
3. See all workspaces created via Embedded

Each workspace will show:
- The external ID you assigned
- All sources configured by that customer
- All connections and their sync status
- Data pipeline performance metrics

![Customer workspaces view](./assets/embedded-workspaces.png)

## Template Tags and Workspace Filtering

Template tags allow you to control which sources and destinations are available in specific workspaces.

### Use Cases

**Environment-Based Filtering:**
```json
{
  "external_id": "prod-customer-123",
  "selected_source_template_tags": ["production"],
  "selected_connection_template_tags": ["production"]
}
```

**Tier-Based Access:**
```json
{
  "external_id": "premium-customer-456",
  "selected_source_template_tags": ["premium", "enterprise"],
  "selected_connection_template_tags": ["premium"]
}
```

**Customer-Specific Configuration:**
```json
{
  "external_id": "customer-789",
  "selected_source_template_tags": ["customer-789-specific"],
  "selected_connection_template_tags": ["default"]
}
```

Learn more in the [Template Tags guide](../widget/template-tags.md).

## Best Practices

### Security

1. **Never reuse external IDs** across different customers
2. **Use scoped tokens** for all customer-facing operations
3. **Rotate access tokens** regularly
4. **Monitor workspace access** through audit logs

### Scalability

1. **Use UUIDs as external IDs** for best scalability
2. **Implement token caching** to reduce API calls
3. **Handle token expiration** gracefully with refresh logic
4. **Monitor workspace creation rate** to detect unusual activity

### Organization

1. **Use template tags** to organize workspace permissions
2. **Document your external ID scheme** for your team
3. **Implement workspace cleanup** for deleted customers
4. **Monitor workspace health** through Airbyte's dashboard

## Troubleshooting

### Workspace Not Found

If you get a "workspace not found" error:

1. Verify the external ID matches exactly (case-sensitive)
2. Ensure the scoped token hasn't expired
3. Check that the workspace was created successfully
4. Verify you're using the correct organization

### Permission Denied

If operations fail with permission errors:

1. Verify you're using a scoped token (not org token) for customer operations
2. Check that the scoped token hasn't expired
3. Ensure the token was generated for the correct external ID
4. Verify template tags are configured correctly

### Multiple Workspaces for Same Customer

If you accidentally create multiple workspaces:

1. Ensure your external ID generation is consistent
2. Check for race conditions in workspace creation
3. Implement idempotency in your token generation
4. Contact support to merge or clean up workspaces

## API Reference

For complete API documentation, see:
- [Scoped Token Generation](./configuring-sources.md#generating-scoped-tokens)
- [Source Templates](./source-templates.md)
- [Connection Templates](./connection-templates.md)
- [Full API Reference](https://api.airbyte.ai/api/v1/docs)

## Next Steps

- Learn about [Source Templates](./source-templates.md)
- Understand [Connection Templates](./connection-templates.md)
- Implement [Source Configuration](./configuring-sources.md)
- Explore the [Embedded Widget](../widget/README.md)
