---
products: oss-*
---

# Configuring Connector Resources

There are four different types of jobs—SYNC, CHECK, DISCOVER and SPEC.

Although it is possible to configure resources for all four jobs, we focus on Sync jobs as it is the most frequently run job.

There are three different ways to configure connector resource requirements for a Sync:

1. Instance-wide - applies to all containers in a Sync.
2. Connector-specific - applies to all containers of that connector type in a Sync.
3. Connection-specific - applies to all containers of that connection in a Sync.

In general, **the narrower scope the requirement, the higher the precedence**.

In decreasing order of precedence:

1. Connection-specific - Highest precedence. Overrides all other configuration. We recommend using this on a case-by-case basis.
2. Connector-specific - Second-highest precedence. Overrides instance-wide configuration. Mostly for internal Airbyte-use. We recommend staying away from this.
3. Instance-wide - Lowest precedence. Overridden by all other configuration. Intended to be a default. We recommend setting this as a baseline.

## Configuring Instance-Wide Requirements

Instance-wide requirements are the simplest requirement to configure. All that is needed is to set the following env vars:

1. `JOB_MAIN_CONTAINER_CPU_REQUEST` - Define the job container's minimum CPU usage. Units follow either Docker or Kubernetes, depending on the deployment. Defaults to none.
2. `JOB_MAIN_CONTAINER_CPU_LIMIT` - Define the job container's maximum CPU usage. Units follow either Docker or Kubernetes, depending on the deployment. Defaults to none.
3. `JOB_MAIN_CONTAINER_MEMORY_REQUEST` - Define the job container's minimum RAM usage. Units follow either Docker or Kubernetes, depending on the deployment. Defaults to none.
4. `JOB_MAIN_CONTAINER_MEMORY_LIMIT` - Define the job container's maximum RAM usage. Units follow either Docker or Kubernetes, depending on the deployment. Defaults to none.

## Configuring Connector-Specific Requirements

1. Connect to the database and run the following query with the image name replaced to find the connector definition id.

```sql
select * from actor_definition where actor_definition.docker_repository like '%<image-name>';
```

2. Run the following commend with the resource requirements and the connection definition id filled in.

```sql
update actor_definition set resource_requirements = '{"jobSpecific": [{"jobType": "sync", "resourceRequirements": {"cpu_limit": "0.5", "cpu_request": "0.5", "memory_limit": "500Mi", "memory_request": "500Mi"}}]}' where id = '<id-from-step-1>';
```

## Configuring Connection-Specific Requirements

1. Navigate to the connection in the Airbyte UI and extract the connection id from the url.
   1. The url format is `<base_url>/workspaces/<workspace-id>/connections/<connection-id>/status`.
      If the url is `localhost:8000/workspaces/92ad8c0e-d204-4bb4-9c9e-30fe25614eee/connections/5432b428-b04a-4562-a12b-21c7b9e8b63a/status`,
      the connection id is `5432b428-b04a-4562-a12b-21c7b9e8b63a`.
2. Connect to the database and run the following command with the connection id and resource requirements filled in.

```sql
// SQL command with example
update connection set resource_requirements = '{"cpu_limit": "0.5", "cpu_request": "0.5", "memory_limit": "500Mi", "memory_request": "500Mi"}' where id = '<id-from-step-1>';
```

## Debugging Connection Resources

Airbyte logs the resource requirements as part of the job logs as containers are created. Both source and destination containers are logged.

If a job is running out-of-memory, simply navigate to the Job in the UI, and look for the log to confirm the right configuration is being detected.

On Kubernetes, the log will look something like this:

```
2024-10-28 23:58:10 platform > Launching replication pod: replication-job-20154943-attempt-0 with containers:
2024-10-28 23:58:10 platform > [source] image: airbyte/source-sftp:1.2.0-dev.54744ff04b resources: ResourceRequirements(claims=[], limits={memory=2Gi, ephemeral-storage=5G, cpu=1}, requests={memory=1Gi, ephemeral-storage=5G, cpu=0.5}, additionalProperties={})
2024-10-28 23:58:10 platform > [destination] image: airbyte/destination-s3:1.4.0-dev.6b9d2e4595 resources: ResourceRequirements(claims=[], limits={memory=2Gi, cpu=1}, requests={memory=2Gi, cpu=0.5}, additionalProperties={})
2024-10-28 23:58:10 platform > [orchestrator] image: airbyte/container-orchestrator:build-256f73c6c2-20488-master resources: ResourceRequirements(claims=[], limits={memory=2Gi, cpu=1}, requests={memory=2Gi, cpu=1}, additionalProperties={})
```
