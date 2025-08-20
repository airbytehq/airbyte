---
products: oss-*
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Upgrading Airbyte

Upgrades require temporarily turning off Airbyte. During upgrades, Airbyte will attempt to upgrade some connector versions. The following rules determine which connectors may be automatically upgraded: 

   1. If you're not using a connector, Airbyte upgrades it to the latest version.
   
   2. If you're using a connector, Airbyte does not upgrade it, to avoid disrupting your work. If you want to upgrade a specific connector, do so from the settings page.

Refer to [Managing Connector Updates](/platform/managing-airbyte/connector-updates) for more details about keeping connectors updated.

## Upgrading Airbyte deployed on Kubernetes with Helm

Upgrade by updating your `values.yaml` file and redeploying Airbyte. If you're not using a `values.yaml` to deploy Airbyte using Helm, you can jump directly to step `4`.

1. If you're not sure which chart versions you're running, run `helm list -n <NAMESPACE>`.

2. Check the [release notes](/release_notes/) to see what versions are available and review any requirements to upgrade. You can also see which Helm chart versions are available in the [Airbyte ArtifactHub](https://artifacthub.io/packages/helm/airbyte/airbyte).

3. Update your `values.yaml` file if necessary. In most cases, you only need to do this if you want to implement a new feature from the new version.

4. Run the following command to upgrade.

   <Tabs groupId="helm-chart-version">
   <TabItem value='helm-1' label='Helm chart V1' default>

   ```bash
   helm upgrade --install <RELEASE-NAME> airbyte/airbyte --values <VALUES.YAML> --version <HELM-APP-VERSION>
   ```

   </TabItem>
   <TabItem value='helm-2' label='Helm chart V2' default>

   ```bash
   helm upgrade airbyte airbyte-v2/airbyte \
   --namespace airbyte-v2 \       # Target Kubernetes namespace
   --values ./values.yaml \       # Custom configuration values
   --version 2.0.3 \              # Helm chart version to use
   --set global.image.tag=1.7.0   # Airbyte version to use
   ```

   </TabItem>
   </Tabs>

   After 5 minutes, Helm prints a message showing how to port-forward Airbyte. This may take longer on Kubernetes clusters with slow internet connections. In general the message is as follows:

   ```bash
   export POD_NAME=$(kubectl get pods -l "app.kubernetes.io/name=webapp" -o jsonpath="{.items[0].metadata.name}")
   export CONTAINER_PORT=$(kubectl get pod  $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
   echo "Visit http://127.0.0.1:8080 to use your application"
   kubectl  port-forward $POD_NAME 8080:$CONTAINER_PORT
   ```

## Upgrading Airbyte deployed with abctl

`abctl` streamlines the way you manage a local installation of Airbyte OSS. 

Run `abctl local install` to upgrade to the latest version of Airbyte. If you'd like to ensure you're running the latest version of Airbyte, you can check the value of the Helm Chart's app version by running `abctl local status`.

### Upgrade abctl

Occasionally, you need to update `abctl` to the latest version. Do that by running `brew upgrade abctl`. This is separate from upgrading Airbyte. It only upgrades the command line tool.
