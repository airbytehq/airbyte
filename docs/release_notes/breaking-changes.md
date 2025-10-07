---
products: oss-*
---

# Breaking change list

Occasionally, new versions of Airbyte introduce breaking changes. This page inventories breaking changes between versions and any necessary steps to mitigate the change.

When you upgrade your Self-Managed instance of Airbyte to a version with a breaking change, you may need to take mitigating action. If you are upgrading multiple versions at once, complete the mitigaton steps for the versions you are skipping as well.

## Self-Managed Community

### 1.7.x to 1.8.x

- Airbyte no longer publishes a `webapp` image and it's no longer independently deployable. To mitigate this, complete 1.7 ingress update.

### 1.6.x to 1.7.x

- Airbyte began removing the `webapp` service and moving its functions to `server`. To mitigate this, [update your ingress](/platform/deploying-airbyte/integrations/ingress-1-7)

## Self-Managed Enterprise

### 1.7.x to 1.8.x

- Airbyte no longer publishes a `webapp` image and it's no longer independently deployable. To mitigate this, complete 1.7 ingress update.

### 1.6.x to 1.7.x

- Airbyte began removing the `webapp` service and moving its functions to `server`. To mitigate this, [update your ingress](/platform/deploying-airbyte/integrations/ingress-1-7).

### 1.5.x to 1.6.x

- Service accounts require a new permission. [Update your service account](/platform/enterprise-setup/upgrade-service-account)
