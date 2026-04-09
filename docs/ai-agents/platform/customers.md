---
sidebar_position: 4
---

# Manage customers

In Agent Engine, a **customer** represents an end-user of your service who connects their own data sources. Each customer gets an isolated environment that stores their credentials, connectors, and data separately from other customers. You may occasionally see the terms `workspace` or `external_customer` in the Agent Engine API. These terms are essentially interchangeable. All of them map to a customer.

The `customer_name` you provide when creating scoped tokens serves as the unique customer identifier within your organization. Use any string that makes sense for your service, like an internal customer ID or company name.

## Why customers exist

Agent Engine uses the customer concept to provide data isolation in multi-tenant applications.

Airbyte isolates each customer's data, credentials, and configurations in their customer. A [scoped token](/ai-agents/api/#scoped-token) can only access that single customer. Customer data never crosses the customer boundary. This architecture means you can safely serve multiple end-users from a single Agent Engine organization without worrying about data leakage between customers.

## Customers and authentication

Agent Engine uses a hierarchical token system where each token type has a different scope. For complete details on token types and how to generate them, see [Token types](/ai-agents/api/#token-types) in the API documentation.

## Create a new customer

You create a new customer when you generate a scoped token with a new `customer_name`. If the customer doesn't exist, Airbyte creates it automatically.

```bash title="Request"
curl -X POST https://api.airbyte.ai/api/v1/account/applications/scoped-token \
  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_name": "customer_acme_corp"
  }'
```

The response contains a scoped token you can use for all operations on behalf of this customer:

```json title="Response"
{
  "token": "eyJhbGci..."
}
```

## Manage customers

Use these endpoints to manage customers programmatically. All customer management endpoints require an application token.

### List customers

Retrieve all customers in your organization.

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
curl https://api.airbyte.ai/api/v1/account/applications/scoped-token/info \
  -H 'Authorization: Bearer <scoped_token>'
```

### Update a customer

Update a customer's name or status.

```bash
curl -X PUT https://api.airbyte.ai/api/v1/workspaces/<workspace_id> \
  -H 'Authorization: Bearer <your_operator_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Acme Corp - Enterprise",
    "status": "active"
  }'
```

Setting status to `inactive` automatically disables all connections in that customer.

### Delete a customer

Delete a customer and all associated resources:

```bash
curl -X DELETE https://api.airbyte.ai/api/v1/workspaces/<workspace_id> \
  -H 'Authorization: Bearer <your_operator_token>'
```

## Best practices

- Use meaningful, consistent naming for `customer_name`. Your internal customer ID or company name works well, and makes it easy to correlate Agent Engine customers with your own customer records.

- Handle token expiration appropriately. Application tokens expire after 15 minutes and scoped tokens expire after 20 minutes.

- Use the customer status to manage customer lifecycle. Setting a customer to `inactive` is a clean way to suspend a customer's access without deleting their data.
