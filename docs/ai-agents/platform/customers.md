---
sidebar_position: 4
---

# Manage customers

In Agent Engine, a "customer" represents an end-user of your service who connects their own data sources. Each customer gets an isolated workspace that stores their credentials, connectors, and data separately from other customers.

In Agent Engine's architecture, each customer maps to a **workspace**. These terms are essentially interchangeable: when you see "workspace," think "customer."

The `workspace_name` you provide when creating tokens serves as the unique customer identifier within your organization. Use any string that makes sense for your service, like an internal customer ID or customer name.

## Why customers exist

Agent Engine uses the customer concept to provide data isolation in multi-tenant applications.

Airbyte isolates each customer's data, credentials, and configurations in their workspace. A [scoped token](../platform/authenticate/hosted) can only access a single customer's workspace, following the principle of least privilege. Customer data never crosses workspace boundaries, which simplifies compliance and security.

This architecture means you can safely serve multiple end-users from a single Agent Engine organization without worrying about data leakage between customers.

## Customers and authentication

Agent Engine uses a hierarchical token system where each token type has a different scope. For complete details on token types and authentication flows, see [Agent Engine authentication](authenticate/hosted.md)

## Create a new customer

You create a new customer when you generate a scoped token with a new `workspace_name`. If the workspace doesn't exist, Airbyte creates it automatically.

```bash title="Request"
curl -X POST https://api.airbyte.ai/api/v1/embedded/scoped-token \
  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "workspace_name": "customer_acme_corp"
  }'
```

The response contains a scoped token you can use for all operations on behalf of this customer:

```json title="Response"
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Manage customers

Use these endpoints to manage customers programmatically. All workspace management endpoints require an Operator Bearer Token.

### List customers

Retrieve all customers (workspaces) in your organization.

```bash
curl https://api.airbyte.ai/api/v1/workspaces \
  -H 'Authorization: Bearer <your_operator_token>'
```

You can filter customers by name and status.

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

### Get customer info from a scoped token

If you have a scoped token and need to retrieve the associated customer information:

```bash
curl https://api.airbyte.ai/api/v1/embedded/scoped-token/info \
  -H 'Authorization: Bearer <scoped_token>'
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

## Best practices

- Use meaningful, consistent naming for `workspace_name`. Your internal customer ID or customer name works well, and makes it easy to correlate Agent Engine workspaces with your own customer records.

- Handle token expiration appropriately. Operator Bearer Tokens expire after 15 minutes and scoped tokens expire after 20 minutes.

- Use the workspace status to manage customer lifecycle. Setting a workspace to `inactive` is a clean way to suspend a customer's access without deleting their data.
