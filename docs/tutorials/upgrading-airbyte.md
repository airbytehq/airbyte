# Upgrading Airbyte

## Overview

This tutorial will describe how to determine if you need to run this upgrade process, and if you do, how to do so. This process does require temporarily turning off Airbyte.

## Determining if you need to Upgrade

All minor and major version releases requiring updating the data that Airbyte stores internally. We follow standard [Semantic Versioning](https://semver.org/) conventions. You can always find the latest stable version of Airbyte in our repository [here](https://github.com/airbytehq/airbyte/blob/master/.env#L1). If you are upgrading to a new major or minor version follow the steps below to upgrade your configuration data.

{% hint style="info" %}
If you inadvertently upgrade to a version of Airbyte that is not compatible with your data, the docker containers will not start up and will log an error stating the incompatibility. In these cases, you should downgrade to the previous version that worked and follow the steps below.
On the other hand, if you don't mind losing your current Airbyte configuration or have never setup any proper connections yet, you can skip the migrating operations and jump directly to step 5 below.
{% endhint %}

## Upgrading \(Docker\)

1. Turn off Airbyte

   ```text
   docker-compose down
   ```

2. Turn on the Airbyte web app, server, and db.

   ```text
   docker-compose up db server webapp
   ```

3. Navigate to the Admin page in the UI. Then go to the Configuration Tab. Click Export. This will download a gzipped tarball of all of your Airbyte configuration data and sync history. _Note: Any secrets that you have entered into Airbyte will be in this archive, so you should treat it as secret._
4. Migrate the archive to the new version using the Migration App \(packaged in a docker container\).

   ```bash
   docker run --rm -v <path to directory containing downloaded airbyte_archive.tar.gz>:/config airbyte/migration:<version you are upgrading to> --\
   --input /config/airbyte_archive.tar.gz\
   --output <path to where migrated archive will be written (should end in .tar.gz)>\
   --target-version <version you are migrating to or empty for latest>
   ```

Here's an example of what might look like with the values filled in. It assumes that the downloaded `airbyte_archive.tar.gz` is in `/tmp`.

```bash
docker run --rm -v /tmp:/config airbyte/migration:0.18.1-alpha --\
  --input /config/airbyte_archive.tar.gz\
  --output /config/airbyte_archive_migrated.tar.gz
```

{% hint style="info" %}
It may seem confusing that you need to specify the target version twice. The version passed as `--target-version` specifies the version to which the data will be migrated. Specifying the target version in the docker container tag makes sure that you are pulling an image that at least has the migration for the version you want. Technically the version used in the docker tag can be equal to or greater than the version you are upgrading to. For the simplicity of this tutorial we have them match.
{% endhint %}

5. Turn off Airbyte fully.

   ```text
   docker-compose down
   ```

6. Delete the existing Airbyte docker volumes. _Note: Make sure you have already exported your data \(step 3\). This command is going to delete your data in Docker!_

   ```bash
   docker volume rm $(docker volume ls -q | grep airbyte)
   ```

7. Upgrade the docker instance to new version.

   i. If you are running Airbyte from a cloned version of the Airbyte repo and want to use the current most recent stable version, just `git pull`.

   ii. If you are running Airbyte from a `.env`, edit the `VERSION` field in that file to be the desired version.

8. Bring Airbyte back online.

   ```text
   docker-compose up
   ```

9. Complete Preferences section. In the subsequent setup page click "Skip Onboarding". Navigate to the Admin page in the UI. Then go to the Configuration Tab. Click Import. This will prompt you to upload the migrated archive to Airbyte. After this completes, your upgraded Airbyte instance will now be running with all of your original configuration.

This step will throw an exception if the data you are trying to upload does not match the version of Airbyte that is running.

## API Instruction

If you prefer to import and export your data via API instead the UI, follow these instructions:

1. Instead of Step 3 above use the following curl command to export the archive:

   ```bash
   curl -H "Content-Type: application/json" -X POST localhost:8001/api/v1/deployment/export --output /tmp/airbyte_archive.tar.gz
   ```

2. Instead of Step X above user the following curl command to import the migrated archive:

   ```bash
   curl -H "Content-Type: application/x-gzip" -X POST localhost:8001/api/v1/deployment/import --data-binary @<path to arhive>
   ```

Here is an example of what this request might look like assuming that the migrated archive is called `airbyte_archive_migrated.tar.gz` and is in the `/tmp` directory.

```bash
curl -H "Content-Type: application/x-gzip" -X POST localhost:8001/api/v1/deployment/import --data-binary @/tmp/airbyte_archive_migrated.tar.gz
```

## Upgrading \(K8s\)

_coming soon_

