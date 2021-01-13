# Workers & Jobs

In Airbyte, all interactions with connectors are run as jobs performed by a Worker. Examples of workers are:

* Spec worker: retrieves the specification of a connector \(the inputs needed to run this connector\)
* Check connection worker: verifies that the inputs to a connector are valid and can be used to run a sync
* Discovery worker: retrieves the schema of the source underlying a connector
* Sync worker, used to sync data between a source and destination

See the [architecture overview](high-level-view.md) for more information about workers.

## Job State Machine

Jobs in the worker follow the following state machine.

![Job state machine](../.gitbook/assets/job-state-machine.png)

[Image Source](https://docs.google.com/drawings/d/1oMahOg1T8cssxiimV8u4lChbQP5D-wVrSjdMSgxdjiQ/edit)

