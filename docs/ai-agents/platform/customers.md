---
sidebar_position: 4
---

# Manage customers

In Agent Engine, a "customer" represents an end-user of your application who connects their own data sources. Each customer gets an isolated workspace where their credentials, connectors, and data are stored separately from other customers.

## What is a customer?

A customer is your end-user who authenticates with their own credentials to access their data through your application. In Agent Engine's architecture, each customer maps to a **workspace**. These terms are essentially interchangeable: when you see "workspace" in the API, think "customer."

The `workspace_name` you provide when creating tokens serves as the unique customer identifier within your organization. You can use any string that makes sense for your application, such as your internal customer ID, email, or account name.

## Why customers exist

Agent Engine uses the customer concept to provide data isolation in multi-tenant applications.

Each customer's data, credentials, and configurations are isolated within their workspace. A scoped token can only access a single customer's workspace, following the principle of least privilege. Customer data never crosses workspace boundaries, which simplifies compliance and security.

This architecture means you can safely serve multiple end-users from a single Agent Engine organization without worrying about data leakage between customers.

## Customers and authentication

Agent Engine uses a hierarchical token system where each token type has a different scope. For complete details on token types and authentication flows, see [Agent Engine authentication](authenticate/hosted.md).

The key relationship between tokens and customers:

- **Operator Bearer Token**: Organization-wide access. Use this to create and manage customers.
- **Scoped Token**: Bound to a single customer's workspace. Created by providing a `workspace_name` that identifies the customer.
- **Widget Token**: Same as a scoped token but with CORS protection for embedding in your frontend.

When you generate a scoped token with a `workspace_name`, you're either accessing an existing customer or creating a new one if that workspace doesn't exist yet.

## Create a new customer

Creating a new customer is as simple as generating a scoped token with a new `workspace_name`. If the workspace doesn't exist, Airbyte creates it automatically.

```bash
curl -X POST https://api.airbyte.ai/api/v1/embedded/scoped-token \
  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_name": "customer_acme_corp"
  }'
```

The response contains a scoped token you can use for all operations on behalf of this customer:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

For details on obtaining an operator token and the full authentication flow, see [Agent Engine authentication](authenticate/hosted.md).

## Customer management API

Use these endpoints to manage customers programmatically. All workspace management endpoints require an Operator Bearer Token.

### List customers

Retrieve all customers (workspaces) in your organization:

```bash
curl https://api.airbyte.ai/api/v1/workspaces \
  -H 'Authorization: Bearer <your_operator_token>'
```

You can filter by name or status:

```bash
curl 'https://api.airbyte.ai/api/v1/workspaces?name_contains=acme&status=active' \
  -H 'Authorization: Bearer <your_operator_token>'
```

### Get customer details

Retrieve details for a specific customer:

```bash
curl https://api.airbyte.ai/api/v1/workspaces/<workspace_id> \
  -H 'Authorization: Bearer <your_operator_token>'
```

### Update a customer

Update a customer's name or status:

```bash
curl -X PUT https://api.airbyte.ai/api/v1/workspaces/<workspace_id> \
  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Acme Corp - Enterprise",
    "status": "active"
  }'
```

Setting status to `inactive` automatically disables all connections in that workspace.

### Delete a customer

Delete a customer and all associated resources:

```bash
curl -X DELETE https://api.airbyte.ai/api/v1/workspaces/<workspace_id> \
  -H 'Authorization: Bearer <your_operator_token>'
```

### Get customer info from a scoped token

If you have a scoped token and need to retrieve the associated customer information:

```bash
curl https://api.airbyte.ai/api/v1/embedded/scoped-token/info \
  -H 'Authorization: Bearer <scoped_token>'
```

## Best practices

Use meaningful, consistent naming for `workspace_name`. Your internal customer ID or account identifier works well, as it makes it easy to correlate Agent Engine workspaces with your own customer records.

Handle token expiration appropriately. Scoped tokens expire after 20 minutes. Generate new tokens as needed rather than caching them for extended periods.

Use the workspace status to manage customer lifecycle. Setting a workspace to `inactive` is a clean way to suspend a customer's access without deleting their data.
