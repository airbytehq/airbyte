---
products: oss-*
---

# Configuring Connector Resources

There are four types of jobs in Airbyte.

- Sync
- Check
- Discover
- Spec

It is possible to configure resources for all four jobs, but this article focuses on Sync jobs as it's the most frequently run job and typically the one you want to configure.

There are three ways to configure connector resource requirements for a sync. The narrower in scope the configuration, the higher the precedence.

| Configuration type   | Description                                                               | Precedence | Overrides                           | Overridden by       |
| -------------------- | ------------------------------------------------------------------------- | ---------- | ----------------------------------- | ------------------- |
| Instance-wide        | Applies to all containers.                                                | Lowest     | Nothing                             | All others          |
| Connector definition | Applies to all connectors of that type (for example, all Stripe sources). | Middle     | Instance-wide                       | Connection-specific |
| Connection-specific  | Applies to one source and destination combination.                        | Highest    | Instance-wide, connector definition | Nothing             |

## Best Practices for Allocating Resources

Follow these best practices to minimize resource issues.

### Configuration Hierarchy

Start with the lowest-precedence configuration that's appropriate, then override that with more specific configurations as needed.

- Set instance-wide configurations if Airbyte's default is unsuitable for you
- Use connector definition configurations when possible
- Apply connection-specific configurations for exceptional cases

We recommend that you start with the default resource allocations set by Airbyte. These should be sufficient for most use cases.

If you suspect insufficient resources, confirm the issue in Airbyte's [logs](#debugging). If the logs indicate a CPU or memory issue, increase allocations only for affected connector definitions. Apply connection-specific overrides as a last resort.

## Configuring Instance-Wide Requirements

Instance-wide requirements affect all job containers that you don't override some other way. Set the following variables in your `values.yaml` file.

1. `JOB_MAIN_CONTAINER_CPU_REQUEST` - Define the job container's minimum CPU usage. Defaults to none.
2. `JOB_MAIN_CONTAINER_CPU_LIMIT` - Define the job container's maximum CPU usage. Defaults to none.
3. `JOB_MAIN_CONTAINER_MEMORY_REQUEST` - Define the job container's minimum RAM usage. Defaults to none.
4. `JOB_MAIN_CONTAINER_MEMORY_LIMIT` - Define the job container's maximum RAM usage. Defaults to none.

## Configuring Connector Definition Requirements

You can use SQL to configure connector definitions, affecting all connectors of that type.

1. Connect to the database and run the following query with the image name replaced to find the connector definition ID.

   ```sql
   select * from actor_definition where actor_definition.docker_repository like '%<image-name>';
   ```

2. Run the following command with the resource requirements and the connector definition ID filled in.

   ```sql
   update actor_definition set resource_requirements = '{"jobSpecific": [{"jobType": "sync", "resourceRequirements": {"cpu_limit": "2", "cpu_request": "2", "memory_limit": "2048Mi", "memory_request": "2048Mi"}}]}' where id = '<id-from-step-1>';
   ```

## Configuring Connection-Specific Requirements

1. Navigate to the connection in the Airbyte UI and extract the connection ID from the URL.

   - The URL format is `<base_url>/workspaces/<workspace-id>/connections/<connection-id>/status`. If the URL is `localhost:8000/workspaces/92ad8c0e-d204-4bb4-9c9e-30fe25614eee/connections/5432b428-b04a-4562-a12b-21c7b9e8b63a/status`, the connection ID is `5432b428-b04a-4562-a12b-21c7b9e8b63a`.

2. Connect to the database and run the following command with the connection ID and resource requirements filled in.

```sql
update connection set resource_requirements = '{"cpu_limit": "2", "cpu_request": "2", "memory_limit": "2048Mi", "memory_request": "2048Mi"}' where id = '<id-from-step-1>';
```

## Debugging Connection Resources {#debugging}

Airbyte logs the resource requirements as part of the job logs as containers are created. Both source and destination containers are logged.

If a job is running out-of-memory, simply navigate to the Job in the UI, and look for the log to confirm the right configuration is being detected. The log will look something like this:

```text
2024-10-28 23:58:10 platform > Launching replication pod: replication-job-20154943-attempt-0 with containers:
2024-10-28 23:58:10 platform > [source] image: airbyte/source-sftp:1.2.0-dev.54744ff04b resources: ResourceRequirements(claims=[], limits={memory=2Gi, ephemeral-storage=5G, cpu=1}, requests={memory=1Gi, ephemeral-storage=5G, cpu=0.5}, additionalProperties={})
2024-10-28 23:58:10 platform > [destination] image: airbyte/destination-s3:1.4.0-dev.6b9d2e4595 resources: ResourceRequirements(claims=[], limits={memory=2Gi, cpu=1}, requests={memory=2Gi, cpu=0.5}, additionalProperties={})
2024-10-28 23:58:10 platform > [orchestrator] image: airbyte/container-orchestrator:build-256f73c6c2-20488-master resources: ResourceRequirements(claims=[], limits={memory=2Gi, cpu=1}, requests={memory=2Gi, cpu=1}, additionalProperties={})
```
