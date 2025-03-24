---
products: oss-*
---

# Upgrading Airbyte

:::info

[Airbyte Cloud](https://cloud.airbyte.com/signup) users always run on the newest
Airbyte version automatically. This documentation only applies to users deploying our self-managed
version.
:::

## Overview

**Note: Upgrades require temporarily turning off Airbyte.**

During upgrades, Airbyte will attempt to upgrade some connector versions. The following rules determine which connectors may be automatically upgraded: 

   1. If a connector is not used, it will be upgraded to the latest version 
   
   2. If a connector is used, it will NOT be upgraded to avoid disrupting working workflows. If you want to upgrade a specific connector, do so in the settings page in the webapp.

Refer to [Managing Connector Updates](../managing-airbyte/connector-updates.md) for more details about keeping connectors updated.

## Upgrading on K8s using Helm

Production setup of our Open Source Software is best accomplished by running it as a Kubernetes deployment via Helm Charts. This simplifies the configuration and deployment process. 

When deployed this way, you'll upgrade by modifying the `values.yaml` file. If you're not using a `values.yaml` to deploy Airbyte using Helm, you can jump directly to step `4`.

1. Access [Airbyte ArtifactHub](https://artifacthub.io/packages/helm/airbyte/airbyte) and select the version you want to upgrade.
2. You can click in `Default Values` and compare the value file between the new version and version you're running. You can run `helm list -n <NAMESPACE>` to check the CHART version you're using.
3. Update your `values.yaml` file if necessary.
4. Upgrade the Helm app by running:

   ```bash
   helm upgrade --install <RELEASE-NAME> airbyte/airbyte --values <VALUE.YAML> --version <HELM-APP-VERSION>
   ```

   After 2-5 minutes, Helm will print a message showing how to port-forward Airbyte. This may take longer on Kubernetes clusters with slow internet connections. In general the message is the following:

   ```bash
   export POD_NAME=$(kubectl get pods -l "app.kubernetes.io/name=webapp" -o jsonpath="{.items[0].metadata.name}")
   export CONTAINER_PORT=$(kubectl get pod  $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
   echo "Visit http://127.0.0.1:8080 to use your application"
   kubectl  port-forward $POD_NAME 8080:$CONTAINER_PORT
   ```

## Upgrading with abctl

`abctl` streamlines the way you manage a local installation of Airbyte OSS. 

Run `abctl local install` to upgrade to the latest version of Airbyte. If you'd like to ensure you're running the latest version of Airbyte, you can check the value of the Helm Chart's app version by running `abctl local status`.

:::note
Occasionally, `abctl` itself will need to be updated. Do that by running `brew update abctl`. This is separate from upgrading Airbyte and only upgrades the command line tool.
:::
