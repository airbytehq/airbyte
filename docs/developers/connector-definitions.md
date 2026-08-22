---
products: all
---

# Manage connector definitions with the API

A **connector definition** is a connector type: "Salesforce", "Postgres", or a
connector you built yourself. It is not a configured connector. When you create a
source or a destination, you pass a `definitionId`, and that definition determines
which connector code runs; your source supplies the configuration and credentials it
runs with.

That distinction is the whole reason the definitions endpoints exist:

| Concept | Endpoint | What it is |
| --- | --- | --- |
| Definition | `/workspaces/{workspaceId}/definitions/sources` | The connector type available in a workspace, and the Docker image version it runs |
| Source | `/sources` | One configured connection to a system, created from a definition |

Definitions are scoped to a workspace, so the same connector can run a different
version in two workspaces of the same organization.

## The three definition endpoints

| Endpoint | Connectors it covers | Read | Create, update, delete |
| --- | --- | --- | --- |
| `definitions/sources` | Source connectors that run a Docker image, both Airbyte's and your custom ones | All deployments | Custom definitions only, and not on Cloud |
| `definitions/destinations` | Destination connectors that run a Docker image | All deployments | Custom definitions only, and not on Cloud |
| `definitions/declarative_sources` | Low-code source connectors built from a Connector Builder manifest | All deployments | All deployments, including Cloud |

Declarative source definitions are deliberately kept apart from `definitions/sources`:
they never appear in its list response, and requesting one by ID there returns a 404.
Use the declarative endpoints for anything built in the Connector Builder.

## Find the definition ID for a connector

This is the most common use of these endpoints, and it needs no custom connectors at
all. List the definitions in a workspace and take the `id` of the connector you want:
that value is the `definitionId` you pass when you create a source or a destination.

```bash
curl --request GET \
  --url 'https://api.airbyte.com/v1/workspaces/<YOUR_WORKSPACE_ID>/definitions/sources' \
  --header 'authorization: Bearer <YOUR_ACCESS_TOKEN>'
```

```json
{
  "data": [
    {
      "id": "dfd88b22-b603-4c3d-aad7-3701784586b1",
      "name": "Sample Data",
      "dockerRepository": "airbyte/source-faker",
      "dockerImageTag": "7.2.1",
      "documentationUrl": "https://docs.airbyte.com/integrations/sources/faker"
    }
  ]
}
```

Then create a source from it:

```bash
curl --request POST \
  --url 'https://api.airbyte.com/v1/sources' \
  --header 'authorization: Bearer <YOUR_ACCESS_TOKEN>' \
  --header 'content-type: application/json' \
  --data '{
    "name": "Sample data",
    "workspaceId": "<YOUR_WORKSPACE_ID>",
    "definitionId": "dfd88b22-b603-4c3d-aad7-3701784586b1",
    "configuration": { "count": 1000 }
  }'
```

The list response is also the answer to "which connector versions is this workspace
running?", which makes it useful for auditing a fleet of workspaces and for scripted
workspace provisioning.

## Add a custom connector on Cloud: declarative source definitions

On Airbyte Cloud, a declarative source definition is the way to add a connector
Airbyte doesn't have. You send a Connector Builder manifest instead of a Docker image,
and Airbyte publishes it as version 1. Your real manifest declares its streams in
`streams`, left empty here for brevity:

```bash
curl --request POST \
  --url 'https://api.airbyte.com/v1/workspaces/<YOUR_WORKSPACE_ID>/definitions/declarative_sources' \
  --header 'authorization: Bearer <YOUR_ACCESS_TOKEN>' \
  --header 'content-type: application/json' \
  --data '{
    "name": "Internal Orders API",
    "manifest": {
      "version": "6.48.15",
      "type": "DeclarativeSource",
      "check": { "type": "CheckStream", "stream_names": ["orders"] },
      "streams": [],
      "spec": {
        "type": "Spec",
        "connection_specification": {
          "$schema": "http://json-schema.org/draft-07/schema#",
          "type": "object",
          "required": [],
          "properties": {}
        }
      }
    }
  }'
```

```json
{
  "id": "9bb26c3b-5125-4492-bb2e-ccda42cfe255",
  "name": "Internal Orders API",
  "version": 1,
  "manifest": { "...": "as sent" }
}
```

Two requirements on the manifest:

