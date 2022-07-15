# Workers & Jobs

In Airbyte, all interactions with connectors are run as jobs performed by a Worker. Examples of workers are:

* Spec worker: retrieves the specification of a connector \(the inputs needed to run this connector\)
* Check connection worker: verifies that the inputs to a connector are valid and can be used to run a sync
* Discovery worker: retrieves the schema of the source underlying a connector
* Sync worker, used to sync data between a source and destination

## Worker Responsibilities

The worker has 4 main responsibilities in its lifecycle. 

1. Spin up any connector docker containers that are needed for the job. 
2. They facilitate message passing to or from a connector docker container \(more on this [below](jobs.md#message-passing)\). 
3. Shut down any connector docker containers that it started. 
4. Return the output of the job. \(See [Airbyte Specification](airbyte-protocol.md) to understand the output of each worker type.\)

## Message Passing

There are 2 flavors of workers: 

1. There are workers that interact with a single connector \(e.g. spec, check, discover\) 
2. There are workers that interact with 2 connectors \(e.g. sync, reset\)

In the first case, the worker is generally extracting data from the connector and reporting it back to the scheduler. It does this by listening to STDOUT of the connector. In the second case, the worker is facilitating passing data \(via record messages\) from the source to the destination. It does this by listening on STDOUT of the source and writing to STDIN on the destination.

For more information on the schema of the messages that are passed, refer to [Airbyte Specification](airbyte-protocol.md).

## Worker Lifecycle

This section will depict the lifecycle of a worker. It will only show the 2 connector version. The single connector version is the same with one side removed.

Note: When a source has passed all of its messages, the docker process should automatically exit. After a destination has received all records, it should automatically shutdown. The worker gives each a grace period to shutdown on their own. If that grace period expires, then the worker will force shutdown.

![Worker Lifecycle](../.gitbook/assets/worker-lifecycle.png)

[Image Source](https://docs.google.com/drawings/d/1k4v_m2M5o2UUoNlYM7mwtZicRkQgoGLgb3eTOVH8QFo/edit)

See the [architecture overview](high-level-view.md) for more information about workers.

## Worker parallelization
Airbyte exposes the following environment variable to change the maximum number of each type of worker allowed to run in parallel. 
Tweaking these values might help you run more jobs in parallel and increase the workload of your Airbyte instance: 
* `MAX_SPEC_WORKERS`: Maximum number of *Spec* workers allowed to run in parallel.
* `MAX_CHECK_WORKERS`: Maximum number of *Check connection* workers allowed to run in parallel.
* `MAX_DISCOVERY_WORKERS`: Maximum number of *Discovery* workers allowed to run in parallel.
* `MAX_SYNC_WORKERS`: Maximum number of *Sync* workers allowed to run in parallel.

The current default value for these environment variables is currently set to **5**.

## Job State Machine

Jobs in the worker follow the following state machine.

![Job state machine](../.gitbook/assets/job-state-machine.png)

[Image Source](https://docs.google.com/drawings/d/1cp8LRZs6UnhAt3jbQ4h40nstcNB0OBOnNRdMFwOJL8I/edit)

