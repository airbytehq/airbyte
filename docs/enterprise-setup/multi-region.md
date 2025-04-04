---
products: oss-enterprise
---

# Implement multiple regions

Self-Managed Enterprise customers can use Airbyte's public API to define regions and create self-registering data planes that operate in those regions. This ensures you're satisfying your data residency and governance requirements with a single Airbyte deployment.

## How it works

By default, Airbyte has a single data plane that any workspace in the organization can access, and it's automatically tied to the default workspace when Airbyte first starts.

To configure additional data planes and associate them to specific workspaces, you complete the steps below.

1. [Create a region](#step-1).
2. [Create a data plane](#step-2) in that region.
3. [Associate your data plane to an Airbyte workspace](#step-3). You can tie each workspace to exactly one data plane.

Once you associate a workspace with a data plane, data in that workspace traverses your data plane in the region you've defined.

<!-- Diagram of what is in control plane and what is in data plane? -->

### Limitations and considerations

Before you begin, beware of the following limitations, and consider how they might impact your environment.

#### Some data resides in the control plane

While data planes process data in their respective regions, some metadata remains in the control plane.

- Airbyte stores Cursor and Primary Key data in the control plane regardless of data plane location. If you have data that you can't store in the region used by your control plane, don't use it as a cursor or primary key.

- Airbyte stores logs in the control plane regardless of data plane location.

- The Connector Builder processes all data through the control plane, regardless of workspace settings. This limitation applies to the development and testing phase only; published connectors respect workspace data residency settings during syncs.

#### Performance considerations

- Ensure there's sufficient network bandwidth between the control plane and data planes, especially for high-volume data operations.

- Data planes in geographically distant regions may experience increased latency when communicating with the control plane, potentially affecting sync scheduling and status updates.

#### Keep connectors compatible and globally available

- If you create custom connectors, you must deploy custom connectors to each workspace/region you need to use them.

- Ensure connector versions are consistent across all workspaces to prevent unexpected behavior.

- Some connectors with high resource requirements might need special [resource allocation](../operator-guides/configuring-connector-resources).

#### Operational constraints

- Airbyte doesn't provide automatic fail over between regions.

- You can't sync data between different regions. All connections run in a workspace, and all workspaces run in one region.

- Distributed data planes require additional monitoring setup to maintain visibility across all environments.

- Coordinate updates and maintenance across all workspaces to ensure consistency.

#### Scaling and overhead

- Consider limiting the number of regions and data planes to the minimum number you expect to use based on your organization's operational needs and data residency obligations.

- Each region you use requires its own infrastructure resources, increasing your overall system footprint and maintenance overhead.

## Prerequisites

Before you begin, make sure you've completed the following.

1. Deploy your Self-Managed Enterprise version of Airbyte as described in the [implementation guide](implementation-guide).

2. As part of that deployment, you must have configured an external secrets manager. Airbyte relies on client IDs and client secrets to communicate between the control plane and the data plane.

3. You must be an Organization Administrator to manage regions, data planes, and workspaces.

4. Set up the Cloud or physical infrastructure needed to host your data planes.

<!-- Anything else? -->

## 1. Create a region {#step-1}

The first step is to create a region. Regions are organization-level objects to which you later associate your workspace.

### Request

```bash
curl --request POST \
  --url https://release-1-6-0.releases.abapp.cloud/api/public/v1/regions \
  --header 'authorization: Bearer $TOKEN' \
  --header 'content-type: application/json' \
  --data '{
  "name": "aws-us-east-1",
  "organizationId": "00000000-0000-0000-0000-000000000000",
  "enabled": true
}'
```

For additional request examples, see [the API reference](https://reference.airbyte.com/reference/regions#/).

Provide these parameters in the request body:

- `name`: the name of your region in Airbyte. For simplicity, you might want to make this the same as the actual cloud region this region runs on.

- `organization ID`: Your Airbyte organization ID. In most cases, this is `00000000-0000-0000-0000-000000000000`.

- `enabled`: set to true.

### Response

```json
{
  "regionId": "uuid-string",
  "name": "region-name",
  "organizationId": "org-uuid-string",
  "enabled": true,
  "createdAt": "timestamp-string",
  "updatedAt": "timestamp-string"
}
```

## 2. Create a data plane {#step-2}

Once you have a region, you create a data plane within it.

### Request

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

### Response

## 3. Associate a region to a workspace {#step-3}

One you have a region and a data plane, you need to associate that region to your workspace. Your data planes automatically register with the control plane, but you still need to inform Airbyte where you're hosting those data planes.

To do this, override Airbyte's helm chart values by updating your `values.yaml` file, then redeploy your Airbyte instance.

:::note
You can only associate a workspace with one data plane at a time.
:::

### Update your `values.yaml` file

```yaml title="values.yaml"
TBD
```

### Redeploy Airbyte

In your terminal:

```bash
helm install \
--namespace airbyte \
--values ./values.yaml \
airbyte-enterprise \
airbyte/airbyte
```

## Manage your regions and data planes

### Check which region your workspaces use

#### From Airbyte's UI

You can see a list of your workspaces and the region associated to each from Airbyte's organization settings.

1. In Airbyte's user interface, click **Settings**.

2. Click **General**.

Airbyte displayed your workspaces and their associated region under **Regions**.

#### From Airbyte's API

<!-- My guess is we can query the workspace API and it's in the dataResidency field -->

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

List all data planes in a region.

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
