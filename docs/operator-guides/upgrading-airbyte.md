# Upgrading Airbyte

## Overview

This tutorial will describe how to determine if you need to run this upgrade process, and if you do, how to do so. This process does require temporarily turning off Airbyte.

When Airbyte is upgraded, it will attempt to upgrade some connector versions. It follows the following rules: 1. if a connector is not used, it will be upgraded to the latest version 2. if a connector is used, it will NOT be upgraded to avoid disrupting working workflows. If you want to upgrade a connector, do so in the settings page in the webapp.

## Determining if you need to Upgrade

Airbyte intelligently performs upgrades automatically based off of your version defined in your `.env` file and will handle data migration for you.

If you are running [Airbyte on Kubernetes](../deploying-airbyte/on-kubernetes.md), you will need to use one of the two processes defined [here](#upgrading-on-k8s-0270-alpha-and-above) that differ based on your Airbyte version.

## Mandatory Intermediate Upgrade

**If your current version of airbyte is < v0.32.0-alpha-patch-1, you first need to upgrade to this version before upgrading to any later version.**

The reason for this is that there are breaking changes made in v0.32.0-alpha-patch-1, and the logic for these changes is removed in later versions, making it impossible to upgrade directly.
To upgrade to v0.32.0-alpha-patch-1, follow the steps in the following sections, but replace the `docker pull` or `wget` commands with the following:

1. If you are in a cloned Airbyte repo, v0.32.0-alpha-patch-1 can be pulled from GitHub with

   ``` 
   git checkout v0.32.0-alpha-patch-1
   ```

2. If you are running Airbyte from downloaded `docker-compose.yaml` and `.env` files without a GitHub repo, run `wget -N https://raw.githubusercontent.com/airbytehq/airbyte/v0.32.0-alpha-patch-1/{.env,docker-compose.yaml}` to pull this version and overwrite both files.

If you use custom connectors, this upgrade requires all of your connector specs to be retrievable from the node running Airbyte, or Airbyte will fail on startup. If the specs are not retrievable, you need to fix this before proceeding. Alternatively, you could delete the custom connector definitions from Airbyte upon upgrade by setting the `VERSION_0_32_0_FORCE_UPGRADE` environment variable to true. This will cause the server to delete any connectors for which specs cannot be retrieved, as well as any connections built on top of them.

## Upgrading on Docker

1. In a terminal, on the host where Airbyte is running, turn off Airbyte.

   ```bash
   docker-compose down
   ```

2. Upgrade the docker instance to new version.

   i. If you are running Airbyte from a cloned version of the Airbyte GitHub repo and want to use the current most recent stable version, just `git pull`.

   ii. If you are running Airbyte from downloaded `docker-compose.yaml` and `.env` files without a GitHub repo, run `wget -N https://raw.githubusercontent.com/airbytehq/airbyte/master/{.env,docker-compose.yaml}` to pull the latest versions and overwrite both files.

3. Bring Airbyte back online.

   ```bash
   docker-compose up
   ```

### Resetting your Configuration

If you did not start Airbyte from the root of the Airbyte monorepo, you may run into issues where existing orphaned Airbyte configurations will prevent you from upgrading with the automatic process. To fix this, we will need to globally remove these lost Airbyte configurations. You can do this with `docker volume rm $(docker volume ls -q | grep airbyte)`.

:::danger

This will completely reset your Airbyte deployment back to scratch and you will lose all data.

:::

## Upgrading on K8s (0.27.0-alpha and above)

If you are upgrading from (i.e. your current version of Airbyte is) Airbyte version **0.27.0-alpha or above** on Kubernetes :

1. In a terminal, on the host where Airbyte is running, turn off Airbyte.

   ```bash
   kubectl delete deployments airbyte-db airbyte-scheduler airbyte-worker airbyte-server airbyte-temporal airbyte-webapp --namespace=<yournamespace or default>
   ```

2. Upgrade the kube deployment to new version.

   i. If you are running Airbyte from a cloned version of the Airbyte GitHub repo and want to use the current most recent stable version, just `git pull`.

3. Bring Airbyte back online.

   ```bash
   kubectl apply -k kube/overlays/stable
   ```

   After 2-5 minutes, `kubectl get pods | grep airbyte` should show `Running` as the status for all the core Airbyte pods. This may take longer on Kubernetes clusters with slow internet connections.

   Run `kubectl port-forward svc/airbyte-webapp-svc 8000:80` to allow access to the UI/API.

## Upgrading on K8s (0.26.4-alpha and below)

If you are upgrading from (i.e. your current version of Airbyte is) Airbyte version **before 0.27.0-alpha** on Kubernetes we **do not** support automatic migration. Please follow the following steps to upgrade your Airbyte Kubernetes deployment.

1. Switching over to your browser, navigate to the Admin page in the UI. Then go to the Configuration Tab. Click Export. This will download a compressed back-up archive \(gzipped tarball\) of all of your Airbyte configuration data and sync history locally.

   _Note: Any secrets that you have entered into Airbyte will be in this archive, so you should treat it as a secret._

2. Back to the terminal, migrate the local archive to the new version using the Migration App (packaged in a docker container).

   ```bash
   docker run --rm -v <path to directory containing downloaded airbyte_archive.tar.gz>:/config airbyte/migration:<version you are upgrading to> --\
     --input /config/airbyte_archive.tar.gz\
     --output <path to where migrated archive will be written (should end in .tar.gz)>\
     [ --target-version <version you are migrating to or empty for latest> ]
   ```

   Here's an example of what it might look like with the values filled in. It assumes that the downloaded `airbyte_archive.tar.gz` is in `/tmp`.

   ```bash
   docker run --rm -v /tmp:/config airbyte/migration:0.40.0-alpha --\
   --input /config/airbyte_archive.tar.gz\
   --output /config/airbyte_archive_migrated.tar.gz
   ```

3. Turn off Airbyte fully and **(see warning)** delete the existing Airbyte Kubernetes volumes.

   _WARNING: Make sure you have already exported your data \(step 1\). This command is going to delete your data in Kubernetes, you may lose your airbyte configurations!_

   This is where all airbyte configurations are saved. Those configuration files need to be upgraded and restored with the proper version in the following steps.

   ```bash
   # Careful, this is deleting data!
   kubectl delete -k kube/overlays/stable
   ```

4. Follow **Step 2** in the `Upgrading on Docker` section to check out the most recent version of Airbyte. Although it is possible to migrate by changing the `.env` file in the kube overlay directory, this is not recommended as it does not capture any changes to the Kubernetes manifests.
5. Bring Airbyte back up.

   ```bash
   kubectl apply -k kube/overlays/stable
   ```

6. Switching over to your browser, navigate to the Admin page in the UI. Then go to the Configuration Tab and click on Import. Upload your migrated archive.

If you prefer to import and export your data via API instead the UI, follow these instructions:

1. Instead of Step 3 above use the following curl command to export the archive:

   ```bash
   curl -H "Content-Type: application/json" -X POST localhost:8000/api/v1/deployment/export --output /tmp/airbyte_archive.tar.gz
   ```

2. Instead of Step X above user the following curl command to import the migrated archive:

   ```bash
   curl -H "Content-Type: application/x-gzip" -X POST localhost:8000/api/v1/deployment/import --data-binary @<path to arhive>
   ```

Here is an example of what this request might look like assuming that the migrated archive is called `airbyte_archive_migrated.tar.gz` and is in the `/tmp` directory.

```bash
curl -H "Content-Type: application/x-gzip" -X POST localhost:8000/api/v1/deployment/import --data-binary @/tmp/airbyte_archive_migrated.tar.gz
```

