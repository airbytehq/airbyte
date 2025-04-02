---
products: oss-enterprise
---

# Set up multiple regions

Self-Managed Enterprise customers can use Airbyte's public API to define regions and create self-registering data planes that operate in those regions. This ensures you're satisfying your data residency and governance requirements with a single Airbyte deployment.

## How it works

By default, Airbyte has a single data plane that any workspace in the organization can access, and it's automatically tied to the default workspace you see when Airbyte first starts.

To configure additional data planes and associate them to specific workspaces, you complete the steps below.

1. Create a region.
2. Create a data plane in that region. The data plane automatically registers with the control plane.
3. Associate your data plane to your Airbyte workspace. You can tie each workspace to exactly one data plane.

Once you associate a workspace with a data plane, data in that workspace traverses your data plane in the region you've defined.

### What isn't stored in the data plane

- Logs
<!-- - Connector Builder? -->

## Prerequisites

Before you begin, make sure you've completed the following.

1. Deploy your Self-Managed Enterprise version of Airbyte as described in the [implementation guide](implementation-guide).

    :::note
    If you're using multiple data planes, you must have configured an external secrets manager as part of your deployment.
    :::

2. You must be an Organization Administrator to manage regions, data planes, and workspaces.

<!-- What else? Secrets? -->

## 1. Create a region

<!-- I'm a bit unclear how we associate the region with an actual region, this is self-hosted -->

```bash
curl --request POST \
  --url https://local.airbyte.dev/api/public/v1/regions \
  --header 'authorization: Bearer $TOKEN' \
  --header 'content-type: application/json' \
  --data '{
  "name": "aws-us-east-1",
  "organizationId": "00000000-0000-0000-0000-000000000000",
  "enabled": true
}'
```

## 2. Create a data plane

```bash
curl --request POST \
  --url https://local.airbyte.dev/api/public/v1/regions/116a49ab-b04a-49d6-8f9e-4d9d6a4189cc/dataplanes \
  --header 'authorization: Bearer $TOKEN' \
  --header 'content-type: application/json' \
  --data '{
  "name": "aws-us-west-3-dp-8",
  "enabled": true
}'
```

## 3. Associate a region to a workspace

<!-- values.yaml? -->

## Manage your data planes

### Check which region your workspaces are in

You can see a list of your workspaces and the region associated to each from Airbyte's organization settings.

1. In Airbyte's user interface, click **Settings**.

2. Click **General**.

Airbyte displayed your workspaces and their associated region under **Regions**.

<!-- Is there an API method? -->

### List all regions

List all regions in your organization.

```bash
curl --request GET \
  --url 'https://local.airbyte.dev/api/public/v1/regions?organizationId=00000000-0000-0000-0000-000000000000' \
  --header 'authorization: Bearer $TOKEN' \
  --header 'content-type: application/json'
```

### Get a region

Get information about a region.

```bash
curl --request GET \
  --url https://local.airbyte.dev/api/public/v1/regions/96129828-e006-4fd6-820f-132dc00a10f2 \
  --header 'authorization: Bearer $TOKEN' \
  --header 'content-type: application/json'
```

### Update a region

Update, enable, or turn off a region.

```bash
curl --request PATCH \
  --url https://local.airbyte.dev/api/public/v1/regions/96129828-e006-4fd6-820f-132dc00a10f2 \
  --header 'authorization: Bearer $TOKEN' \
  --header 'content-type: application/json' \
  --data '{
  "enabled": false
}'
```

### Delete a region

Delete a region.

```bash
curl --request DELETE \
  --url https://local.airbyte.dev/api/public/v1/regions/8fee0404-6d56-442a-bb54-e28edada1405 \
  --header 'authorization: Bearer $TOKEN' \
  --header 'content-type: application/json'
```

### List data planes

List all data planes in your organization.

```bash
curl --request GET \
  --url https://local.airbyte.dev/api/public/v1/regions/116a49ab-b04a-49d6-8f9e-4d9d6a4189cc/dataplanes \
  --header 'authorization: Bearer $TOKEN'
```

### Get a data plane

Get information about a data plane.

```bash
curl --request GET \
  --url https://local.airbyte.dev/api/public/v1/regions/116a49ab-b04a-49d6-8f9e-4d9d6a4189cc/dataplanes/312b4641-2edc-4dc9-9933-41b759d3b2d8 \
  --header 'authorization: Bearer $TOKEN'
```

### Delete a data plane

Delete a data plane from a region.

```bash
curl --request DELETE \
  --url https://local.airbyte.dev/api/public/v1/regions/116a49ab-b04a-49d6-8f9e-4d9d6a4189cc/dataplanes/f1482a93-4786-4662-800e-ff07363418b1 \
  --header 'authorization: Bearer $TOKEN'
```
