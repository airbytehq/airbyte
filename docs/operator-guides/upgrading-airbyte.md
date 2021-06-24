# Upgrading Airbyte

## Overview

This tutorial will describe how to determine if you need to run this upgrade process, and if you do, how to do so. This process does require temporarily turning off Airbyte.

## Determining if you need to Upgrade

All minor and major version releases requiring updating the data that Airbyte stores internally. We follow standard [Semantic Versioning](https://semver.org/) conventions. You can always find the latest stable version of Airbyte in our repository [here](https://github.com/airbytehq/airbyte/blob/master/.env#L1). If you are upgrading to a new major or minor version follow the steps below to upgrade your configuration data.

{% hint style="info" %}
If you inadvertently upgrade to a version of Airbyte that is not compatible with your data, the docker containers will not start up and will log an error stating the incompatibility. In these cases, you should downgrade to the previous version that worked and follow the steps below. On the other hand, if you don't mind losing your current Airbyte configuration or have never setup any proper connections yet, you can skip the migrating operations and jump directly to step 5 below.
{% endhint %}

## Upgrading

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
