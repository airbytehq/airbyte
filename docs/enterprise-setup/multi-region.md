---
products: oss-enterprise
---

# Multiple region deployments

Self-Managed Enterprise customers can use Airbyte's public API to define regions and create self-registering data planes that operate in those regions. This ensures you're satisfying your data residency and governance requirements with a single Airbyte deployment.

![Stylized diagram showing a control plane above multiple data planes in different global regions](assets/data-planes.png)

## How it works

If you're not very familiar with Kubernetes, think of the control plane as the brain and data planes as the muscles doing work the brain tells them to do.

- The control plane is responsible for Airbyte's user interface, APIs, Terraform provider, and orchestrating work.
- The data plane initiates jobs, syncs data, completes jobs, and reports its status back to the control plane.

This separation of duties is what allows a single Airbyte deployment to ensure your data remains segregated and compliant.

By default, Airbyte has a single data plane that any workspace in the organization can access, and it's automatically tied to the default workspace when Airbyte first starts. To configure additional data planes and regions, you complete the steps below.

1. [Create a region](#step-1).
2. [Create a data plane](#step-2) in that region.
3. [Associate your data plane to an Airbyte workspace](#step-3). You can tie each workspace to exactly one region.

Once you associate a workspace with a data plane, data in that workspace traverses your data plane in the region you've defined.

### Limitations and considerations

Before you begin, consider the following points and how they might impact your environment.

#### Some metadata resides in the control plane

While data planes process data in their respective regions, some metadata remains in the control plane.

- Airbyte stores Cursor and Primary Key data in the control plane regardless of data plane location. If you have data that you can't store in the region used by your control plane, don't use it as a cursor or primary key.

- Airbyte stores logs in the control plane regardless of data plane location.

- The Connector Builder processes all data through the control plane, regardless of workspace settings. This limitation applies to the development and testing phase only; published connectors respect workspace data residency settings during syncs.

#### Performance considerations

- Ensure there's sufficient network bandwidth between the control plane and data planes, especially for high-volume data operations.

- Data planes in geographically distant regions may experience increased latency when communicating with the control plane.

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

- Consider limiting the number of regions and data planes to the minimum number you expect to use based on your organization's operational needs and data residency obligations. Each region you use requires its own infrastructure resources, increasing your overall system footprint and maintenance overhead.

## Prerequisites

Before you begin, make sure you've completed the following.

### Deploy Airbyte

1. Deploy your Self-Managed Enterprise version of Airbyte as described in the [implementation guide](implementation-guide).

2. As part of that deployment, you must have configured an external secrets manager.

3. You must be an Organization Administrator.

### Get API access

If you haven't already, create an application and generate an access token. For help, see [Configuring API access](../enterprise-setup/api-access-config).

## 1. Create a region {#step-1}

The first step is to create a region. Regions are objects that contain data planes, and which you associate to workspaces.

<details>
  <summary>Request</summary>

Send a POST request to /v1/regions/.

```bash
curl --request POST \
  --url https://example.com/api/public/v1/regions \
  --header 'authorization: Bearer $TOKEN' \
  --header 'content-type: application/json' \
  --data '{
  "name": "aws-us-east-1",
  "organizationId": "00000000-0000-0000-0000-000000000000",
  "enabled": true
}'
```

Include the following parameters in your request.

| Body parameter   | Description                                                                                                                              |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `name`           | The name of your region in Airbyte. For simplicity, you might want to make this the same as the actual cloud region this region runs on. |
| `organizationId` | Your Airbyte organization ID. In most cases, this is `00000000-0000-0000-0000-000000000000`.                                             |
| `enabled`        | Set this to true.                                                                                                                        |

For additional request examples, see [the API reference](https://reference.airbyte.com/reference/regions#/).

</details>

<details>
  <summary>Response</summary>

Make note of your `regionId`. You need it to create a data plane.

```json title="200 Successful operation"
{
  //highlight-next-line
  "regionId": "uuid-string",
  "name": "region-name",
  "organizationId": "org-uuid-string",
  "enabled": true,
  "createdAt": "timestamp-string",
  "updatedAt": "timestamp-string"
}
```

</details>

## 2. Create a data plane {#step-2}

Once you have a region, you create a data plane within it.

<details>
  <summary>Request</summary>

Send a POST request to /v1/regions/`<REGION_ID>`/dataplanes.

```bash
curl --request POST \
  --url https://example.com/api/public/v1/regions/116a49ab-b04a-49d6-8f9e-4d9d6a4189cc/dataplanes \
  --header 'authorization: Bearer $TOKEN' \
  --header 'content-type: application/json' \
  --data '{
  "name": "aws-us-west-3-dp-8",
  "enabled": true
}'
```

Include the following parameters in your request.

| Body parameter | Description                                                                                                         |
| -------------- | ------------------------------------------------------------------------------------------------------------------- |
| `name`         | The name of your data plane. For simplicity, you might want to name it based on the region in which you created it. |
| `enabled`      | Set this to true.                                                                                                   |

For additional request examples, see [the API reference](https://reference.airbyte.com/reference/regions#/).

</details>

<details>
  <summary>Response</summary>

Make note of your `dataplaneId`, `clientId` and `clientSecret`. You need them to associate your workspace to a region.

```json title="200 Successful operation"
json
{
  "dataplaneId": "uuid-string",
  "clientId": "client-id-string",
  "clientSecret": "client-secret-string"
}
```

</details>

## 3. Associate a region to a workspace {#step-3}

One you have a region and a data plane, you need to associate that region to your workspace.

Your data planes self-register with the control plane, but you still need to inform Airbyte where you're hosting those data planes. Override Airbyte's helm chart values by updating your `values.yaml` file, then redeploy your Airbyte instance.

:::note
You can only associate each workspace with one region.
:::

### Update your deployment values

Add the following overrides to the `values.yaml` file you use to deploy Airbyte.

```yaml title="values.yaml"
dataPlane:
  secretName: "data-plane-creds"
  id: "preview-data-plane"
  clientIdSecretName: "data-plane-creds"
  clientIdSecretKey: "DATA_PLANE_CLIENT_ID" # Use the client ID returned in step 2
  clientSecretSecretName: "data-plane-creds"
  clientSecretSecretKey: "DATA_PLANE_CLIENT_SECRET" # Use the client secret returned in step 2
```

<!-- I'm still a bit unsure how this is associating a region to a DP -->

### Redeploy Airbyte with your new values

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

Airbyte displays your workspaces and each workspace's region under **Regions**.

#### From Airbyte's API

Request:

```bash
bash
curl -X GET "https://example.com/api/public/v1/workspaces/{workspaceId}" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

Response:

```json
{
  "workspaceId": "18dccc91-0ab1-4f72-9ed7-0b8fc27c5826",
  "name": "Acme Company",
  //highlight-next-line
  "dataResidency": "auto",
}
```

### List all regions

List all regions in your organization.

Request:

```bash
curl --request GET \
  --url 'https://example.com/api/public/v1/regions?organizationId=00000000-0000-0000-0000-000000000000' \
  --header 'authorization: Bearer $TOKEN' \
  --header 'content-type: application/json'
```

Response:

```json
{
  "data": [
    {
      "regionId": "uuid-string",
      "name": "region-name",
      "organizationId": "org-uuid-string",
      "enabled": true,
      "createdAt": "timestamp-string",
      "updatedAt": "timestamp-string"
    }
  ]
}
```

### Get a region

Get information about a region.

Request:

```bash
curl --request GET \
  --url https://example.com/api/public/v1/regions/96129828-e006-4fd6-820f-132dc00a10f2 \
  --header 'authorization: Bearer $TOKEN' \
  --header 'content-type: application/json'
```

Response:

```json
{
  "data": [
    {
      "regionId": "uuid-string",
      "name": "region-name",
      "organizationId": "org-uuid-string",
      "enabled": true,
      "createdAt": "timestamp-string",
      "updatedAt": "timestamp-string"
    }
  ]
}
```

### Update a region

Update, turn on, or turn off a region.

Request:

```bash
curl -X PATCH "https://example.com/api/public/v1/regions/{regionId}" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "updated-region-name",
    "enabled": true
  }'
```

Response:

```json
{
  "regionId": "uuid-string",
  "name": "updated-region-name",
  "organizationId": "org-uuid-string",
  "enabled": true,
  "createdAt": "timestamp-string",
  "updatedAt": "timestamp-string"
}
```

### Delete a region

Delete a region.

```bash
curl --request DELETE \
  --url https://example.com/api/public/v1/regions/8fee0404-6d56-442a-bb54-e28edada1405 \
  --header 'authorization: Bearer $TOKEN' \
  --header 'content-type: application/json'
```

### List data planes

List all data planes in a region.

```bash
curl --request GET \
  --url https://example.com/api/public/v1/regions/116a49ab-b04a-49d6-8f9e-4d9d6a4189cc/dataplanes \
  --header 'authorization: Bearer $TOKEN'
```

### Get a data plane

Get information about a data plane.

```bash
curl --request GET \
  --url https://example.com/api/public/v1/regions/116a49ab-b04a-49d6-8f9e-4d9d6a4189cc/dataplanes/312b4641-2edc-4dc9-9933-41b759d3b2d8 \
  --header 'authorization: Bearer $TOKEN'
```

### Delete a data plane

Delete a data plane from a region.

```bash
curl --request DELETE \
  --url https://example.com/api/public/v1/regions/116a49ab-b04a-49d6-8f9e-4d9d6a4189cc/dataplanes/f1482a93-4786-4662-800e-ff07363418b1 \
  --header 'authorization: Bearer $TOKEN'
```
