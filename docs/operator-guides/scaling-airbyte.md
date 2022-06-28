# Scaling Airbyte

As depicted in our [High-Level View](../understanding-airbyte/high-level-view.md), Airbyte is made up of several components under the hood: 1. Scheduler 2. Server 3. Temporal 4. Webapp 5. Database

These components perform control plane operations that are low-scale, low-resource work. In addition to the work being low cost, these components are efficient and optimized for these jobs, meaning that only uncommonly large workloads will require deployments at scale. In general, you would only encounter scaling issues when running over a thousand connections.

As a reference point, the typical Airbyte user has 5 - 20 connectors and 10 - 100 connections configured. Almost all of these connections are scheduled, either hourly or daily, resulting in at most 100 concurrent jobs.

## What To Scale

[Workers](../understanding-airbyte/jobs.md) do all the heavy lifting within Airbyte. A worker is responsible for executing Airbyte operations \(e.g. Discover, Read, Sync etc\), and is created on demand whenever these operations are requested. Thus, every job has a corresponding worker executing its work.

How a worker executes work depends on the Airbyte deployment. In the Docker deployment, an Airbyte worker spins up at least one Docker container. In the Kubernetes deployment, an Airbyte worker will create at least one Kubernetes pod. The created resource \(Docker container or Kubernetes pod\) does all the actual work.

Thus, scaling Airbyte is a matter of ensuring that the Docker container or Kubernetes Pod running the jobs has sufficient resources to execute its work.

Jobs-wise, we are mainly concerned with Sync jobs when thinking about scale. Sync jobs sync data from sources to destinations and are the majority of jobs run. Sync jobs use two workers. One worker reads from the source; the other worker writes to the destination.

**In general, we recommend starting out with a mid-sized cloud instance \(e.g. 4 or 8 cores\) and gradually tuning instance size to your workload.**

There are two resources to be aware of when thinking of scale: 1. Memory 2. Disk space

### Memory

As mentioned above, we are mainly concerned with scaling Sync jobs. Within a Sync job, the main memory culprit is the Source worker.

This is because the Source worker reads up to 10,000 records in memory. This can present problems for database sources with tables that have large row sizes. e.g. a table with an average row size of 0.5MBs will require 0.5 \* 10000 / 1000 = 5GBs of RAM. See [this issue](https://github.com/airbytehq/airbyte/issues/3439) for more information.

Our Java connectors currently follow Java's default behaviour with container memory and will only use up to 1/4 of the host's allocated memory. e.g. On a Docker agent with 8GBs of RAM configured, a Java connector limits itself to 2Gbs of RAM and will see Out-of-Memory exceptions if this goes higher. The same applies to Kubernetes pods.
You may want to customize this by setting `JOB_MAIN_CONTAINER_MEMORY_REQUEST` and `JOB_MAIN_CONTAINER_MEMORY_LIMIT` environment variables to custom values.

Note that all Source database connectors are Java connectors. This means that users currently need to over-specify memory resource for Java connectors.


### Disk Space

Airbyte uses backpressure to try to read the minimal amount of logs required. In the past, disk space was a large concern, but we've since deprecated the expensive on-disk queue approach.

However, disk space might become an issue for the following reasons:

1. Long-running syncs can produce a fair amount of logs from the Docker agent and Airbyte on Docker deployments. Some work has been done to minimize accidental logging, so this should no longer be an acute problem, but is still an open issue.
2. Although Airbyte connector images aren't massive, they aren't exactly small either. The typical connector image is ~300MB. An Airbyte deployment with multiple connectors can easily use up to 10GBs of disk space.

Because of this, we recommend allocating a minimum of 30GBs of disk space per node. Since storage is on the cheaper side, we'd recommend you be safe than sorry, so err on the side of over-provisioning.

### On Kubernetes

Users running Airbyte Kubernetes also have to make sure the Kubernetes cluster can accommodate the number of pods Airbyte creates.

To be safe, make sure the Kubernetes cluster can schedule up to `2 x <number-of-possible-concurrent-connections>` pods at once. This is the worse case estimate, and most users should be fine with `2 x <number-of-possible-concurrent-connections>` as a rule of thumb.

This is a **non-issue** for users running Airbyte Docker.

### Temporal DB

Temporal maintains multiple idle connections. By the default value is `20` and you may want to lower or increase this number. One issue we noticed is
that temporal creates multiple pools and the number specified in the `SQL_MAX_IDLE_CONNS` environment variable of the `docker.compose.yaml` file
might end up allowing 4-5 times more connections than expected.

If you want to increase the amount of allowed idle connexion, you will also need to increase `SQL_MAX_CONNS` as well because `SQL_MAX_IDLE_CONNS`
is capped by `SQL_MAX_CONNS`.

## Feedback

The advice here is best-effort and by no means comprehensive. Please reach out on Slack if anything doesn't make sense or if something can be improved.

If you've been running Airbyte in production and have more tips up your sleeve, we welcome contributions!

## Recommended Metrics
Airbyte supports exporting built-in metrics to Datadog or [OpenTelemetry](https://docs.airbyte.com/operator-guides/collecting-metrics/)

### Key Metrics 

<table>
  <tr>
   <td><strong>Key Metrics</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td>oldest_pending_job_age_secs
   </td>
   <td>Shows how long a pending job waits before it is scheduled. If a job is in pending state for a long time, more workers may be required.
   </td>
  </tr>
  <tr>
   <td>oldest_running_job_age_secs
   </td>
   <td>Shows how long the oldest job has been running. A running job that is too large can indicate stuck jobs. This is relative to each job’s runtime. 
   </td>
  </tr>
  <tr>
   <td>job_failed_by_release_stage
   </td>
   <td>Shows jobs that have failed in that release stage and is tagged as alpha, beta, or GA.
   </td>
  </tr>
</table>
      
        :::note

        Metrics with `by_release_stage` in their name are tagged by connector release stage (alpha, beta, or GA). These tags allow you to filter by release stage. Alpha and beta connectors are less stable and have a higher failure rate than GA connectors, so filtering by those release stages can help you find failed jobs.  
        
        :::

:::code

**Example**

If a job was created for an Alpha source to a Beta destination, and the outcome of the job is a success, the following metrics are displayed:

`job_created_by_release_stage\[“alpha”\] = 1;`  
`job_created_by_release_stage\[“beta”\] = 1;`  
`job_failed_by_release_stage\[“alpha”\] = 1;`  
`job_succeeded_by_release_stage\[“beta”\] = 1;`  

**Note:** Each job has a source and destination, so each metric is counted twice — once for source and once for destination.

:::

<table>
  <tr>
   <td><strong>Additional Recommended Metrics</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td>num_running_jobs & num_pending_jobs
   </td>
   <td>Shows how many jobs are currently running and how many jobs are in pending state. These help you understand the general system state.
   </td>
  </tr>
  <tr>
   <td>job_succeeded_by_release_stage
   </td>
   <td>Shows successful jobs in that release stage and is tagged as alpha, beta, or GA.
   </td>
  </tr>
  <tr>
   <td>job_created_by_release_stage
   </td>
   <td>Shows the jobs created in that release stage and is tagged as alpha, beta, or GA.
   </td>
  </tr>
</table>
