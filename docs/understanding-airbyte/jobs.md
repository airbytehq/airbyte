# Workers & Jobs

In Airbyte, all interactions with connectors are run as jobs performed by a Worker. Each job has a corresponding worker:

* Spec worker: retrieves the specification of a connector \(the inputs needed to run this connector\)
* Check connection worker: verifies that the inputs to a connector are valid and can be used to run a sync
* Discovery worker: retrieves the schema of the source underlying a connector
* Sync worker, used to sync data between a source and destination

There are 4 types of workers in general.

## Worker Responsibilities

The worker has the following responsibilities.

1. Handle the process lifecycle for job-related processes. This includes starting, monitoring and shutting down processes.
2. Facilitate message passing to or from various processes, if required. \(more on this [below](jobs.md#worker-types)\).
3. Handle job-relation operational work such as:
   1. Basic schema validation.
   2. Returning job output, including any error messages. \(See [Airbyte Specification](airbyte-protocol.md) to understand the output of each worker type.\)
   3. Telemetry work e.g. tracking the number and size of records within a sync.

Conceptually, **the worker contains the complexity of all non-connector job operations**. This lets each connector be as simple as possible.

### Worker Types

There are 2 flavors of workers: 

1. **Synchronous Job Worker** - Workers that interact with a single connector \(e.g. spec, check, discover\).

   The worker extracts data from the connector and reports it to the scheduler.  It does this by listening to the connector's STDOUT.
   These jobs are synchronous as they are part of the configuration process and need to be immediately run to provide a good user experience. These are also all lightweight operations.

2. **Asynchronous Job Worker** - Workers that interact with 2 connectors \(e.g. sync, reset\)

   The worker passes data \(via record messages\) from the source to the destination. It does this by listening on STDOUT of the source and writing to STDIN on the destination.
   These jobs are asynchronous as they often are long-running resource-intensive processes. They are decoupled from the rest of the platform to simplify development and operation.

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
