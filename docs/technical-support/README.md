---
description: 'Technical support'
---

# Technical Support Page

## Common issues and their workarounds

#### Airbyte is stuck while loading required configuration parameters for my connector
Example of the issue: 

![](../.gitbook/assets/faq_stuck_onboarding.png)

To load configuration parameters, Airbyte must first `docker pull` the connector's image, which may be many hundreds of megabytes. 
Under poor connectivity conditions, the request to pull the image may take a very long time or time out. More context on this issue can be found 
[here](https://github.com/airbytehq/airbyte/issues/1462).  If your internet speed is less than 30mbps down or are running bandwidth-consuming workloads concurrently with Airbyte, you may encounter this issue. [Run a speed test](https://www.speedtest.net/) to verify your internet speed.

One workaround is to manually pull the latest version of every connector you'll use then resetting Airbyte. Note that this will remove any configured connections, sources, or destinations you currently have in Airbyte. To do this:
1. Decide which connectors you'd like to use. For this example let's say you want the Postgres source and the Snowflake destination. 
2. Find the Docker image name of those connectors. Look [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/init/src/main/resources/seed/source_definitions.yaml) for sources and [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-config/init/src/main/resources/seed/destination_definitions.yaml) for destinations. For each of the connectors you'd like to use, copy the value of the `dockerRepository` and `dockerImageTag` fields. For example, for the Postgres source this would be `airbyte/source-postgres` and e.g `0.1.6`.  
3. For **each of the connectors** you'd like to use, from your shell run `docker pull <repository>:<tag>`, replacing `<repository>` and `<tag>` with the values copied from the step above e.g: `docker pull airbyte/source-postgres:0.1.6`. 
4. Once you've finished downloading all the images, from the Airbyte repository root run `docker-compose down -v` followed by `docker-compose up`. 
5. The issue should be resolved.

If the above workaround does not fix your problem, please report it [here](https://github.com/airbytehq/airbyte/issues/1462) or in our [Slack](https://slack.airbyte.io).



