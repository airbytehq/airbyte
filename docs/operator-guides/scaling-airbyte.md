## Scaling Airbyte

As depicted in our [High-Level View](../understanding-airbyte/high-level-view.md), Airbyte is made up of several components under the hood:
1) Scheduler
2) Server
3) Temporal
4) Webapp
5) Database

These components perform control plane operations which are low-scale low-resource work. On top of that, these components are also decently efficient.
Unless your workload involves uncommonly large - more than a thousand - numbers of Airbyte resources (e.g. a connection of a source etc.) these components
should not present any scaling issues.

As a reference point, the typical Airbyte user has 5 - 20 connectors and 10 - 100 connections configured. Almost all of these connections are scheduled,
either hourly or daily, resulting in at most 100 concurrent jobs.

### What To Scale
[Workers](../understanding-airbyte/jobs.md) do all the heavy lifting within Airbyte. A worker is responsible for executing an Airbyte operations (e.g. Discover, Read, Sync etc),
and is created on demand whenever these operations are requested. Thus, every job has a corresponding worker executing its work.

How a worker executes work depends on the Airbyte deployment. In the Docker deployment, an Airbyte worker spins up at least one docker container. In the Kubernetes
deployment, an Airbyte worker create at laest one Kubernetes pod. The created resource - Docker container or Kubernetes pod - does all the actual work.

Thus, scaling Airbyte is a matter of ensuring the Docker container/Kubernetes pod have sufficient resources to execute its work.

There are two resources to be aware of:
1) Memory
2) Disk space

##### Memory

#### Disk Space
Airbyte used to use an on-disk queue resulting in significant disk space usage, especially for long-running syncs. Today Airbyte uses backpressure to try
and read the minimal amount of logs required. Disk space is no longer a large concern as it was before.

However disk space might be an issue for the following reasons:

1) Long-running syncs can produce a fair amount of logs from the Docker agent and Airbyte on Docker deployments. Some work has been done to minimise
   accidental logging so this should no longer be an acute problem. However, this is not guaranteed
   
2) Although Airyte connector images aren't massive, they aren't exactly small either. The typical connector image is ~300MB. An Airbyte deployment with
multiple connectors can easily use up to 10GBs of disk space.

Because of this, we recommend allocating a minimum of 30GBs of disk space per node. Since storage is on the cheaper side, we'd recommend you being safe rather than sorry, so err on the side of overprovisioning.