- It must contain a `spec` object with a `connection_specification` — the JSON schema
  for your connector's own configuration. Without it, the request fails.
- Its `version` must be a CDK version whose major version your deployment supports. A
  manifest built against a newer major version is rejected with a 409.

The definition also becomes a Connector Builder project, so you can open and edit the
connector in the UI afterwards. The returned `id` is a normal `definitionId`: create
sources from it exactly as above.

### Publish a new version

`PUT` publishes the manifest as the next version and activates it. Versions increment
on their own — the first update to a new definition returns `version: 2` — so this is
the endpoint to call from CI when the manifest changes in git:

```bash
curl --request PUT \
  --url 'https://api.airbyte.com/v1/workspaces/<YOUR_WORKSPACE_ID>/definitions/declarative_sources/<DEFINITION_ID>' \
  --header 'authorization: Bearer <YOUR_ACCESS_TOKEN>' \
  --header 'content-type: application/json' \
  --data '{ "manifest": { "...": "your updated manifest" } }'
```

The request body takes only the manifest. You can't rename a definition this way.

## Add a custom connector on Self-Managed: image-based definitions

If you built a connector with the CDK and pushed it to a registry, register the image
in a workspace with `POST definitions/sources` (or `definitions/destinations`):

```bash
curl --request POST \
  --url '<YOUR_AIRBYTE_URL>/api/public/v1/workspaces/<YOUR_WORKSPACE_ID>/definitions/sources' \
  --header 'authorization: Bearer <YOUR_ACCESS_TOKEN>' \
  --header 'content-type: application/json' \
  --data '{
    "name": "Internal Orders API",
    "dockerRepository": "registry.example.com/airbyte/source-internal-orders",
    "dockerImageTag": "1.4.0",
    "documentationUrl": "https://example.com/docs/source-internal-orders"
  }'
```

Airbyte pulls and runs the image to read its connector specification, so the image
must be reachable from your deployment, and the request can take a while to return on
first pull. This is the API equivalent of
[uploading a Docker-based custom connector](/platform/operator-guides/using-custom-connectors)
in the UI.

To move the connector to a new version, `PUT` the new tag. Both `name` and
`dockerImageTag` are required, so send the current name if you only want to change the
tag:

```bash
curl --request PUT \
  --url '<YOUR_AIRBYTE_URL>/api/public/v1/workspaces/<YOUR_WORKSPACE_ID>/definitions/sources/<DEFINITION_ID>' \
  --header 'authorization: Bearer <YOUR_ACCESS_TOKEN>' \
  --header 'content-type: application/json' \
  --data '{ "name": "Internal Orders API", "dockerImageTag": "1.5.0" }'
```

`DELETE` removes the definition from the workspace and returns it one last time.

:::note
Creating or updating an image-based definition runs the connector image to read its
specification, so these two calls can take a long time when the image isn't cached yet
— long enough for a proxy in front of Airbyte to time out the request before Airbyte
answers. If a create or update appears to time out, `GET` the definition before
retrying: the change may have been applied. If the tag can't be pulled at all, the
call fails and the definition keeps its previous tag.
:::

## What each deployment allows

Two rules explain almost every error these endpoints return:

- **Only custom definitions can be written to.** Airbyte's registry connectors are
  managed for you; updating or deleting one fails with
  `Public definitions cannot be modified.` This holds on every deployment, including
  Self-Managed.
- **Cloud doesn't accept image-based definitions.** Creating or updating a source or
  destination definition on Cloud fails with `Non-declarative definitions cannot be
  created or updated in Airbyte Cloud.` Cloud runs connectors from Airbyte's registry
  plus declarative connectors, so use a declarative source definition instead. There
  is no declarative equivalent for destinations, so custom destinations are a
  Self-Managed capability.

## See also

- [Configuring API access](/platform/using-airbyte/configuring-api-access) — how to get
  an access token
- [API documentation](/developers/api-documentation) — base URLs and your first request
- [Connector Builder overview](/platform/connector-development/connector-builder-ui/overview) —
  building the manifest a declarative definition needs
- [Low-code YAML reference](/platform/connector-development/config-based/understanding-the-yaml-file/yaml-overview) —
  what goes in a manifest
- [Uploading Docker-based custom connectors](/platform/operator-guides/using-custom-connectors) —
  the UI equivalent of image-based definitions
