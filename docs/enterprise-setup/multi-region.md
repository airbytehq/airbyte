---
products: oss-enterprise
---

# Set up multiple regions

Self-Managed Enterprise customers can use Airbyte's public API to define regions and create self-registering data planes that operate in those regions. This ensures you're satisfying your data residency and governance requirements with a single Airbyte deployment.

## How it works

By default, Airbyte has a single data plane that any workspace in the organization can access, and it's automatically tied to the default workspace when Airbyte first starts.

To configure additional data planes and associate them to specific workspaces, you complete the steps below.

1. Create a region.
2. Create a data plane in that region. The data plane automatically registers with the control plane.
3. Associate your data plane to your Airbyte workspace. You can tie each workspace to exactly one data plane.

Once you associate a workspace with a data plane, data in that workspace traverses your data plane in the region you've defined.

<!-- Diagram of what is in control plane and what is in data plane? -->

### Limitations and considerations

Before you begin, beware of the following limitations, and consider how they might impact your environment.

#### Data residency

While data planes process data in their respective regions, some metadata remains in the control plane.

- Airbyte stores Cursor and Primary Key data in the US control plane regardless of data plane location. If you have data that you can't store in the US, don't use it as a cursor or primary key.

- Airbyte stores logs in the US control plane regardless of data plane location.

- The Connector Builder processes all data through US data planes, regardless of workspace settings. This limitation applies to the development and testing phase only; published connectors respect workspace data residency settings during syncs.

#### Performance

- Data planes in geographically distant regions may experience increased latency when communicating with the control plane, potentially affecting sync scheduling and status updates.

- Ensure sufficient network bandwidth between the control plane and data planes, especially for high-volume data operations.

- Moving data between regions may incur additional cloud provider costs and latency. <!-- is this a thing? -->

#### Connector compatibility

- If you create custom connectors, you must deploy custom connectors to each workspace/region you need to use them.

- Ensure connector versions are consistent across all data planes to prevent unexpected behavior. <!-- is this a thing? -->

- Some connectors with high resource requirements may need special configuration. <!-- I guess this would be like resource provisioning maybe -->

#### Operational constraints

- There's no automatic fail over between data planes. Workspaces only run in one region.

- Distributed data planes require additional monitoring setup to maintain visibility across all environments.

- Maintenance Windows: Updates and maintenance must be coordinated across all data planes to ensure system consistency.

#### Scaling

- While there is no hard limit on the number of data planes, practical management considerations suggest limiting to 10-15 data planes per organization.

- Each additional data plane requires its own infrastructure resources, increasing overall system footprint.

- Each data plane adds configuration and maintenance overhead.

## Prerequisites

Before you begin, make sure you've completed the following.

1. Deploy your Self-Managed Enterprise version of Airbyte as described in the [implementation guide](implementation-guide).

2. As part of that deployment, you must have configured an external secrets manager. Airbyte relies on client IDs and client secrets to communicate between the control plane and the data plane.

3. You must be an Organization Administrator to manage regions, data planes, and workspaces.

<!-- Anything else? -->

## 1. Create a region

The first step is to create a region. Regions are organization-level objects to which you later associate your workspace.

<!-- I'm a bit unclear how we associate the region with an actual geographical region, this is self-hosted -->

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

Once you have a region, you create a data plane within in.

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

You can associate a workspace with a data plane using either the API or the Airbyte UI.

:::note
You can only associate a workspace with one data plane at a time. To change the data plane for a workspace, simply update the region association using either of the following methods.
:::

### Using the API

```bash
???
```

<!-- values.yaml? -->

### Using the Airbyte UI

1. In Airbyte's user interface, click **Settings**.
2. Click **Workspace**.
3. Under **Data Residency**, select the region you want to associate with this workspace from the dropdown menu.
4. Click **Save**.

Once you've associated a workspace with a region, all data processing for that workspace occurs in the data plane in that region. Existing connections continue to use their current data plane until the next sync.

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
