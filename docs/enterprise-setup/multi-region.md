---
products: oss-enterprise
---

# Multiple region deployments

Self-Managed Enterprise customers can use Airbyte's public API to define regions and create independent data planes that operate in those regions. This ensures you're satisfying your data residency and governance requirements with a single Airbyte deployment.

![Stylized diagram showing a control plane above multiple data planes in different global regions](assets/data-planes.png)

## How it works

If you're not familiar with Kubernetes, think of the control plane as the brain and data planes as the muscles doing work the brain tells them to do.

- The control plane is responsible for Airbyte's user interface, APIs, Terraform provider, and orchestrating work.
- The data plane initiates jobs, syncs data, completes jobs, and reports its status back to the control plane.

This separation of duties is what allows a single Airbyte deployment to ensure your data remains segregated and compliant.

By default, Airbyte has a single data plane that any workspace in the organization can access, and it's automatically tied to the default workspace when Airbyte first starts. To configure additional data planes and regions, complete these steps.

1. [Create a region](#step-1).
2. [Create a data plane](#step-2) in that region.
3. [Associate your data plane to an Airbyte workspace](#step-3). You can tie each workspace to exactly one region.
4. [Update your values.yaml file](#step-4) with a new Kubernetes secret.
5. [Redeploy Airbyte](#step-5).

Once you complete these steps, jobs in your workspace move data exclusively using the data plane mapped to that region.

### Limitations and considerations

While data planes process data in their respective regions, some metadata remains in the control plane.

- Airbyte stores Cursor and Primary Key data in the control plane regardless of data plane location. If you have data that you can't store in the control plane, don't use it as a cursor or primary key.

- The Connector Builder processes all data through the control plane, regardless of workspace settings. This limitation applies to the development and testing phase only; published connectors respect workspace data residency settings during syncs.

- If you're using a secrets manager, the secrets manager used by the control plane is the one used by the data plane.

## Prerequisites

Before you begin, make sure you've completed the following.

### Deploy Airbyte

- Deploy your Self-Managed Enterprise version of Airbyte as described in the [implementation guide](implementation-guide).

- You must be an Organization Administrator.

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

One you have a region and a data plane, you need to associate that region to your workspace. You can associate a workspace with a region when you create that workspace or later, after it exists.

:::note
You can only associate each workspace with one region.
:::

### When creating a new workspace

<details>
  <summary>Request</summary>

Send a POST request to /v1/workspaces/

```bash
curl -X POST "https://example.com/api/public/v1/workspaces" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My New Workspace",
    "dataResidency": "auto"
  }'
```

Include the following parameters in your request.

| Body parameter  | Description                            |
| --------------- | -------------------------------------- |
| `name`          | The name of your workspace in Airbyte. |
| `dataResidency` | A string with a region identifier.      |

</details>

<details>
  <summary>Response</summary>

```json
{
  "workspaceId": "uuid-string",
  "name": "workspace-name",
  "dataResidency": "auto",
  "notifications": {
    "failure": {},
    "success": {}
  }
}
```

</details>

### When updating a workspace

<details>
  <summary>Request</summary>

Send a PATCH request to /v1/workspaces/`{workspaceId}`

```bash
curl -X PATCH "https://example.com/api/public/v1/workspaces/{workspaceId}" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Workspace Name",
    "dataResidency": "us-west"
  }'
```

Include the following parameters in your request.

| Body parameter  | Description                            |
| --------------- | -------------------------------------- |
| `name`          | The name of your workspace in Airbyte. |
| `dataResidency` | A string with a region identifier.      |

</details>

<details>
  <summary>Response</summary>

```json
{
  "workspaceId": "uuid-string",
  "name": "updated-workspace-name",
  "dataResidency": "region-identifier",
  "notifications": {
    "failure": {},
    "success": {}
  }
}
```

</details>

## 4. Update your deployment values {#step-4}

Add the following overrides to the `values.yaml` file you use to deploy Airbyte. Data planes rely on Kubernetes secrets to communicate with the control plane, and your data planes use these values to identify themselves with the control plane.

```yaml title="values.yaml"
dataPlane:
  # Used to render the data plane credentials secret into the chart.
  secretName: "data-plane-creds"
  id: "preview-data-plane"

  # Describe the secret name and key where each of the client ID and secret are stored.
  clientIdSecretName: "data-plane-creds"
  clientIdSecretKey: "DATA_PLANE_CLIENT_ID"
  clientSecretSecretName: "data-plane-creds"
  clientSecretSecretKey: "DATA_PLANE_CLIENT_SECRET"
```

## 5. Redeploy Airbyte with your new values {#step-5}

In your terminal:

```bash
helm install \
--namespace airbyte \
--values ./values.yaml \
airbyte-enterprise \
airbyte/airbyte
```

## Check which region your workspaces use

### From Airbyte's UI

You can see a list of your workspaces and the region associated to each from Airbyte's organization settings.

1. In Airbyte's user interface, click **Settings**.

2. Click **General**.

Airbyte displays your workspaces and each workspace's region under **Regions**.

### From Airbyte's API

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
