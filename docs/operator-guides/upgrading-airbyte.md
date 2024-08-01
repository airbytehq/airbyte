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

This document explains how to determine if you need to upgrade your Airbyte instance as well as how to proceed with an upgrade when needed. 

**Note: Upgrades require temporarily turning off Airbyte.**

During upgrades, Airbyte will attempt to upgrade some connector versions. The following rules determine which connectors may be automatically upgraded: 

   1. If a connector is not used, it will be upgraded to the latest version 
   
   2. If a connector is used, it will NOT be upgraded to avoid disrupting working workflows. If you want to upgrade a specific connector, do so in the settings page in the webapp.

Refer to [Managing Connector Updates](../managing-airbyte/connector-updates.md) for more details about keeping connectors updated.

## Determining if you need to upgrade

Airbyte intelligently performs upgrades automatically based on the version defined in your `.env` file and will handle data migration for you.

<em>If you are using an Airbyte version earlier than v0.32.0-alpha-patch-1, you must upgrade to this version as an intermediary step before upgrading to any later version. Read more about this process [here](#mandatory-intermediate-upgrade)</em>

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

## Upgrading on Docker

:::note

Airbyte version 0.40.27 or later requires [Docker Compose V2](https://docs.docker.com/compose/compose-v2/) to be [installed](https://docs.docker.com/compose/install/) before upgrading.

:::

1. In a terminal, on the host where Airbyte is running, turn off Airbyte.

   ```bash
   docker compose down
   ```

2. Upgrade the Airbyte instance in Docker to a new version.

   1. If you are running Airbyte from a cloned version of the Airbyte GitHub repo and want to use the current most recent stable version, just `git pull`.

   2. If you are running Airbyte from downloaded `docker-compose.yaml` and `.env` files without a GitHub repo, run `wget https://raw.githubusercontent.com/airbytehq/airbyte/master/run-ab-platform.sh` to download the installation script.

3. Remove previous local `docker-compose.yaml` and `.env`

   ```bash
   ./run-ab-platform.sh -r
   ```

4. Bring Airbyte back online, optionally with the `-b` flag to run the containers in the background (Docker detached mode).

   ```bash
   ./run-ab-platform.sh -b
   ```

## Upgrading with abctl

`abctl` streamlines the way you manage a local installation of Airbyte OSS. 

Run `abctl local install` to upgrade to the latest version of Airbyte. If you'd like to ensure you're running the latest version of Airbyte, you can check the value of the Helm Chart's app version by running `abctl local status`.

:::note
Occasionally, `abctl` itself will need to be updated. Do that by running `brew update abctl`. This is seperate from upgrading Airbyte and only upgrades the command line tool.
:::

### Resetting your Configuration

If you did not start Airbyte from the root of the Airbyte monorepo, you may run into issues where existing orphaned Airbyte configurations will prevent you from upgrading with the automatic process. To fix this, we will need to globally remove these lost Airbyte configurations. You can do this with `docker volume rm $(docker volume ls -q | grep airbyte)`.

:::danger

This will completely reset your Airbyte deployment. You will lose all data.

:::



## Older Versions

<details>
  <summary>Mandatory Intermediate Upgrade for **version 0.32.0-alpha-patch-1**</summary>

**If your current version of airbyte is < v0.32.0-alpha-patch-1, you first need to upgrade to this version before upgrading to any later version.**

The reason for this is that there are breaking changes made in v0.32.0-alpha-patch-1, and the logic for these changes is removed in later versions, making it impossible to upgrade directly.
To upgrade to v0.32.0-alpha-patch-1, follow the steps in the following sections, but replace the `docker pull` or `wget` commands with the following:

1. If you are in a cloned Airbyte repo, v0.32.0-alpha-patch-1 can be pulled from GitHub with

   ```
   git checkout v0.32.0-alpha-patch-1
   ```

2. If you are running Airbyte from downloaded `docker-compose.yaml` and `.env` files without a GitHub repo, run `wget -N https://raw.githubusercontent.com/airbytehq/airbyte/v0.32.0-alpha-patch-1/{.env,flags.yml,docker-compose.yaml}` to pull this version and overwrite both files.

If you use custom connectors, this upgrade requires all of your connector specs to be retrievable from the node running Airbyte, or Airbyte will fail on startup. If the specs are not retrievable, you need to fix this before proceeding. Alternatively, you could delete the custom connector definitions from Airbyte upon upgrade by setting the `VERSION_0_32_0_FORCE_UPGRADE` environment variable to true. This will cause the server to delete any connectors for which specs cannot be retrieved, as well as any connections built on top of them.

</details>

