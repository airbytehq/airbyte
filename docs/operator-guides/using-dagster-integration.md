---
description: Start triggering Airbyte jobs with Dagster in minutes
---

# Using the Dagster Integration 

Airbyte is an official integration in the Dagster project. The Airbyte Integration allows you to trigger synchronization jobs in Airbyte, and this tutorial will walk through configuring your Dagster Ops to do so.

The Airbyte Task documentation on the Dagster project can be found [here](https://docs.dagster.io/_apidocs/libraries/dagster-airbyte). We also have a tutorial on [dynamically configuring Airbyte using `dagster-airbyte`](https://airbyte.com/tutorials/configure-airbyte-with-python-dagster).

## 1. Set up the tools

First, make sure you have Docker installed. We'll be using the `docker-compose` command, so your install should contain `docker-compose`.

### Start Airbyte

If this is your first time using Airbyte, we suggest going through our [Basic Tutorial](https://github.com/airbytehq/airbyte/tree/e378d40236b6a34e1c1cb481c8952735ec687d88/docs/quickstart/getting-started.md). This tutorial will use the Connection set up in the basic tutorial.

For the purposes of this tutorial, set your Connection's **sync frequency** to **manual**. Dagster will be responsible for manually triggering the Airbyte job.

### Install Dagster

If you don't have a Dagster installed, we recommend following this [guide](https://docs.dagster.io/getting-started) to set one up.

## 2. Create the Dagster Op to trigger your Airbyte job

### Creating a simple Dagster DAG to run an Airbyte Sync Job

Create a new folder called `airbyte_dagster` and create a file `airbyte_dagster.py`.

```python
from dagster import job
from dagster_airbyte import airbyte_resource, airbyte_sync_op

my_airbyte_resource = airbyte_resource.configured(
    {
        "host": {"env": "AIRBYTE_HOST"},
        "port": {"env": "AIRBYTE_PORT"},
    }
)
sync_foobar = airbyte_sync_op.configured({"connection_id": "your-connection-uuid"}, name="sync_foobar")

@job(resource_defs={"airbyte": my_airbyte_resource})
def my_simple_airbyte_job():
    sync_foobar()

```

The Airbyte Dagster Resource accepts the following parameters:

* `host`: The host URL to your Airbyte instance.
* `port`: The port value you have selected for your Airbyte instance.
* `use_https`: If your server use secure HTTP connection.
* `request_max_retries`: The maximum number of times requests to the Airbyte API should be retried before failing.
* `request_retry_delay`: Time in seconds to wait between each request retry.

The Airbyte Dagster Op accepts the following parameters:
* `connection_id`: The Connection UUID you want to trigger
* `poll_interval`: The time in seconds that will be waited between successive polls.
* `poll_timeout`: he maximum time that will waited before this operation is timed out.

After running the file, `dagster job execute -f airbyte_dagster.py ` this will trigger the job with Dagster.

## That's it!

Don't be fooled by our simple example of only one Dagster Flow. Airbyte is a powerful data integration platform supporting many sources and destinations. The Airbyte Dagster Integration means Airbyte can now be easily used with the Dagster ecosystem - give it a shot!

We love to hear any questions or feedback on our [Slack](https://slack.airbyte.io/). We're still in alpha, so if you see any rough edges or want to request a connector, feel free to create an issue on our [Github](https://github.com/airbytehq/airbyte) or thumbs up an existing issue.

