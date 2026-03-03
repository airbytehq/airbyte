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
   --version 2.x.x                # Helm chart version to use
   ```

   </TabItem>
   </Tabs>

   After 5 minutes, Helm prints a message showing how to port-forward Airbyte. This may take longer on Kubernetes clusters with slow internet connections. In general the message is as follows:

   ```bash
   Get the application URL by running these commands:

   echo "Visit http://127.0.0.1:8080 to use your application"
   kubectl -n airbyte port-forward deployment/airbyte-server 8080:8001
   ```

## Upgrading Airbyte deployed with abctl

`abctl` streamlines the way you manage a local installation of Airbyte Core.

Run `abctl local install` to upgrade to the latest version of Airbyte. If you'd like to ensure you're running the latest version of Airbyte, you can check the value of the Helm Chart's app version by running `abctl local status`.

### Upgrade abctl

Occasionally, you need to update `abctl` to the latest version. This is separate from upgrading Airbyte. It only upgrades the command line tool.

<Tabs defaultValue="abctl-curl">

<TabItem value="abctl-curl" label="curl">

Run the following command to upgrade abctl.

```shell
curl -LsfS https://get.airbyte.com | bash -
```

Verify the upgrade.

```bash
abctl version
```

</TabItem>
<TabItem value="abctl-go" label="Go">

Run the following command to upgrade abctl.

```bash
go install github.com/airbytehq/abctl@latest
```

Verify the upgrade.

```bash
abctl version
```

</TabItem>
<TabItem value="abctl-brew" label="Homebrew">

Run the following command to upgrade abctl.

```bash
brew upgrade abctl
```

Verify the upgrade.

```bash
abctl version
```

</TabItem>
<TabItem value="abctl-linux" label="GitHub - Linux">

1. Verify your processor architecture.

    ```bash
    uname -m
    ```

    If the output is `x86_64`, download the **linux-amd64** release. If the output is `aarch64` or similar, download the **linux-arm64** release.

2. Download the latest release from the [abctl releases page](https://github.com/airbytehq/abctl/releases/latest).

3. Extract the archive. This creates a directory named `abctl`, which contains the executable and other needed files.

    ```bash
    tar -xvzf {name-of-file-downloaded.linux-*.tar.gz}
    ```

4. Replace the existing executable with the new version.

    ```bash
    chmod +x abctl/abctl
    sudo mv abctl /usr/local/bin
    ```

5. Verify the upgrade.

    ```bash
    abctl version
    ```

</TabItem>
<TabItem value="abctl-windows" label="GitHub - Windows">

1. Download the latest release from the [abctl releases page](https://github.com/airbytehq/abctl/releases/latest). Download the **windows-amd64** or **windows-arm64** release depending on your processor architecture.

2. Extract the zip file to the same location where you previously installed abctl, replacing the existing files.

3. Verify the upgrade.

    ```bash
    abctl version
    ```

</TabItem>
</Tabs>
