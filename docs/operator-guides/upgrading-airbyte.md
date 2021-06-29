# Upgrading Airbyte

## Overview

This tutorial will describe how to determine if you need to run this upgrade process, and if you do, how to do so. This process does require temporarily turning off Airbyte.

## Determining if you need to Upgrade

All minor and major version releases requiring updating the data that Airbyte stores internally. We follow standard [Semantic Versioning](https://semver.org/) conventions. You can always find the latest stable version of Airbyte in our repository [here](https://github.com/airbytehq/airbyte/blob/master/.env#L1). If you are upgrading to a new major or minor version follow the steps below to upgrade your configuration data.

{% hint style="info" %}
If you inadvertently upgrade to a version of Airbyte that is not compatible with your data, the docker containers will not start up and will log an error stating the incompatibility. In these cases, you should downgrade to the previous version that worked and follow the steps below. On the other hand, if you don't mind losing your current Airbyte configuration or have never setup any proper connections yet, you can skip the migrating operations and jump directly to step 5 below.
{% endhint %}

## Upgrading \(Docker\)

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

## Upgrading \(K8s\)

Airbyte Kubernetes **does not** support automatic migration. Please follow the following steps to upgrade your Airbyte Kubernetes deployment.

1. Switching over to your browser, navigate to the Admin page in the UI. Then go to the Configuration Tab. Click Export. This will download a compressed back-up archive \(gzipped tarball\) of all of your Airbyte configuration data and sync history locally.

   _Note: Any secrets that you have entered into Airbyte will be in this archive, so you should treat it as secret._

2. Back to the terminal, migrate the local archive to the new version using the Migration App \(packaged in a docker container\).

   ```bash
   docker run --rm -v <path to directory containing downloaded airbyte_archive.tar.gz>:/config airbyte/migration:<version you are upgrading to> --\
     --input /config/airbyte_archive.tar.gz\
     --output <path to where migrated archive will be written (should end in .tar.gz)>\
     [ --target-version <version you are migrating to or empty for latest> ]
   ```

   Here's an example of what it might look like with the values filled in. It assumes that the downloaded `airbyte_archive.tar.gz` is in `/tmp`.

   ```bash
   docker run --rm -v /tmp:/config airbyte/migration:0.26.4-alpha --\
   --input /config/airbyte_archive.tar.gz\
   --output /config/airbyte_archive_migrated.tar.gz
   ```

3. Turn off Airbyte fully and **\(see warning\)** delete the existing Airbyte Kubernetes volumes.

   _WARNING: Make sure you have already exported your data \(step 1\). This command is going to delete your data in Kubernetes, you may lose your airbyte configurations!_

   This is where all airbyte configurations are saved. Those configuration files need to be upgraded and restored with the proper version in the following steps.

   ```bash
   # Careful, this is deleting data!
   kubectl delete -k kube/overlays/stable
   ```
4. Follow **Step 2** in the [Docker upgrade process](#Upgrading-\(Docker\)) to check out the most recent version of Airbyte. Although it is possible to
   migrate by changing the `.env` file in the kube overlay directory, this is not recommended as it does not capture any changes to the Kubernetes manifests.

5. Bring Airbyte back up.
   ```bash
   kubectl apply -k kube/overlays/stable
   ```
6. Follow **Step 8** in the [Docker upgrade process](#Upgrading-\(Docker\)) to upload your migrated Archive and restore your configuration and data.

## API Instruction

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
