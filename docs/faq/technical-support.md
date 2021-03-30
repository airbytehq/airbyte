---
description: Common issues and their workarounds
---

# Technical Support

## `docker.errors.DockerException: Error while fetching server API version`

If you see the following error:
```
docker.errors.DockerException: Error while fetching server API
version: ('Connection aborted.', FileNotFoundError(2, 'No such file or
directory'))
```

It usually means that Docker isn't running on your machine (and a running Docker daemon is required to run Airbyte). An easy way to verify this is to run `docker ps`, which will show `Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?` if the Docker daemon is not running on your machine.

## Airbyte is stuck while loading required configuration parameters for my connector

Example of the issue:

![](../.gitbook/assets/faq_stuck_onboarding.png)

To load configuration parameters, Airbyte must first `docker pull` the connector's image, which may be many hundreds of megabytes. Under poor connectivity conditions, the request to pull the image may take a very long time or time out. More context on this issue can be found [here](https://github.com/airbytehq/airbyte/issues/1462). If your Internet speed is less than 30Mbps down or are running bandwidth-consuming workloads concurrently with Airbyte, you may encounter this issue. Run a [speed test](https://fast.com/) to verify your internet speed.

One workaround is to manually pull the latest version of every connector you'll use then resetting Airbyte. Note that this will remove any configured connections, sources, or destinations you currently have in Airbyte. To do this:

1. Decide which connectors you'd like to use. For this example let's say you want the Postgres source and the Snowflake destination.
2. Find the Docker image name of those connectors. Look [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/init/src/main/resources/seed/source_definitions.yaml) for sources and [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/init/src/main/resources/seed/destination_definitions.yaml) for destinations. For each of the connectors you'd like to use, copy the value of the `dockerRepository` and `dockerImageTag` fields. For example, for the Postgres source this would be `airbyte/source-postgres` and e.g `0.1.6`.
3. For **each of the connectors** you'd like to use, from your shell run `docker pull <repository>:<tag>`, replacing `<repository>` and `<tag>` with the values copied from the step above e.g: `docker pull airbyte/source-postgres:0.1.6`.
4. Once you've finished downloading all the images, from the Airbyte repository root run `docker-compose down -v` followed by `docker-compose up`.
5. The issue should be resolved.

If the above workaround does not fix your problem, please report it [here](https://github.com/airbytehq/airbyte/issues/1462) or in our [Slack](https://slack.airbyte.io).

## One of your sync jobs is failing

Several things to check:

* **Is Airbyte updated to your latest version?** You can see the latest version [here](https://github.com/airbytehq/airbyte/tags). If not, please upgrade to the latest one, [upgrading instructions are here](../tutorials/upgrading-airbyte.md)
* **Is the connector that is failing updated to the latest version?** You can check the latest version available for the connectors [in the yamls here](https://github.com/airbytehq/airbyte/tree/master/airbyte-config/init/src/main/resources/seed). If you don't have the latest connector version, make sure you first update to the latest Airbyte version, and then go to the Admin section in the web app and put the right version in the cell for the connector. Then try again. 

If the above workaround does not fix your problem, please report it [here](https://github.com/airbytehq/airbyte/issues/1462) or in our [Slack](https://slack.airbyte.io).

## Your incremental connection is not working

Our current version of incremental is [append](../architecture/incremental-append.md). It works from a cursor field. So you need to check which cursor field you're using and if it's well populated in every record in your table.

If this is true, then, there are still several things to check:

* **Is Airbyte updated to your latest version?** You can see the latest version [here](https://github.com/airbytehq/airbyte/tags). If not, please upgrade to the latest one, [upgrading instructions are here](../tutorials/upgrading-airbyte.md)
* **Is the connector that is failing updated to the latest version?** You can check the latest version available for the connectors [in the yamls here](https://github.com/airbytehq/airbyte/tree/master/airbyte-config/init/src/main/resources/seed). If you don't have the latest connector version, make sure you first update to the latest Airbyte version, and then go to the Admin section in the web app and put the right version in the cell for the connector. Then try again. 

If the above workaround does not fix your problem, please report it [here](https://github.com/airbytehq/airbyte/issues/1462) or in our [Slack](https://slack.airbyte.io).

## **Airbyte says successful sync, but some records are missing**

Several things to check:

* What is the name of the table you are looking at in the destination? Let's make sure you're not looking at a temporary table. 
* **Is the basic normalization toggle set to true at the connection settings?** If it's false, you won't see columns but most probably a JSON file. So you need to switch it on true, and try again. 
* **Is Airbyte updated to your latest version?** You can see the latest version [here](https://github.com/airbytehq/airbyte/tags). If not, please upgrade to the latest one, [upgrading instructions are here](../tutorials/upgrading-airbyte.md)
* **Is the connector that is failing updated to the latest version?** You can check the latest version available for the connectors [in the yamls here](https://github.com/airbytehq/airbyte/tree/master/airbyte-config/init/src/main/resources/seed). If you don't have the latest connector version, make sure you first update to the latest Airbyte version, and then go to the Admin section in the web app and put the right version in the cell for the connector. Then try again. 

If the above workaround does not fix your problem, please report it [here](https://github.com/airbytehq/airbyte/issues/1462) or in our [Slack](https://slack.airbyte.io).

## **Connection refused errors when connecting to a local db**

Depending on your Docker network configuration, you may not be able to connect to `localhost` or `127.0.0.1` directly.

If you are running into connection refused errors when running Airbyte via Docker Compose on Mac, try using `host.docker.internal` as the host. On Linux, you may have to modify `docker-compose.yml` and add a host that maps to your local machine using [`extra_hosts`](https://docs.docker.com/compose/compose-file/compose-file-v3/#extra_hosts).

